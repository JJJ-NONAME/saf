# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import Generator
from importlib.metadata import entry_points
from pathlib import Path
import sys
from typing import Any

import click
from packaging.specifiers import SpecifierSet
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator
import tomlkit


class SafTemplateValidationError:
    def __init__(self, template_name: str, error: ValidationError):
        self.template_name = template_name
        self.error = error


class SafTemplate(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    description: str = Field(min_length=1)
    location: Path
    dependencies: dict[str, Any] = Field(default_factory=dict)
    saf_cli_compatibility_range: SpecifierSet | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Path) -> Path:
        if not v.is_dir():
            raise ValueError(f"Location path '{v}' is not a valid directory")
        return v

    @field_validator("saf_cli_compatibility_range", mode="before")
    @classmethod
    def validate_saf_cli_compatibility_range(cls, value: Any) -> SpecifierSet | None:
        if value is None:
            return None
        try:
            spec_str: str = str(value).strip()
            return SpecifierSet(spec_str)
        except Exception as e:
            raise ValueError(
                f"Invalid saf-cli version compatibility range: '{value}'. "
                f"Make sure you define a range of versions using standard packaging specifier format, "
                f"e.g. '>=0.1.0,<1.0.0' or '==0.2.5'.",
            ) from e


class SafPluginValidationError:
    def __init__(self, module_name: str, error: ValidationError):
        self.module_name = module_name
        self.error = error


class SafPlugin(BaseModel):
    path: Path
    module_name: str = Field(min_length=1)
    templates_config: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def load_templates_config(self) -> "SafPlugin":
        config_path = self.path / "templates.toml"
        if not config_path.is_file():
            raise ValueError(
                f"Config file 'templates.toml' not found for plugin module '{self.module_name}' "
                f"at expected location {config_path}",
            )
        try:
            templates_config = tomlkit.loads(config_path.read_bytes()).unwrap()
        except Exception as e:
            raise ValueError(
                f"Error loading config file 'templates.toml' for plugin module '{self.module_name}' "
                f"at location {config_path}: {e}",
            ) from e
        if not templates_config.get("templates"):
            raise ValueError(
                f"No templates in templates configuration file for plugin module '{self.module_name}'",
            )
        self.templates_config = templates_config
        return self


class ClickRenderer:
    def __init__(self, verbose: bool = False, steps_only: bool = False, solutions_only: bool = False):
        self._verbose = verbose
        self._steps_only = steps_only
        self._solutions_only = solutions_only

    def _render_plugin_information(self, module_name: str) -> None:
        click_str = (
            "Step templates" if self._steps_only else "Solution templates" if self._solutions_only else "Templates"
        )
        click.secho(f"{click_str} in ", fg="cyan", nl=False)
        click.secho(f"{module_name}", fg="cyan", bold=True)

    def _render_template_information(self, saf_template: SafTemplate) -> None:
        click.secho(f"    {saf_template.name} ({saf_template.type}): ", fg="green", nl=False)
        click.secho(f"{saf_template.description}")
        if self._verbose:
            click.secho(f"        location: {saf_template.location}")
            if saf_template.dependencies:
                for group_name in saf_template.dependencies:
                    click.secho(f"        {group_name} dependencies:")
                    for dependency_name, dependency_specification in saf_template.dependencies[group_name].items():
                        click.secho(f"          - {dependency_name}: {dependency_specification}")
        click.echo()

    def render_plugin_and_template_information(self, plugin_templates: dict[str, list[SafTemplate]]) -> None:
        for module_name, templates in plugin_templates.items():
            self._render_plugin_information(module_name)
            for template in templates:
                if self._steps_only and template.type != "step" or self._solutions_only and template.type != "solution":
                    continue
                self._render_template_information(template)

    def render_plugin_errors(self, plugin_errors: list[SafPluginValidationError]) -> None:
        if self._verbose and plugin_errors:
            for error in plugin_errors:
                click.secho(f"Error in plugin module '{error.module_name}':", err=True, fg="red")
                click.secho(f"{error.error}", err=True, fg="red")
                click.echo()
        elif plugin_errors:
            click.secho(
                f"Warning: {len(plugin_errors)} template plugin(s) could not be loaded. "
                f"Use --verbose flag for more details.",
                err=True,
                fg="yellow",
            )

    def render_template_errors(self, template_errors: list[SafTemplateValidationError]) -> None:
        if self._verbose and template_errors:
            for error in template_errors:
                click.secho(f"Error in template '{error.template_name}':", err=True, fg="red")
                click.secho(f"{error.error}", err=True, fg="red")
                click.echo()
        elif template_errors:
            click.secho(
                f"Warning: {len(template_errors)} template(s) could not be loaded. "
                f"Use --verbose flag for more details.",
                err=True,
                fg="yellow",
            )


