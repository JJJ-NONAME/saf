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

from ansys.saf.testing.solution.end_to_end import ProjectFixture
from fastmcp import Client as MCPClient
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.exceptions import ToolError
import pytest

from tests.e2e.mcp.conftest import assert_mcp_response, assert_no_mcp_response
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution

pytestmark = pytest.mark.parametrize("solution_type", [EndToEndSolution], indirect=True)


@pytest.mark.usefixtures("enable_mcp_server")
class TestMCPDataManagement:
    async def test_set_fields_tool(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_project: ProjectFixture[EndToEndSolution],
    ):
        step = function_project.project.steps.transaction_verification_step
        fields: dict[str, Any] = {
            "field_1": 3.5,
            "sleepy_seconds": 2,
            "text_content": "updated-through-mcp",
            "child_process_is_running": True,
        }
        for field_name, value in fields.items():
            assert getattr(step, field_name) != value

        result = await mcp_client.call_tool(
            "set_fields",
            {
                "project_name": function_project.project_name,
                "step_name": "transaction_verification_step",
                "fields": fields,
            },
        )
        assert_no_mcp_response(result)

        for field_name, value in fields.items():
            assert getattr(step, field_name) == value

    async def test_get_fields_tool(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_project: ProjectFixture[EndToEndSolution],
    ):
        step = function_project.project.steps.transaction_verification_step
        fields: dict[str, Any] = {
            "field_1": 4.5,
            "sleepy_seconds": 11,
            "text_content": "read-through-mcp",
            "child_process_is_running": True,
        }
        for field_name, value in fields.items():
            setattr(step, field_name, value)

        result = await mcp_client.call_tool(
            "get_fields",
            {
                "project_name": function_project.project_name,
                "step_name": "transaction_verification_step",
                "field_names": list(fields),
            },
        )
        assert result.structured_content == {**fields, "sleepy_seconds": 11.0}

    async def test_upload_file_tool(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_project: ProjectFixture[EndToEndSolution],
    ):
        step = function_project.project.steps.transaction_verification_step
        content = b"uploaded-through-mcp"

        result = await mcp_client.call_tool(
            "upload_file",
            {
                "project_name": function_project.project_name,
                "step_name": "transaction_verification_step",
                "entity_handle_name": "text_file",
                "content": content,
            },
        )
        assert_no_mcp_response(result)

        assert function_project.project.storage_scope.get_bytes(step.text_file) == content

    async def test_download_file_tool(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_project: ProjectFixture[EndToEndSolution],
    ):
        step = function_project.project.steps.transaction_verification_step
        content = b"downloaded-through-mcp"
        step.text_file = function_project.project.storage_scope.store_stream(content)

        result = await mcp_client.call_tool(
            "download_file",
            {
                "project_name": function_project.project_name,
                "step_name": "transaction_verification_step",
                "entity_handle_name": "text_file",
            },
        )
        assert_mcp_response(result, content.decode(), has_structure_content=False)

    @pytest.mark.parametrize("tool_name", ["set_fields", "get_fields", "upload_file", "download_file"])
    async def test_data_tools_with_non_existing_field(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_project: ProjectFixture[EndToEndSolution],
        tool_name: str,
    ):
        call_args: dict[str, Any] = {
            "project_name": function_project.project_name,
            "step_name": "transaction_verification_step",
        }
        expected_error_msg = (
            "At least one of the provided field names is not a 'TransactionVerificationStep' step field."
        )
        if tool_name in ["set_fields", "get_fields"]:
            if tool_name == "set_fields":
                call_args["fields"] = {"non_existing_field": 1.0}
                expected_error_msg = "'TransactionVerificationStep' has no field(s) 'non_existing_field'."
            else:
                call_args["field_names"] = ["non_existing_field"]
        elif tool_name in ["upload_file", "download_file"]:
            expected_error_msg = "Field 'non_existing_field' is not an entityhandle field."
            call_args["entity_handle_name"] = "non_existing_field"
            if tool_name == "upload_file":
                call_args["content"] = b"invalid-target-field"

        with pytest.raises(ToolError, match=re.escape(expected_error_msg)):
            await mcp_client.call_tool(tool_name, call_args)

    @pytest.mark.parametrize("tool_name", ["upload_file", "download_file"])
    async def test_file_tools_with_non_entity_handle_field(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
        function_project: ProjectFixture[EndToEndSolution],
        tool_name: str,
    ):
        call_args: dict[str, str | bytes] = {
            "project_name": function_project.project_name,
            "step_name": "transaction_verification_step",
            "entity_handle_name": "field_1",
        }
        if tool_name == "upload_file":
            call_args["content"] = b"invalid-target-field"

        with pytest.raises(ToolError, match="Field 'field_1' is not an entityhandle field."):
            await mcp_client.call_tool(tool_name, call_args)
