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
from fastmcp import Client as MCPClient
from fastmcp.client.transports import StreamableHttpTransport
from mcp.types import TextContent
import pytest

from tests.e2e.mcp.conftest import assert_mcp_response
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution

pytestmark = pytest.mark.parametrize("solution_type", [EndToEndSolution], indirect=True)


@pytest.mark.usefixtures("enable_mcp_server")
class TestMCPGuidance:
    async def test_mcp_solution_workflow_tool(self, mcp_client: MCPClient[StreamableHttpTransport]):
        result = await mcp_client.call_tool("solution_workflow")
        assert_mcp_response(
            result,
            "Step-by-step workflow for using the solution End-to-end solution.",
            has_structure_content=True,
        )

    async def test_mcp_saf_concepts_tool(self, mcp_client: MCPClient[StreamableHttpTransport]):
        result = await mcp_client.call_tool("saf_concepts")
        assert len(result.content) == 1
        assert isinstance(result.content[0], TextContent)
        text = result.content[0].text
        for keyword in ["Project", "Step", "Field", "Entity handle", "Transaction", "Long-running transaction"]:
            assert keyword in text

    @pytest.mark.usefixtures("add_solution_md_file")
    @pytest.mark.parametrize("add_solution_md_file", ["## Workflow\nmy-custom-workflow"], indirect=True)
    async def test_mcp_solution_workflow_tool_can_be_customized(
        self,
        mcp_client: MCPClient[StreamableHttpTransport],
    ):
        result = await mcp_client.call_tool("solution_workflow")
        assert_mcp_response(result, "my-custom-workflow", has_structure_content=True)
