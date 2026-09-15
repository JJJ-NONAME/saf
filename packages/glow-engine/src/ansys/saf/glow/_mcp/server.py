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
from base64 import b64decode, b64encode
from binascii import Error as BinasciiError
from collections.abc import Callable
import inspect
from pathlib import Path
from random import randint
import tempfile
from types import ModuleType
from typing import Annotated, Any, get_type_hints

from ansys.bdm.api import EntityHandle
from fastmcp import FastMCP
from fastmcp.server import Context
from fastmcp.tools import ToolResult
from pydantic import Field

from ansys.saf.glow._core.transaction import categorize_transaction_parameters
from ansys.saf.glow._mcp.solution_doc import SolutionDoc
from ansys.saf.glow._utilities.conversion import python_identifier_to_url_part
from ansys.saf.glow.client import Client, LongRunning
from ansys.saf.glow.solution import MethodStatus, Solution

_SOLUTION_CLASS_ATTR = "_solution_class"
_SOLUTION_API_URL_ATTR = "_solution_api_url"
_SOLUTION_WORKFLOW_ATTR = "_solution_workflow"


def _get_solution_config(ctx: Context) -> tuple[type[Solution], str]:
    app = ctx.fastmcp
    solution_class = getattr(app, _SOLUTION_CLASS_ATTR, None)
    solution_api_url = getattr(app, _SOLUTION_API_URL_ATTR, None)
    if solution_class is None or solution_api_url is None:
        raise RuntimeError("Solution class or API URL not configured.")
    return solution_class, solution_api_url


def _make_tool_func(
    step_name: str,
    transaction_name: str,
    step_type: type[Any],
) -> Callable[..., Any]:
    transaction = getattr(step_type, transaction_name)
    method_type_hints = get_type_hints(transaction)
    transaction_signature = inspect.signature(transaction)
    transaction_body_params, _ = categorize_transaction_parameters(method_type_hints, transaction_signature)
    transaction_param_names = list(transaction_body_params)

    custom_parameters: list[inspect.Parameter] = []
    for param_name in transaction_param_names:
        param = transaction_signature.parameters[param_name]
        param_type = method_type_hints.get(param_name, Any)
        custom_parameters.append(
            param.replace(
                annotation=Annotated[
                    param_type,
                    Field(description=f"Transaction argument '{param_name}'."),
                ],
            ),
        )

    tool_signature = inspect.Signature(
        [
            inspect.Parameter(
                "ctx",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[Context, Field(description="MCP request context.")],
            ),
            inspect.Parameter(
                "project_name",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[str, Field(description="Name of the project containing the transaction.")],
            ),
            *custom_parameters,
        ],
        # type(None) is what it's returned if `-> None` is set as return type in the transaction method.
        return_annotation=(
            method_type_hints.get("return", type(None))
            if transaction_name not in step_type.get_long_running_method_names()
            else type(None)
        ),
    )

    def _run(*args: Any, **kwargs: Any) -> Any:
        bound = tool_signature.bind_partial(*args, **kwargs)
        ctx = bound.arguments["ctx"]
        project_name = bound.arguments["project_name"]
        transaction_kwargs = {
            name: bound.arguments[name] for name in transaction_param_names if name in bound.arguments
        }

        sol_class, sol_api_url = _get_solution_config(ctx)

        with Client(sol_class, sol_api_url) as client:
            project = client.get_project(project_name)
            step = getattr(project.steps, step_name, None)  # type: ignore
            if not step:
                raise ValueError(f"Step '{step_name}' not found.")
            transaction_obj = getattr(step, transaction_name, None)
            if not transaction_obj:
                raise ValueError(f"Transaction '{transaction_name}' not found on step '{step_name}'.")
            return_valued = transaction_obj(**transaction_kwargs)
            if isinstance(return_valued, LongRunning):
                return None
            return return_valued

    _run.__signature__ = tool_signature  # pyright: ignore[reportFunctionMemberAccess]
    # pydantic's TypeAdapter resolves parameter types from __annotations__, not just __signature__.
    _run.__annotations__ = {name: param.annotation for name, param in tool_signature.parameters.items()}
    _run.__annotations__["return"] = tool_signature.return_annotation

    return _run


