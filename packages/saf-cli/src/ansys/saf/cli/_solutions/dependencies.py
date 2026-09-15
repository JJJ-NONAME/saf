# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
import subprocess
from typing import Any

import click
from pydantic import BaseModel
import tomlkit
from tomlkit.items import Table

from ansys.saf.cli._solutions.plugins import SafTemplate


class ManualDependency(BaseModel):
    name: str
    specification: str | dict[str, Any]
    group: str


class DependencyManager:
    def __init__(
        self,
        saf_template: SafTemplate,
        solution_root_dir: Path,
    ) -> None:
        self._saf_template = saf_template
        self._solution_root_dir = solution_root_dir
        self._pyproject_path = solution_root_dir / "pyproject.toml"
        if not self._pyproject_path.is_file():
            raise FileNotFoundError(f"pyproject.toml not found in solution root directory '{self._solution_root_dir}'.")

    @staticmethod
    def _create_new_dependency_group() -> Table:
        new_group = tomlkit.table()
        new_group.add("optional", True)
        deps = tomlkit.table()
        new_group.add("dependencies", deps)
        new_group.add(tomlkit.nl())
        return new_group

    def _get_group_str(self, group_name: str) -> str:
        return "main" if group_name == "main" else f"{group_name} group"

    def _get_solution_dependency_groups(self, poetry_section: dict[str, Any]) -> dict[str, Any]:
        if "group" not in poetry_section:  # type: ignore
            if any(step_dep_group != "main" for step_dep_group in self._saf_template.dependencies):
                poetry_section["group"] = tomlkit.table(is_super_table=True)  # type: ignore
            else:
                return {}
        return poetry_section["group"]  # type: ignore

    def _find_dependency_in_solution(
        self,
        dependency_name: str,
        main_dependencies: dict[str, Any],
        dependency_groups: dict[str, Any],
    ) -> bool:
        if dependency_name in main_dependencies:
            return True
        for _, group_dependencies in dependency_groups.items():
            if dependency_name in group_dependencies.get("dependencies", {}):
                return True
        return False

    def _add_dependency_to_solution(
        self,
        step_dependency_name: str,
        step_dependency_spec: str | dict[str, Any],
        solution_dependencies: dict[str, Any],
    ) -> None:
        if isinstance(step_dependency_spec, str):
            # Dependencies in the format dependency_name: "dependency_specification"
            solution_dependencies[step_dependency_name] = step_dependency_spec
        else:
            # Dependencies in the format dependency_name: { "key": "value", ... }
            inline_dependency = tomlkit.inline_table()
            inline_dependency.update(step_dependency_spec)  # pyright: ignore[reportUnknownMemberType]
            inline_dependency.trivia.trail = "\n"
            solution_dependencies[step_dependency_name] = inline_dependency

    def _render_manual_dependency_warning(self, manual_dependencies: list[ManualDependency], groups: set[str]) -> None:
        click.secho(
            f"WARNING: the step template '{self._saf_template.name}' has some dependencies in common with the "
            f"solution's pyproject.toml at {self._pyproject_path}. Review the solution's pyproject.toml and manually "
            f"update it if necessary, to ensure that it is compatible with the step template's dependencies.\n",
            fg="yellow",
        )
        click.secho("Step specification of the common dependencies:", fg="yellow")
        for manual_dependency in manual_dependencies:
            click.secho(
                f"  - {manual_dependency.name} ({self._get_group_str(manual_dependency.group)}): "
                f"{manual_dependency.specification}",
                fg="yellow",
            )
        install_command = "poetry install"
        if groups:
            install_command += f" --with {','.join(sorted(groups))}"
        click.secho(
            f"\nAfter reviewing the dependencies, please run:\n"
            f'  - saf execute {self._solution_root_dir.name} "poetry lock"\n'
            f'  - saf execute {self._solution_root_dir.name} "{install_command}"',
            fg="yellow",
        )

    def update_solution_dependencies(self, executable: Path, solution_env: dict[str, str]) -> None:
        pyproject_content = tomlkit.loads(self._pyproject_path.read_bytes())
        if not pyproject_content.get("tool", {}).get("poetry", {}):  # type: ignore
            raise ValueError(f"No [tool.poetry] section found in pyproject.toml at '{self._pyproject_path}'.")
        poetry_section = pyproject_content["tool"]["poetry"]  # type: ignore
        main_deps = poetry_section.get("dependencies", {})  # type: ignore
        if not main_deps:
            raise ValueError(f"No main dependencies found in pyproject.toml at '{self._pyproject_path}'.")
        dep_groups = self._get_solution_dependency_groups(poetry_section)  # type: ignore

        manual_deps: list[ManualDependency] = []
        for step_dep_group in self._saf_template.dependencies:
            if step_dep_group != "main" and step_dep_group not in dep_groups:
                dep_groups[step_dep_group] = self._create_new_dependency_group()
            group_deps = dep_groups.get(step_dep_group, {}).get("dependencies", {})
            for step_dep_name, step_dep_spec in self._saf_template.dependencies[step_dep_group].items():
                if self._find_dependency_in_solution(step_dep_name, main_deps, dep_groups):  # type: ignore
                    manual_deps.append(
                        ManualDependency(
                            name=step_dep_name,
                            specification=step_dep_spec,
                            group=step_dep_group,
                        ),
                    )
                else:
                    self._add_dependency_to_solution(
                        step_dep_name,
                        step_dep_spec,
                        main_deps if step_dep_group == "main" else group_deps,  # type: ignore
                    )

        self._pyproject_path.write_text(tomlkit.dumps(pyproject_content), newline="")  # type: ignore

        groups = {group for group in self._saf_template.dependencies if group != "main"}
        if not manual_deps:
            cmd = [executable.as_posix(), "lock"]
            subprocess.run(cmd, env=solution_env, cwd=self._solution_root_dir, check=True)

            cmd = [executable.as_posix(), "install"]
            cmd += ["--with", ",".join(sorted(groups))] if groups else []
            subprocess.run(cmd, env=solution_env, cwd=self._solution_root_dir, check=True)
        else:
            self._render_manual_dependency_warning(manual_deps, groups)
