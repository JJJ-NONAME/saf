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

from dataclasses import dataclass
import importlib
import logging
import os
from pathlib import Path
import sys
import traceback
from types import ModuleType

import click

from ansys.saf.glow._config.const import (
    GLOW_API_HOST,
    GLOW_API_PORT,
    GLOW_API_URL,
    GLOW_CORS_ORIGINS,
    GLOW_DEBUG,
    GLOW_PORTAL_URL,
    GLOW_PRODUCT_INSTANCE_SYSTEM_HOST,
    GLOW_PRODUCT_INSTANCE_SYSTEM_PORT,
    GLOW_SOLUTION_DEFINITION,
    GLOW_UI_HOST,
    GLOW_UI_MODULE,
    GLOW_UI_PORT,
)
from ansys.saf.glow._server.analysis import AnalysisResultModel, perform_analysis
from ansys.saf.glow._server.main import run_api_server
from ansys.saf.glow._ui.main import run_ui_server
from ansys.saf.glow._utilities.solution_modules import (
    get_definition_module,
    get_definition_module_from_solution_param,
    get_ui_module,
    get_ui_module_from_solution_param,
)

# Each CLI command has an associated Python function that serves as the exclusive entry point for any application.
# It can be accessed either through the CLI invocation or through a direct Python call,
# as seen in SAF Desktop using multiprocessing.
# This setup is necessary because invoking Click commands directly as functions can be challenging.
# This approach enables us to configure initial settings for logging and environment variables,
# while keeping the library's exposure
# to external applications limited to this module.


logger = logging.getLogger(__name__)


def _set_env_var_if_not_none(name: str, value: str | None = None):
    if value is not None:
        os.environ[name] = value


@dataclass
class SolutionModule:
    definition_module: ModuleType | None = None
    ui_module: ModuleType | None = None


@click.group()
@click.pass_context
def cli(ctx: click.Context): ...


@cli.command(short_help="Run as solution REST API server.")
@click.option("--host", envvar=GLOW_API_HOST, type=str, help="Bind socket to this host. [default: 127.0.0.1]")
@click.option("--port", envvar=GLOW_API_PORT, type=int, help="Bind socket to this port. [default: 5432]")
@click.option(
    "--pim-host",
    envvar=GLOW_PRODUCT_INSTANCE_SYSTEM_HOST,
    type=str,
    help="The host where the product instance management system (HPS/PIM) is running. [default: 127.0.0.1]",
)
@click.option(
    "--pim-port",
    envvar=GLOW_PRODUCT_INSTANCE_SYSTEM_PORT,
    type=int,
    help="The port where the product instance management system (HPS/PIM) is running.",
)
@click.option(
    "--cors-origin",
    multiple=True,
    help="A list of origins that should be permitted to make cross-origin requests.",
)
@click.option("--definition", type=str, help="The solution definition module.")
@click.option("--solution", type=str, help="The solution module.")
@click.option(
    "--env-file",
    type=click.Path(exists=True, file_okay=True, path_type=Path),
    help="Load environment variables from this file.",
)
@click.pass_context
def api(
    ctx: click.Context,
    host: str | None = None,
    port: int | None = None,
    pim_host: str | None = None,
    pim_port: int | None = None,
    cors_origin: list[str] | None = None,
    definition: str | None = None,
    solution: str | None = None,
    env_file: Path | None = None,
):
    """Run the solution REST API server."""
    try:
        # Fall back to GLOW_SOLUTION_DEFINITION env var when --definition is not provided on the CLI.
        definition = definition or os.environ.get(GLOW_SOLUTION_DEFINITION)
        definition_module = get_definition_module(ctx, definition=definition, solution=solution, validate_module=False)

        run_api(host, port, definition_module, pim_host, pim_port, cors_origin or [], env_file)
    except Exception as e:
        _generic_exception_handler(e)


def _import_definition_module(definition_module: ModuleType | str):
    if isinstance(definition_module, str):
        # Modules can't be pickled, which is mandatory if we want to use this
        # function in multiprocessing calls, as we do in SAF Desktop.
        definition_module = importlib.import_module(definition_module)
    return definition_module


def _format_click_args_to_env_var_list(args: str):
    # List in env var need to have a special formatting: '["a", "b"]'
    # whereas list args given by click are in the following format: "('a', 'b')"
    formatted_args = args.replace(",)", ")")  # Remove pending ',' when there is only one arg "('a',)"
    return formatted_args.replace("(", "[").replace(")", "]").replace("'", '"')