def _format_field_names(field_names: list[str]) -> str:
    return ", ".join(field_names) if field_names else "none"


def _describe_transaction_args(transaction: Callable[..., Any]) -> str:
    method_type_hints = get_type_hints(transaction)
    transaction_signature = inspect.signature(transaction)
    transaction_body_params, _ = categorize_transaction_parameters(method_type_hints, transaction_signature)
    return _format_field_names(list(transaction_body_params))


def _describe_transaction_return_type(transaction: Callable[..., Any]) -> str:
    return_type = get_type_hints(transaction).get("return", type(None))
    if return_type is type(None):
        return "None"
    return inspect.formatannotation(return_type)


def _make_transaction_description(
    step_name: str,
    step_type: type[Any],
    transaction_name: str,
) -> str:
    transaction = getattr(step_type, transaction_name)
    step_transaction_spec = getattr(transaction, "_transaction", {}).get("self")
    download_fields = getattr(step_transaction_spec, "download", []) if step_transaction_spec else []
    upload_fields = getattr(step_transaction_spec, "upload", []) if step_transaction_spec else []

    details = [
        f"Download step fields: {_format_field_names(download_fields)}.",
        f"Upload step fields: {_format_field_names(upload_fields)}.",
        f"Transaction args: {_describe_transaction_args(transaction)}.",
        f"Return type: {_describe_transaction_return_type(transaction)}.",
    ]

    base_description = inspect.getdoc(transaction) or f"Run transaction '{transaction_name}' on step '{step_name}'."
    suffix = (
        " It continues after the tool call starts it."
        if transaction_name in step_type.get_long_running_method_names()
        else " It completes during the tool call."
    )
    return f"{base_description} {' '.join(details)}{suffix}"


def _register_transaction_tools(app: FastMCP, solution_class: type[Solution]) -> None:
    for step_name, step_type in solution_class.get_steps_fields().items():
        for transaction_name in step_type.get_transaction_method_names():
            tool_name = f"{step_name}__{transaction_name}"

            tool_func = _make_tool_func(step_name, transaction_name, step_type)
            # make every tool function have a unique name and qualname, so they are internally distinguishable.
            tool_func.__name__ = tool_name
            tool_func.__qualname__ = tool_name

            description = _make_transaction_description(step_name, step_type, transaction_name)

            app.tool(name=tool_name, description=description)(tool_func)


