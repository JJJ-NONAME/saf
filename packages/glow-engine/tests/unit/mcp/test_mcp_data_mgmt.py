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
import re
from typing import Any
from unittest.mock import MagicMock

from ansys.bdm.api import EntityHandle
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.exceptions import ToolError
import pytest

from tests.e2e.mcp.conftest import assert_mcp_response, assert_no_mcp_response


async def test_set_fields_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client
    mock_step = mock_instance.get_project.return_value.steps.transaction_verification_step
    fields: dict[str, Any] = {
        "field_1": 3.5,
        "sleepy_seconds": 2.0,
        "text_content": "updated-through-mcp",
        "child_process_is_running": True,
    }

    result = await mcp_unit_client.call_tool(
        "set_fields",
        {
            "project_name": "test-project",
            "step_name": "transaction_verification_step",
            "fields": fields,
        },
    )
    assert_no_mcp_response(result)
    mock_step.set_fields.assert_called_once_with(fields)


async def test_get_fields_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client
    mock_step = mock_instance.get_project.return_value.steps.transaction_verification_step
    field_names = ["field_1", "sleepy_seconds", "text_content", "child_process_is_running"]
    fields: dict[str, Any] = {
        "field_1": 4.5,
        "sleepy_seconds": 11.0,
        "text_content": "read-through-mcp",
        "child_process_is_running": True,
    }
    mock_step.get_fields.return_value = fields

    result = await mcp_unit_client.call_tool(
        "get_fields",
        {
            "project_name": "test-project",
            "step_name": "transaction_verification_step",
            "field_names": field_names,
        },
    )
    assert result.structured_content == fields
    mock_step.get_fields.assert_called_once_with(field_names)


async def test_upload_file_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client
    mock_step = mock_instance.get_project.return_value.steps.transaction_verification_step
    mock_step.text_file = MagicMock(spec=EntityHandle)
    mock_project = mock_instance.get_project.return_value

    content = b"uploaded-through-mcp"
    result = await mcp_unit_client.call_tool(
        "upload_file",
        {
            "project_name": "test-project",
            "step_name": "transaction_verification_step",
            "entity_handle_name": "text_file",
            "content": content,
        },
    )
    assert_no_mcp_response(result)
    mock_project.storage_scope.store_stream.assert_called_once_with(content)


async def test_download_file_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
):
    _, mock_instance = mock_glow_client
    mock_step = mock_instance.get_project.return_value.steps.transaction_verification_step
    mock_step.text_file = MagicMock(spec=EntityHandle)
    mock_project = mock_instance.get_project.return_value

    content = b"downloaded-through-mcp"
    mock_project.storage_scope.get_bytes.return_value = content

    result = await mcp_unit_client.call_tool(
        "download_file",
        {
            "project_name": "test-project",
            "step_name": "transaction_verification_step",
            "entity_handle_name": "text_file",
        },
    )
    assert_mcp_response(result, content.decode(), has_structure_content=False)


@pytest.mark.parametrize("tool_name", ["set_fields", "get_fields", "upload_file", "download_file"])
async def test_data_tools_with_non_existing_field(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
    tool_name: str,
):
    _, mock_instance = mock_glow_client
    mock_step = mock_instance.get_project.return_value.steps.transaction_verification_step

    call_args: dict[str, Any] = {
        "project_name": "test-project",
        "step_name": "transaction_verification_step",
    }
    expected_error_msg = "At least one of the provided field names is not a 'TransactionVerificationStep' step field."
    if tool_name in ["set_fields", "get_fields"]:
        if tool_name == "set_fields":
            call_args["fields"] = {"non_existing_field": 1.0}
            expected_error_msg = "'TransactionVerificationStep' has no field(s) 'non_existing_field'."
            mock_step.set_fields.side_effect = ValueError(expected_error_msg)
        else:
            call_args["field_names"] = ["non_existing_field"]
            mock_step.get_fields.side_effect = ValueError(expected_error_msg)
    elif tool_name in ["upload_file", "download_file"]:
        expected_error_msg = "Field 'non_existing_field' is not an entityhandle field."
        call_args["entity_handle_name"] = "non_existing_field"
        if tool_name == "upload_file":
            call_args["content"] = b"invalid-target-field"

    with pytest.raises(ToolError, match=re.escape(expected_error_msg)):
        await mcp_unit_client.call_tool(tool_name, call_args)


@pytest.mark.parametrize("tool_name", ["upload_file", "download_file"])
async def test_file_tools_with_non_entity_handle_field(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
    tool_name: str,
):
    # mock_step.field_1 is a MagicMock (not EntityHandle), so the isinstance check raises
    call_args: dict[str, str | bytes] = {
        "project_name": "test-project",
        "step_name": "transaction_verification_step",
        "entity_handle_name": "field_1",
    }
    if tool_name == "upload_file":
        call_args["content"] = b"invalid-target-field"

    with pytest.raises(ToolError, match="Field 'field_1' is not an entityhandle field."):
        await mcp_unit_client.call_tool(tool_name, call_args)