def run_api(
    host: str | None,
    port: int | None,
    definition_module: ModuleType | str,
    pim_host: str | None = None,
    pim_port: int | None = None,
    cors_origins: list[str] | None = None,
    env_file: Path | None = None,
):
    """Run the solution REST API server."""
    definition_module = _import_definition_module(definition_module)
    # We want the order of precedence (highest to lowest) as follows:
    # - CLI parameters
    # - environment variables
    # - .env config
    # so let's assign cli parameters to env var in case they aren't coming already from env var.
    _set_env_var_if_not_none(GLOW_API_HOST, host)
    _set_env_var_if_not_none(GLOW_API_PORT, str(port) if port else None)
    _set_env_var_if_not_none(GLOW_PRODUCT_INSTANCE_SYSTEM_HOST, pim_host)
    _set_env_var_if_not_none(GLOW_PRODUCT_INSTANCE_SYSTEM_PORT, str(pim_port) if pim_port else None)
    # List in env var need special formatting: '["a", "b"]'
    cors_env = _format_click_args_to_env_var_list(str(cors_origins)) if cors_origins else None
    _set_env_var_if_not_none(GLOW_CORS_ORIGINS, cors_env)
    _set_env_var_if_not_none(GLOW_SOLUTION_DEFINITION, definition_module.__name__)
    run_api_server(env_file)


@cli.command(short_help="Run as solution UI server.")
@click.option("--host", envvar=GLOW_UI_HOST, type=str, help="Bind socket to this host. [default: 127.0.0.1]")
@click.option("--port", envvar=GLOW_UI_PORT, type=int, help="Bind socket to this port. [default: 5433]")
@click.option("--api-server-url", envvar=GLOW_API_URL, type=str, help="The url of the solution api server.")
@click.option("--portal-ui-url", envvar=GLOW_PORTAL_URL, type=str, help="The url of the portal.")
@click.option("--solution", type=str, help="The solution module.")
@click.option(
    "--env-file",
    type=click.Path(exists=True, file_okay=True, path_type=Path),
    help="Load environment variables from this file.",
)
@click.pass_context
def ui(
    ctx: click.Context,
    host: str | None,
    port: int | None,
    api_server_url: str | None,
    portal_ui_url: str | None,
    solution: str | None = None,
    env_file: Path | None = None,
):
    """Run the solution Dash UI server."""
    try:
        definition_module = get_definition_module(ctx, solution=solution, validate_module=True)
        ui_module = get_ui_module(ctx, solution=solution)
        if ui_module is None:
            raise RuntimeError("The ui app module cannot be omitted in this configuration or mode")

        run_ui(host, port, definition_module, ui_module, api_server_url, portal_ui_url, env_file)
    except Exception as e:
        _generic_exception_handler(e)


def run_ui(
    host: str | None,
    port: int | None,
    definition_module: ModuleType | str,
    ui_app_module: ModuleType | str,
    api_server_url: str | None,
    portal_ui_url: str | None,
    env_file: Path | None = None,
):
    """Run the solution Dash UI server."""
    if isinstance(definition_module, str):
        # Modules can't be pickled, which is mandatory if we want to use this
        # function in multiprocessing calls, as we do in SAF Desktop.
        definition_module = importlib.import_module(definition_module)
    if isinstance(ui_app_module, str):
        ui_app_module = importlib.import_module(ui_app_module)

    _set_env_var_if_not_none(GLOW_UI_HOST, host)
    _set_env_var_if_not_none(GLOW_UI_PORT, str(port) if port else None)
    _set_env_var_if_not_none(GLOW_PORTAL_URL, portal_ui_url)
    _set_env_var_if_not_none(GLOW_API_URL, api_server_url)
    _set_env_var_if_not_none(GLOW_SOLUTION_DEFINITION, definition_module.__name__)
    _set_env_var_if_not_none(GLOW_UI_MODULE, ui_app_module.__name__)
    run_ui_server(env_file)


@cli.command(short_help="Perform static analysis.")
@click.option("--definition", help="The solution definition module.")
@click.option("--solution", help="The solution module.")
@click.pass_context
def analysis(ctx: click.Context, definition: str | None = None, solution: str | None = None):
    """Perform static analysis of the solution."""
    try:
        definition_module = get_definition_module(ctx, definition=definition, solution=solution, validate_module=True)
        ui_module = get_ui_module(ctx, solution=solution)

        analysis_result = run_analysis(definition_module, ui_module)
        click.echo(analysis_result.model_dump_json())
    except Exception as e:
        _generic_exception_handler(e)


def run_analysis(
    definition_module: ModuleType | None = None,
    ui_app_module: ModuleType | None = None,
    solution_main_module_name: str | None = None,
) -> AnalysisResultModel:
    """Perform static analysis of the solution."""
    # TODO: do we need instrumentor here or a basic logging config at least?
    if definition_module is None:
        if solution_main_module_name is None:
            raise ValueError("Provide either the definition_module or the solution_main_module_name parameters")
        definition_module = get_definition_module_from_solution_param(solution_main_module_name, validate_module=True)
        ui_app_module = get_ui_module_from_solution_param(solution_main_module_name)
    analysis_result = perform_analysis(definition_module, ui_app_module)
    return analysis_result


def _generic_exception_handler(e: Exception):
    if not os.environ.get(GLOW_DEBUG) or os.environ.get(GLOW_DEBUG) == "False":
        error_stack_trace = f"Error: {e}\n{traceback.format_exc()}"
        click.secho(error_stack_trace, err=True, fg="red")
    else:
        click.secho(f"Error: {e}", err=True, fg="red")
    sys.exit(1)
