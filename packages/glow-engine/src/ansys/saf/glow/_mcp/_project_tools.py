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
from pathlib import Path
from random import randint
import tempfile
from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.server import Context
from pydantic import Field

from ansys.saf.glow._mcp._resolution import get_solution_config


def register_project_tools(app: FastMCP, client_factory: Any) -> None:  # noqa: C901
    @app.tool()
    def create_project(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        display_name: Annotated[
            str | None,
            Field(description="Project name displayed to the user. If not set, a name is generated automatically."),
        ] = None,
    ) -> str:
        """Create a solution project."""
        solution_class, solution_api_url = get_solution_config(ctx)

        if display_name is not None and not display_name.strip():
            raise ValueError("display_name must not be empty or blank.")

        if display_name is None:
            display_name = f"mcp-{str(randint(0, 10000)).zfill(4)}"  # noqa: S311

        with client_factory(solution_class, solution_api_url) as client:
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
        solution_class, solution_api_url = get_solution_config(ctx)

        with client_factory(solution_class, solution_api_url) as client:
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
        solution_class, solution_api_url = get_solution_config(ctx)

        outcomes: dict[str, str] = {}
        with client_factory(solution_class, solution_api_url) as client:
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
        solution_class, solution_api_url = get_solution_config(ctx)

        try:
            archive = b64decode(content, validate=True)
        except BinasciiError as ex:
            raise ValueError(f"Content is not valid base64: {ex}") from None

        with tempfile.TemporaryDirectory() as tmp_dir:
            safx_path = Path(tmp_dir) / "project.safx"
            safx_path.write_bytes(archive)
            with client_factory(solution_class, solution_api_url) as client:
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
        solution_class, solution_api_url = get_solution_config(ctx)

        with tempfile.TemporaryDirectory() as tmp_dir:
            destination = Path(tmp_dir)
            with client_factory(solution_class, solution_api_url) as client:
                client.get_project(project_name).export(destination)
            # there should be only one file, so we avoid the extra http request to retrieve the project display name.
            safx_path = next(destination.glob("*.safx"))
            return b64encode(safx_path.read_bytes()).decode()
