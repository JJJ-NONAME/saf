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
from pathlib import Path

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from mcp.types import TextResourceContents
from pytest_mock import MockerFixture

from ansys.saf.glow._mcp.server import build_app
from tests.mocks.solution_end_to_end.solution import definition
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution


async def test_mcp_list_tools_resource(mcp_unit_client: Client[FastMCPTransport]):
    result = await mcp_unit_client.read_resource("toolsets://definition")
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


async def test_mcp_solution_workflow_resource(mcp_unit_client: Client[FastMCPTransport]):
    result = await mcp_unit_client.read_resource("solution://workflow")
    assert len(result) == 1
    assert isinstance(result[0], TextResourceContents)
    assert result[0].text == "Step-by-step workflow for using the solution End-to-end solution."


async def test_mcp_saf_concepts_resource(mcp_unit_client: Client[FastMCPTransport]):
    result = await mcp_unit_client.read_resource("saf://concepts")
    assert len(result) == 1
    assert isinstance(result[0], TextResourceContents)
    text = result[0].text
    for keyword in ["Project", "Step", "Field", "Entity handle", "Transaction", "Long-running transaction"]:
        assert keyword in text


async def test_mcp_solution_workflow_resource_can_be_customized(tmp_path: Path, mocker: MockerFixture):
    solution_md = tmp_path / "SOLUTION.md"
    solution_md.write_text("## Workflow\nmy-custom-workflow", encoding="utf-8")
    mocker.patch.object(definition, "__file__", str(tmp_path / "definition.py"))
    mcp = build_app(
        definition_module=definition,
        solution_class=EndToEndSolution,
        solution_api_url="http://localhost:8000",
    )
    async with Client(transport=mcp) as client:
        result = await client.read_resource("solution://workflow")
    assert len(result) == 1
    assert isinstance(result[0], TextResourceContents)
    assert result[0].text == "my-custom-workflow"
