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
import json

from fastmcp import Client as MCPClient
from fastmcp.client.transports import StreamableHttpTransport
from mcp.types import TextResourceContents
import pytest

from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution

pytestmark = pytest.mark.parametrize("solution_type", [EndToEndSolution], indirect=True)


@pytest.mark.usefixtures("enable_mcp_server")
class TestMCPResources:
    async def test_mcp_list_tools_resource(self, mcp_client: MCPClient[StreamableHttpTransport]):
        result = await mcp_client.read_resource("toolsets://definition")
        assert len(result) == 1
        assert isinstance(result[0], TextResourceContents)
        toolsets = json.loads(result[0].text)
        assert len(toolsets) == 3
        assert toolsets[0] == {
            "name": "project",
            "description": "Tools for managing projects",
            "tools": [
                "create_project",
                "list_projects",
                "delete_projects",
                "import_project",
                "export_project",
            ],
        }
        assert toolsets[1] == {
            "name": "data",
            "description": "Tools for setting and retrieving fields and files",
            "tools": ["set_fields", "get_fields", "upload_file", "download_file"],
        }

        expected_dynamic_tools: set[str] = set()
        for step_name, step_type in EndToEndSolution.get_steps_fields().items():
            for transaction_name in step_type.get_transaction_method_names():
                expected_dynamic_tools.add(f"{step_name}__{transaction_name}")
        assert toolsets[2] == {
            "name": "transactions",
            "description": "Tools for running transactions",
            "tools": [*sorted(expected_dynamic_tools), "wait_for_longrunning_transaction"],
        }

    async def test_mcp_solution_workflow_resource(self, mcp_client: MCPClient[StreamableHttpTransport]):
        result = await mcp_client.read_resource("solution://workflow")
        assert len(result) == 1
        assert isinstance(result[0], TextResourceContents)
        assert result[0].text == "Step-by-step workflow for using the solution End-to-end solution."

    async def test_mcp_saf_concepts_resource(self, mcp_client: MCPClient[StreamableHttpTransport]):
        result = await mcp_client.read_resource("saf://concepts")
        assert len(result) == 1
        assert isinstance(result[0], TextResourceContents)
        text = result[0].text
        for keyword in ["Project", "Step", "Field", "Entity handle", "Transaction", "Long-running transaction"]:
            assert keyword in text

    @pytest.mark.usefixtures("add_solution_md_file")
    @pytest.mark.parametrize("add_solution_md_file", ["## Workflow\nmy-custom-workflow"], indirect=True)
    async def test_mcp_solution_workflow_resource_can_be_customized(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
    ):
        result = await mcp_client.read_resource("solution://workflow")
        assert len(result) == 1
        assert isinstance(result[0], TextResourceContents)
        assert result[0].text == "my-custom-workflow"