def _iterate_plugins() -> Generator[SafPlugin | SafPluginValidationError, None, None]:
    plugins = entry_points(group="ansys_saf_templates")
    if not plugins:
        click.secho("No template plugins found.", fg="yellow")
        sys.exit(1)
    for plugin in sorted(plugins, key=lambda p: p.value.split(":")[0]):
        module_name = plugin.value.split(":")[0]
        try:
            yield SafPlugin.model_validate(
                {
                    "path": plugin.load()(),
                    "module_name": module_name,
                },
            )
        except ValidationError as e:
            yield SafPluginValidationError(module_name, e)


def _find_template_in_plugin(template_name: str, plugin: SafPlugin) -> SafTemplate | None:
    if template_name not in plugin.templates_config["templates"]:
        return None
    template = plugin.templates_config["templates"][template_name]
    try:
        return SafTemplate.model_validate(
            {
                "name": template_name,
                "type": template["type"],
                "description": template["description"],
                "location": plugin.path / template["location"],
                "dependencies": template.get("dependencies", {}),
                "saf_cli_compatibility_range": template.get("saf_cli_compatibility_range"),
            },
        )
    except Exception as e:
        raise ValueError(f"Template '{template_name}' in plugin module '{plugin.module_name}' is invalid.") from e


def resolve_template(template_name: str) -> SafTemplate:
    plugin_errors: list[SafPluginValidationError] = []
    for plugin in _iterate_plugins():
        if isinstance(plugin, SafPluginValidationError):
            plugin_errors.append(plugin)
            continue
        if not (saf_template := _find_template_in_plugin(template_name, plugin)):
            continue
        return saf_template

    raise ValueError(
        f"Could not find a valid template for template name '{template_name}'.\n"
        f" - Run `saf templates` to list the available templates.\n"
        f" - Run `saf templates --verbose` to include more details on plugin and template errors.",
    )


def _scan_plugin_templates(plugin: SafPlugin) -> Generator[SafTemplate | SafTemplateValidationError, None, None]:
    for template_name, template in plugin.templates_config["templates"].items():
        try:
            yield SafTemplate.model_validate(
                {
                    "name": template_name,
                    "type": template.get("type", ""),
                    "description": template.get("description"),
                    "location": plugin.path / template.get("location", ""),
                    "dependencies": template.get("dependencies", {}),
                    "saf_cli_compatibility_range": template.get("saf_cli_compatibility_range"),
                },
            )
        except ValidationError as e:
            yield SafTemplateValidationError(template_name, e)


def list_available_templates(steps_only: bool = False, solutions_only: bool = False, verbose: bool = False) -> None:
    renderer = ClickRenderer(verbose, steps_only, solutions_only)
    plugin_templates: dict[str, list[SafTemplate]] = {}
    plugin_errors: list[SafPluginValidationError] = []
    template_errors: list[SafTemplateValidationError] = []
    for plugin in _iterate_plugins():
        if isinstance(plugin, SafPluginValidationError):
            plugin_errors.append(plugin)
            continue
        for saf_template in _scan_plugin_templates(plugin):
            if isinstance(saf_template, SafTemplateValidationError):
                template_errors.append(saf_template)
                continue
            if plugin.module_name not in plugin_templates:
                plugin_templates[plugin.module_name] = []
            plugin_templates[plugin.module_name].append(saf_template)

    renderer.render_plugin_and_template_information(plugin_templates)
    renderer.render_plugin_errors(plugin_errors)
    renderer.render_template_errors(template_errors)
