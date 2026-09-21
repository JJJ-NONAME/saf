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
from typing import Annotated, Any

from ansys.bdm.api import EntityHandle
from fastmcp import FastMCP
from fastmcp.server import Context
from pydantic import Field

from ansys.saf.glow._mcp._resolution import get_solution_config, get_step


def register_data_tools(app: FastMCP, client_factory: Any) -> None:
    @app.tool()
    def set_fields(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        project_name: Annotated[str, Field(description="Name of the project to update.")],
        step_name: Annotated[str, Field(description="Name of the step containing the fields.")],
        fields: Annotated[dict[str, Any], Field(description="Field names mapped to their new values.")],
    ) -> None:
        """Set field values on a solution step."""
        solution_class, solution_api_url = get_solution_config(ctx)

        with client_factory(solution_class, solution_api_url) as client:
            project = client.get_project(project_name)
            get_step(project, step_name).set_fields(fields)

    @app.tool()
    def get_fields(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        project_name: Annotated[str, Field(description="Name of the project to read.")],
        step_name: Annotated[str, Field(description="Name of the step containing the fields.")],
        field_names: Annotated[list[str], Field(description="Names of the fields to read.")],
    ) -> dict[str, Any]:
        """Get field values from a solution step."""
        solution_class, solution_api_url = get_solution_config(ctx)

        with client_factory(solution_class, solution_api_url) as client:
            project = client.get_project(project_name)
            fields = get_step(project, step_name).get_fields(field_names)
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
        solution_class, solution_api_url = get_solution_config(ctx)

        with client_factory(solution_class, solution_api_url) as client:
            project = client.get_project(project_name)
            step = get_step(project, step_name)
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
        solution_class, solution_api_url = get_solution_config(ctx)

        with client_factory(solution_class, solution_api_url) as client:
            project = client.get_project(project_name)
            step = get_step(project, step_name)
            entity_handle_field = getattr(step, entity_handle_name, None)
            if not isinstance(entity_handle_field, EntityHandle):
                raise ValueError(f"Field '{entity_handle_name}' is not an entityhandle field.")
            content = project.storage_scope.get_bytes(entity_handle_field)
        return content