def build_app(definition_module: ModuleType, solution_class: type[Solution], solution_api_url: str) -> FastMCP:  # noqa: C901
    doc = SolutionDoc.from_solution_md(definition_module, solution_class)
    app = FastMCP(name=solution_class.model_construct().display_name, instructions=doc.instructions)
    setattr(app, _SOLUTION_CLASS_ATTR, solution_class)
    setattr(app, _SOLUTION_API_URL_ATTR, solution_api_url)
    setattr(app, _SOLUTION_WORKFLOW_ATTR, doc.workflow)

    transaction_tool_names = [
        f"{step_name}__{transaction_name}"
        for step_name, step_type in solution_class.get_steps_fields().items()
        for transaction_name in step_type.get_transaction_method_names()
    ]

    @app.resource("solution://workflow")
    def solution_workflow() -> str:  # pyright: ignore[reportUnusedFunction]
        """Step by step workflow guideline for using the Solution."""
        workflow = getattr(app, _SOLUTION_WORKFLOW_ATTR, None)
        if workflow is None:
            raise RuntimeError("Solution workflow documentation not configured.")
        return workflow

    @app.resource("saf://concepts")
    def saf_concepts() -> str:  # pyright: ignore[reportUnusedFunction]
        """Generic explanation of SAF solution concepts: projects, steps, fields, entity handles, transactions."""
        return """\
        A SAF solution is a guided simulation workflow made of the following building blocks:

        - Project: a persisted instance of the solution. All data, files, and transaction state belong to
        exactly one project. Use the "project" toolset (create_project, list_projects, delete_projects,
        import_project, export_project) to manage projects.
        - Step: a named stage of the workflow (e.g. "geometry", "mesh", "solve"). Each step owns a set of
        fields and the transactions that operate on them. Discover a solution's steps and transactions via
        the "toolsets://definition" and "solution://workflow" resources.
        - Field: a typed piece of data owned by a step (numbers, strings, booleans, custom pydantic models,
        or entity handles). Read and write fields with the get_fields and set_fields tools.
        - Entity handle: a field type that references file content (inputs, results, meshes, images, etc.)
        stored outside the field itself. Read and write their bytes with download_file and upload_file.
        - Transaction: a step method that downloads some fields, does work, and uploads other fields.
        Transactions are the only supported way to mutate step data; run them with the generated
        "<step_name>__<transaction_name>" tools. Each transaction tool's description states which fields it
        downloads, which it uploads, its arguments, and its return type.
        - Long-running transaction: a transaction that keeps running after its tool call returns. Start it
        with its tool as usual, then block on completion with wait_for_longrunning_transaction.

        Typical usage: create or open a project, inspect the workflow, set input fields and upload input
        files, run transactions in the order the workflow describes, then read output fields and download
        output files.
        """

    @app.resource("toolsets://definition")
    def list_tool_sets() -> list[dict[str, str | list[str]]]:  # pyright: ignore[reportUnusedFunction]
        """Available tools for using the Solution."""
        return [
            {
                "name": "project",
                "description": "Tools for managing projects",
                "tools": [
                    "create_project",
                    "list_projects",
                    "delete_projects",
                    "import_project",
                    "export_project",
                ],
            },
            {
                "name": "data",
                "description": "Tools for setting and retrieving fields and files",
                "tools": ["set_fields", "get_fields", "upload_file", "download_file"],
            },
            {
                "name": "transactions",
                "description": "Tools for running transactions",
                "tools": [*sorted(transaction_tool_names), "wait_for_longrunning_transaction"],
            },
        ]

    @app.tool()
    def create_project(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        display_name: Annotated[
            str | None,
            Field(description="Project name displayed to the user. If not set, a name is generated automatically."),
        ] = None,
    ) -> str:
        """Create a solution project."""
        solution_class, solution_api_url = _get_solution_config(ctx)

        if display_name is not None and not display_name.strip():
            raise ValueError("display_name must not be empty or blank.")

        if display_name is None:
            display_name = f"mcp-{str(randint(0, 10000)).zfill(4)}"  # noqa: S311

        with Client(solution_class, solution_api_url) as client:
            project = client.create_project(display_name)

        return project.project_name

    @app.tool()
    def list_projects(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        page_size: Annotated[
            int | None,
            Field(description="Maximum number of projects to return per page. Defaults to 100, capped at 100."),
        ] = None,
        page: Annotated[int | None, Field(description="Page number to return, starting at 1.")] = None,
        order_by: Annotated[
            str | None,
            Field(
                description=(
                    "Comma-separated fields to order by, ascending unless suffixed with ' desc'. "
                    "Supported fields: display_name, description, date_created, date_modified, name. "
                    "For example: 'date_modified desc, name'."
                ),
            ),
        ] = None,
        filter: Annotated[  # noqa: A002
            str | None,
            Field(
                description=(
                    "Filter expression of the form '<field> <operator> <value> [AND ...]'. "
                    "The display_name and description fields only support '=' as a case-insensitive "
                    "contains match. The date_created and date_modified fields support =, !=, <, >, <=, >= "
                    "with ISO 8601 values. For example: 'display_name = Motor AND date_created >= 2024-01-01'."
                ),
            ),
        ] = None,
    ) -> dict[str, Any]:
        """List solution projects with pagination, ordering, and optional filtering.

        Use this to discover existing projects and their resource names before reading,
        exporting, or deleting them.
        """
        solution_class, solution_api_url = _get_solution_config(ctx)

        with Client(solution_class, solution_api_url) as client:
            return client.list_projects(page_size=page_size, page=page, order_by=order_by, filter=filter)

    @app.tool()
    def delete_projects(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        names: Annotated[
            list[str],
            Field(description="Resource names of the projects to delete, each of the form 'projects/<project_id>'."),
        ],
    ) -> dict[str, str]:
        """Delete one or more solution projects and their project directories.

        This is destructive and irreversible. Deletion is attempted for every name, so a
        failure on one project does not prevent the others from being deleted. Returns the
        outcome per project name: 'deleted' on success, or the error message on failure.
        """
        solution_class, solution_api_url = _get_solution_config(ctx)

        outcomes: dict[str, str] = {}
        with Client(solution_class, solution_api_url) as client:
            for name in dict.fromkeys(names):
                try:
                    client.delete_project(name)
                except Exception as ex:
                    outcomes[name] = str(ex)
                else:
                    outcomes[name] = "deleted"
        return outcomes

    @app.tool()
    def import_project(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        content: Annotated[
            str,
            Field(description="Base64-encoded content of the '.safx' project archive to import."),
        ],
        display_name: Annotated[str, Field(description="Project name displayed to the user.")],
    ) -> str:
        """Import a '.safx' project archive as a new solution project.

        The archive is a binary zip, so its content must be base64-encoded. Returns the
        resource name of the imported project.
        """
        solution_class, solution_api_url = _get_solution_config(ctx)

        try:
            archive = b64decode(content, validate=True)
        except BinasciiError as ex:
            raise ValueError(f"Content is not valid base64: {ex}") from None

        with tempfile.TemporaryDirectory() as tmp_dir:
            safx_path = Path(tmp_dir) / "project.safx"
            safx_path.write_bytes(archive)
            with Client(solution_class, solution_api_url) as client:
                project = client.import_project(safx_path, display_name)
                return project.project_name

    @app.tool()
    def export_project(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        project_name: Annotated[str, Field(description="Name of the project to export.")],
    ) -> str:
        """Export a solution project as a '.safx' project archive.

        The archive is a binary zip, so it is returned base64-encoded and must be decoded
        before being written to a file.
        """
        solution_class, solution_api_url = _get_solution_config(ctx)

        with tempfile.TemporaryDirectory() as tmp_dir:
            destination = Path(tmp_dir)
            with Client(solution_class, solution_api_url) as client:
                client.get_project(project_name).export(destination)
            # there should be only one file, so we avoid the extra http request to retrieve the project display name.
            safx_path = next(destination.glob("*.safx"))
            return b64encode(safx_path.read_bytes()).decode()

    @app.tool()
    def set_fields(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        project_name: Annotated[str, Field(description="Name of the project to update.")],
        step_name: Annotated[str, Field(description="Name of the step containing the fields.")],
        fields: Annotated[dict[str, Any], Field(description="Field names mapped to their new values.")],
    ) -> None:
        """Set field values on a solution step."""
        solution_class, solution_api_url = _get_solution_config(ctx)

        with Client(solution_class, solution_api_url) as client:
            project = client.get_project(project_name)
            step = getattr(project.steps, step_name, None)  # type: ignore
            if not step:
                raise ValueError(f"Step '{step_name}' not found.")
            step.set_fields(fields)

    @app.tool()
    def get_fields(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        project_name: Annotated[str, Field(description="Name of the project to read.")],
        step_name: Annotated[str, Field(description="Name of the step containing the fields.")],
        field_names: Annotated[list[str], Field(description="Names of the fields to read.")],
    ) -> dict[str, Any]:
        """Get field values from a solution step."""
        solution_class, solution_api_url = _get_solution_config(ctx)

        with Client(solution_class, solution_api_url) as client:
            project = client.get_project(project_name)
            step = getattr(project.steps, step_name, None)  # type: ignore
            if not step:
                raise ValueError(f"Step '{step_name}' not found.")
            fields = step.get_fields(field_names)
        return fields

    @app.tool()
    def upload_file(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        project_name: Annotated[str, Field(description="Name of the project to update.")],
        step_name: Annotated[str, Field(description="Name of the step containing the entity handle field.")],
        entity_handle_name: Annotated[str, Field(description="Name of the entity handle field to write.")],
        content: Annotated[bytes, Field(description="File content to upload.")],
    ) -> None:
        """Upload file content to an entity handle field."""
        solution_class, solution_api_url = _get_solution_config(ctx)

        with Client(solution_class, solution_api_url) as client:
            project = client.get_project(project_name)
            step = getattr(project.steps, step_name, None)  # type: ignore
            if not step:
                raise ValueError(f"Step '{step_name}' not found.")
            entity_handle_field = getattr(step, entity_handle_name, None)
            if not isinstance(entity_handle_field, EntityHandle):
                raise ValueError(f"Field '{entity_handle_name}' is not an entityhandle field.")
            entity = project.storage_scope.store_stream(content)
            setattr(step, entity_handle_name, entity)

    @app.tool()
    def download_file(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        project_name: Annotated[str, Field(description="Name of the project to read.")],
        step_name: Annotated[str, Field(description="Name of the step containing the entity handle field.")],
        entity_handle_name: Annotated[str, Field(description="Name of the entity handle field to read.")],
    ) -> bytes:
        """Download file content from an entity handle field."""
        solution_class, solution_api_url = _get_solution_config(ctx)

        with Client(solution_class, solution_api_url) as client:
            project = client.get_project(project_name)
            step = getattr(project.steps, step_name, None)  # type: ignore
            if not step:
                raise ValueError(f"Step '{step_name}' not found.")
            entity_handle_field = getattr(step, entity_handle_name, None)
            if not isinstance(entity_handle_field, EntityHandle):
                raise ValueError(f"Field '{entity_handle_name}' is not an entityhandle field.")
            content = project.storage_scope.get_bytes(entity_handle_field)
        return content

    @app.tool()
    def wait_for_longrunning_transaction(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        project_name: Annotated[str, Field(description="Name of the project containing the transaction.")],
        step_name: Annotated[str, Field(description="Name of the step containing the transaction.")],
        transaction_name: Annotated[str, Field(description="Name of the long-running transaction to wait for.")],
        timeout: Annotated[int, Field(description="Maximum time to wait, in seconds.")] = 600,
    ) -> Any | None:
        """Wait for a started long-running transaction to finish."""
        solution_class, solution_api_url = _get_solution_config(ctx)

        with Client(solution_class, solution_api_url) as client:
            project = client.get_project(project_name)
            step = getattr(project.steps, step_name, None)  # type: ignore
            if not step:
                raise ValueError(f"Step '{step_name}' not found.")
            if transaction_name not in step._step_model_type.get_long_running_method_names():
                raise ValueError(
                    f"Transaction '{transaction_name}' on step '{step_name}' is not a long-running transaction.",
                )
            # We manually build the LongRunning object due to a Client limitation.
            # longrunning's wait()/return value cannot be retrieved from a different context where it's launched.
            # For example, another callback or another MCP tool. In the future We would like to have
            # something like `return_value = step.my_transaction_method.wait()`, assuming that somewhere else
            # we have already done `step.my_transaction_method()`.
            method_id = python_identifier_to_url_part(transaction_name)
            method_url = f"{step._url}:{method_id}"
            method = getattr(step._step_model_type, transaction_name)  # already validated to exist above
            return_type = get_type_hints(method).get("return")
            long_running = LongRunning(
                step._step_model_type,
                step._step_name,
                transaction_name,
                method_url,
                client.http_client,
                return_type,
            )
            if long_running.get_state().status == MethodStatus.RunRequired:
                raise RuntimeError(
                    f"Transaction '{transaction_name}' on step '{step_name}' has not been started.",
                )
            return_value = long_running.wait(timeout=timeout)

        # This tool is shared by every long-running transaction, so its declared output schema
        # can't reflect each transaction's actual return type. Mirror behaviour of sync transactions,
        # so callers still get structured content matching the transaction's real return value,
        # instead of only text content.
        if return_value is None or isinstance(return_value, dict):
            return return_value  # pyright: ignore[reportUnknownVariableType]
        return ToolResult(content=return_value, structured_content={"result": return_value})

    _register_transaction_tools(app, solution_class)
    return app
