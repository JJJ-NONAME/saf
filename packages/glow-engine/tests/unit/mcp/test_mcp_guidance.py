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
from pathlib import Path

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from pytest_mock import MockerFixture

from ansys.saf.glow._mcp.server import build_app
from tests.e2e.mcp.conftest import assert_mcp_response
from tests.mocks.solution_end_to_end.solution import definition
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution


async def test_mcp_solution_workflow_tool(mcp_unit_client: Client[FastMCPTransport]):
    result = await mcp_unit_client.call_tool("solution_workflow")
    assert_mcp_response(
        result,
        "Step-by-step workflow for using the solution End-to-end solution.",
        has_structure_content=True,
    )


async def test_mcp_saf_concepts_tool(mcp_unit_client: Client[FastMCPTransport]):
    result = await mcp_unit_client.call_tool("saf_concepts")
    assert len(result.content) == 1
    text = result.content[0].text
    for keyword in ["Project", "Step", "Field", "Entity handle", "Transaction", "Long-running transaction"]:
        assert keyword in text


async def test_mcp_solution_workflow_tool_can_be_customized(tmp_path: Path, mocker: MockerFixture):
    solution_md = tmp_path / "SOLUTION.md"
    solution_md.write_text("## Workflow\nmy-custom-workflow", encoding="utf-8")
    mocker.patch.object(definition, "__file__", str(tmp_path / "definition.py"))
    mcp = build_app(
        definition_module=definition,
        solution_class=EndToEndSolution,
        solution_api_url="http://localhost:8000",
    )
    async with Client(transport=mcp) as client:
        result = await client.call_tool("solution_workflow")
    assert_mcp_response(result, "my-custom-workflow", has_structure_content=True)
