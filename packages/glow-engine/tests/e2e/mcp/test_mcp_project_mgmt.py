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
from base64 import b64decode, b64encode
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastmcp import Client as MCPClient
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.exceptions import ToolError
import pytest

from ansys.saf.glow.client import Client
from tests.e2e.mcp.conftest import assert_mcp_response
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution
from tests.mocks.solution_end_to_end.solution.transaction_verification_step import TEXT_FILE_DUMMY_STRING

pytestmark = pytest.mark.parametrize("solution_type", [EndToEndSolution], indirect=True)


def _get_project_names(client: Client[EndToEndSolution], old_project_names: list[str] | None = None) -> list[str]:
    return [
        proj["name"]
        for proj in client.list_projects(filter="display_name = mcp-")["projects"]
        if proj["name"] not in (old_project_names or [])
    ]


@pytest.mark.usefixtures("enable_mcp_server")
class TestMCPProjectManagement:
    async def test_create_project_tool(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_client: Client[EndToEndSolution],
    ):
        old_projects_names = _get_project_names(function_client)

        result = await mcp_client.call_tool("create_project")
        new_project_names = _get_project_names(function_client, old_projects_names)
        assert len(new_project_names) == 1
        assert_mcp_response(result, new_project_names[0], has_structure_content=True)

        # every call should create a new project with a different name
        result = await mcp_client.call_tool("create_project")
        newer_project_names = _get_project_names(function_client, old_projects_names + new_project_names)
        assert len(newer_project_names) == 1
        assert_mcp_response(result, newer_project_names[0], has_structure_content=True)

    async def test_create_project_tool_with_display_name(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_client: Client[EndToEndSolution],
        random_project_name: Callable[[], str],
    ):
        display_name = random_project_name()

        result = await mcp_client.call_tool("create_project", {"display_name": display_name})
        matching = function_client.list_projects(filter=f"display_name = '{display_name}'")["projects"]
        assert len(matching) == 1
        assert_mcp_response(result, matching[0]["name"], has_structure_content=True)

        # calling again with the same display_name creates another project rather than erroring
        result = await mcp_client.call_tool("create_project", {"display_name": display_name})
        matching = function_client.list_projects(filter=f"display_name = '{display_name}'")["projects"]
        assert len(matching) == 2
        assert result.structured_content is not None
        assert result.structured_content["result"] in [proj["name"] for proj in matching]

    @pytest.mark.parametrize("display_name", ["", "   "], ids=["empty", "blank"])
    async def test_create_project_tool_rejects_blank_display_name(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        display_name: str,
    ):
        with pytest.raises(ToolError, match="display_name must not be empty or blank."):
            await mcp_client.call_tool("create_project", {"display_name": display_name})

    async def test_list_projects_tool(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_client: Client[EndToEndSolution],
    ):
        created = function_client.create_project("mcp-listed").project_name

        result = await mcp_client.call_tool("list_projects", {"filter": "display_name = mcp-listed"})
        assert isinstance(result.structured_content, dict)
        assert [proj["name"] for proj in result.structured_content["projects"]] == [created]

    async def test_delete_projects_tool(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_client: Client[EndToEndSolution],
    ):
        names = [
            function_client.create_project("mcp-deleted-1").project_name,
            function_client.create_project("mcp-deleted-2").project_name,
        ]

        result = await mcp_client.call_tool("delete_projects", {"names": names})
        assert result.structured_content == dict.fromkeys(names, "deleted")

        remaining = function_client.list_projects(filter="display_name = mcp-deleted")["projects"]
        assert remaining == []

    async def test_delete_projects_tool_reports_unknown_project(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
    ):
        result = await mcp_client.call_tool("delete_projects", {"names": ["projects/does-not-exist"]})
        assert isinstance(result.structured_content, dict)
        assert result.structured_content["projects/does-not-exist"] != "deleted"

    async def test_export_then_import_project_round_trip(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_client: Client[EndToEndSolution],
    ):
        exported_name = function_client.create_project("mcp-round-trip").project_name

        fields: dict[str, Any] = {"field_1": 7.5, "text_content": "round-trip-through-mcp"}
        await mcp_client.call_tool(
            "set_fields",
            {
                "project_name": exported_name,
                "step_name": "transaction_verification_step",
                "fields": fields,
            },
        )
        await mcp_client.call_tool(
            "transaction_verification_step__create_text_file",
            {"project_name": exported_name},
        )

        export_result = await mcp_client.call_tool("export_project", {"project_name": exported_name})
        assert isinstance(export_result.structured_content, dict)
        archive = b64decode(export_result.structured_content["result"], validate=True)
        # a '.safx' archive is a zip.
        assert archive.startswith(b"PK")

        import_result = await mcp_client.call_tool(
            "import_project",
            {"content": b64encode(archive).decode(), "display_name": "mcp-round-trip-imported"},
        )
        assert isinstance(import_result.structured_content, dict)
        imported_name = import_result.structured_content["result"]
        assert imported_name != exported_name

        imported = function_client.list_projects(filter="display_name = mcp-round-trip-imported")["projects"]
        assert [proj["name"] for proj in imported] == [imported_name]

        # the modified fields and the file written by the transaction must survive the round trip.
        # check the fields before running 'read_text_file', which uploads 'text_content' without downloading it.
        fields_result = await mcp_client.call_tool(
            "get_fields",
            {
                "project_name": imported_name,
                "step_name": "transaction_verification_step",
                "field_names": list(fields),
            },
        )
        assert fields_result.structured_content == fields

        read_result = await mcp_client.call_tool(
            "transaction_verification_step__read_text_file",
            {"project_name": imported_name},
        )
        assert_mcp_response(read_result, TEXT_FILE_DUMMY_STRING, has_structure_content=True)

    async def test_export_with_client_then_import_with_mcp(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_client: Client[EndToEndSolution],
        tmp_path: Path,
    ):
        """An archive exported with the Client API can be imported with the MCP tool."""
        display_name = "mcp-client-export"
        project = function_client.create_project(display_name)
        project.steps.transaction_verification_step.create_text_file()

        project.export(tmp_path)
        archive = (tmp_path / f"{display_name}.safx").read_bytes()

        import_result = await mcp_client.call_tool(
            "import_project",
            {"content": b64encode(archive).decode(), "display_name": "mcp-client-export-imported"},
        )
        assert isinstance(import_result.structured_content, dict)
        imported_name = import_result.structured_content["result"]
        assert imported_name != project.project_name

        imported = function_client.get_project(imported_name)
        assert imported.steps.transaction_verification_step.read_text_file() == TEXT_FILE_DUMMY_STRING

    async def test_export_with_mcp_then_import_with_client(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_client: Client[EndToEndSolution],
        tmp_path: Path,
    ):
        """An archive exported with the MCP tool can be imported with the Client API."""
        project = function_client.create_project("mcp-mcp-export")
        project.steps.transaction_verification_step.create_text_file()

        export_result = await mcp_client.call_tool("export_project", {"project_name": project.project_name})
        assert isinstance(export_result.structured_content, dict)
        archive = b64decode(export_result.structured_content["result"], validate=True)

        safx_path = tmp_path / "exported.safx"
        safx_path.write_bytes(archive)

        imported = function_client.import_project(safx_path, "mcp-mcp-export-imported")
        assert imported.project_name != project.project_name
        assert imported.steps.transaction_verification_step.read_text_file() == TEXT_FILE_DUMMY_STRING
