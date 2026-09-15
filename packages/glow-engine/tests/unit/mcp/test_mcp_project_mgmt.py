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
from base64 import b64encode
from unittest.mock import MagicMock

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.exceptions import ToolError
import pytest

from tests.e2e.mcp.conftest import assert_mcp_response

# a '.safx' archive is a zip, so it is binary and not utf-8 decodable.
SAFX_CONTENT = b"PK\x03\x04\x14\x00\x00\x00\x08\x00\xff\xfe\xfd\x00safx"


async def test_create_project_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client

    proj1 = MagicMock()
    proj1.project_name = "mcp-0001"
    proj2 = MagicMock()
    proj2.project_name = "mcp-0002"
    mock_instance.create_project.side_effect = [proj1, proj2]

    result = await mcp_unit_client.call_tool("create_project")
    assert_mcp_response(result, "mcp-0001", has_structure_content=True)

    # every call should create a new project
    result = await mcp_unit_client.call_tool("create_project")
    assert_mcp_response(result, "mcp-0002", has_structure_content=True)

    assert mock_instance.create_project.call_count == 2


async def test_create_project_tool_with_display_name(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client

    project = MagicMock()
    project.project_name = "projects/my-project"
    mock_instance.create_project.return_value = project

    result = await mcp_unit_client.call_tool("create_project", {"display_name": "my project"})
    assert_mcp_response(result, "projects/my-project", has_structure_content=True)
    mock_instance.create_project.assert_called_once_with("my project")


@pytest.mark.parametrize("display_name", ["", "   "], ids=["empty", "blank"])
async def test_create_project_tool_rejects_blank_display_name(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
    display_name: str,
):
    _, mock_instance = mock_glow_client

    with pytest.raises(ToolError, match="display_name must not be empty or blank."):
        await mcp_unit_client.call_tool("create_project", {"display_name": display_name})

    mock_instance.create_project.assert_not_called()


async def test_create_project_tool_with_display_name_allows_duplicates(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client

    proj1 = MagicMock()
    proj1.project_name = "projects/my-project-1"
    proj2 = MagicMock()
    proj2.project_name = "projects/my-project-2"
    mock_instance.create_project.side_effect = [proj1, proj2]

    result = await mcp_unit_client.call_tool("create_project", {"display_name": "my project"})
    assert_mcp_response(result, "projects/my-project-1", has_structure_content=True)

    # calling again with the same display_name creates another project rather than erroring
    result = await mcp_unit_client.call_tool("create_project", {"display_name": "my project"})
    assert_mcp_response(result, "projects/my-project-2", has_structure_content=True)

    assert mock_instance.create_project.call_args_list == [
        (("my project",),),
        (("my project",),),
    ]


async def test_list_projects_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client
    listing = {
        "projects": [{"name": "projects/abc", "display_name": "mcp-0001"}],
        "current_page": 1,
        "total_pages": 1,
        "page_size": 100,
        "total_projects": 1,
    }
    mock_instance.list_projects.return_value = listing

    result = await mcp_unit_client.call_tool("list_projects")
    assert result.structured_content == listing
    mock_instance.list_projects.assert_called_once_with(page_size=None, page=None, order_by=None, filter=None)


async def test_list_projects_tool_forwards_query_arguments(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client
    mock_instance.list_projects.return_value = {"projects": []}

    await mcp_unit_client.call_tool(
        "list_projects",
        {"page_size": 5, "page": 2, "order_by": "date_modified desc", "filter": "display_name = mcp-"},
    )
    mock_instance.list_projects.assert_called_once_with(
        page_size=5,
        page=2,
        order_by="date_modified desc",
        filter="display_name = mcp-",
    )


async def test_delete_projects_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client

    result = await mcp_unit_client.call_tool(
        "delete_projects",
        {"names": ["projects/abc", "projects/def"]},
    )
    assert result.structured_content == {"projects/abc": "deleted", "projects/def": "deleted"}
    assert [call.args[0] for call in mock_instance.delete_project.call_args_list] == [
        "projects/abc",
        "projects/def",
    ]


async def test_delete_projects_tool_deletes_each_name_once(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client

    result = await mcp_unit_client.call_tool(
        "delete_projects",
        {"names": ["projects/abc", "projects/abc"]},
    )
    assert result.structured_content == {"projects/abc": "deleted"}
    assert mock_instance.delete_project.call_count == 1


async def test_delete_projects_tool_reports_failures_per_project(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client
    mock_instance.delete_project.side_effect = [None, ValueError("project not found"), None]

    result = await mcp_unit_client.call_tool(
        "delete_projects",
        {"names": ["projects/abc", "projects/missing", "projects/def"]},
    )
    assert result.structured_content == {
        "projects/abc": "deleted",
        "projects/missing": "project not found",
        "projects/def": "deleted",
    }


async def test_delete_projects_tool_without_names(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client

    result = await mcp_unit_client.call_tool("delete_projects", {"names": []})
    assert result.structured_content == {}
    mock_instance.delete_project.assert_not_called()


async def test_import_project_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client
    project = MagicMock()
    project.project_name = "projects/imported"
    mock_instance.import_project.return_value = project

    written: dict[str, bytes] = {}
    mock_instance.import_project.side_effect = lambda path, _name: (  # type: ignore
        written.update(content=path.read_bytes()),  # type: ignore
        project,
    )[1]

    result = await mcp_unit_client.call_tool(
        "import_project",
        {"content": b64encode(SAFX_CONTENT).decode(), "display_name": "imported project"},
    )
    assert_mcp_response(result, "projects/imported", has_structure_content=True)

    # the binary archive must survive the base64 transport unchanged.
    assert written["content"] == SAFX_CONTENT

    safx_path, display_name = mock_instance.import_project.call_args.args
    assert display_name == "imported project"
    # the temporary file holding the uploaded content is removed once the tool returns.
    assert not safx_path.exists()


async def test_import_project_tool_rejects_invalid_base64(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client

    result = await mcp_unit_client.call_tool(
        "import_project",
        {"content": "not base64!", "display_name": "imported project"},
        raise_on_error=False,
    )
    assert result.is_error
    mock_instance.import_project.assert_not_called()


async def test_export_project_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client
    project = MagicMock()
    project.export.side_effect = lambda destination: (destination / "my project.safx").write_bytes(SAFX_CONTENT)  # type: ignore
    mock_instance.get_project.return_value = project

    result = await mcp_unit_client.call_tool("export_project", {"project_name": "projects/abc"})
    assert_mcp_response(result, b64encode(SAFX_CONTENT).decode(), has_structure_content=True)
    mock_instance.get_project.assert_called_once_with("projects/abc")

    # the temporary directory holding the exported archive is removed once the tool returns.
    (destination,) = project.export.call_args.args
    assert not destination.exists()
