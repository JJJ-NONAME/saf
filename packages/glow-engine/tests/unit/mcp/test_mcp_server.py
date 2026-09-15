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
import inspect
from pathlib import Path
import re
from typing import Any
from unittest.mock import MagicMock

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.exceptions import ToolError
import pytest
from pytest_mock import MockerFixture

from ansys.saf.glow._mcp._resolution import get_step
from ansys.saf.glow._mcp._transaction_metadata import TransactionMetadata
from ansys.saf.glow._mcp.server import build_app
from ansys.saf.glow.client import NotFoundException
from tests.mcp_expectations import (
    LONG_RUNNING_DESCRIPTION_SUFFIX,
    NONEXISTENT_PROJECT_CASES,
    NONEXISTENT_STEP_CASES,
    STATIC_TOOL_DESCRIPTIONS,
    STATIC_TOOL_PARAMETER_DESCRIPTIONS,
    SYNC_DESCRIPTION_SUFFIX,
    TRANSACTION_TOOL_DESCRIPTIONS,
    TRANSACTION_TOOL_PARAMETER_DESCRIPTIONS,
    parameter_descriptions,
    transaction_tool_names,
)
from tests.mocks.solution_end_to_end.solution import definition
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution
from tests.mocks.solution_end_to_end.solution.transaction_verification_step import CustomTypeXYZ


def test_get_step_resolves_named_step():
    project = MagicMock()
    expected_step = project.steps.mesh

    assert get_step(project, "mesh") is expected_step


def test_get_step_rejects_missing_step():
    project = MagicMock()
    project.steps.mesh = None

    with pytest.raises(ValueError, match="Step 'mesh' not found."):
        get_step(project, "mesh")


def test_transaction_metadata_exposes_schema_and_description_data():
    step_type = EndToEndSolution.get_steps_fields()["transaction_verification_step"]
    metadata = TransactionMetadata(
        step_name="transaction_verification_step",
        transaction_name="sum_two_floats_with_inputs_and_output",
        step_type=step_type,
    )

    assert metadata.transaction_parameter_names == ["field_1", "field_2"]
    assert metadata.return_type is float
    assert not metadata.is_long_running
    assert "Transaction args: field_1, field_2." in metadata.description


async def test_mcp_server_is_responsive(mcp_unit_client: Client[FastMCPTransport]):
    healthy = await mcp_unit_client.ping()
    assert healthy


async def test_mcp_server_name_is_solution_display_name(mcp_unit_client: Client[FastMCPTransport]):
    assert mcp_unit_client.initialize_result is not None
    assert mcp_unit_client.initialize_result.serverInfo.name == EndToEndSolution.model_construct().display_name


async def test_mcp_server_has_expected_tools(mcp_unit_client: Client[FastMCPTransport]):
    tools = await mcp_unit_client.list_tools()
    descriptions = {tool.name: tool.description for tool in tools}

    transaction_tools = transaction_tool_names()
    assert transaction_tools
    assert set(descriptions) == set(STATIC_TOOL_DESCRIPTIONS) | set(transaction_tools)

    assert {name: descriptions[name] for name in STATIC_TOOL_DESCRIPTIONS} == STATIC_TOOL_DESCRIPTIONS

    for tool_name, is_long_running in transaction_tools.items():
        description = descriptions[tool_name]
        assert description is not None
        expected_suffix = LONG_RUNNING_DESCRIPTION_SUFFIX if is_long_running else SYNC_DESCRIPTION_SUFFIX
        assert description.endswith(expected_suffix)
        assert description.removesuffix(expected_suffix).strip()


async def test_mcp_server_tool_parameters_have_descriptions(mcp_unit_client: Client[FastMCPTransport]):
    tools = {tool.name: tool for tool in await mcp_unit_client.list_tools()}

    for tool_name, expected_descriptions in STATIC_TOOL_PARAMETER_DESCRIPTIONS.items():
        assert parameter_descriptions(tools[tool_name].inputSchema) == expected_descriptions


async def test_mcp_server_transaction_tools_have_descriptions(mcp_unit_client: Client[FastMCPTransport]):
    tools = await mcp_unit_client.list_tools()

    descriptions = {tool.name: tool.description for tool in tools}
    assert {name: descriptions[name] for name in TRANSACTION_TOOL_DESCRIPTIONS} == TRANSACTION_TOOL_DESCRIPTIONS


async def test_mcp_server_transaction_tool_custom_docstring_keeps_appended_details(
    mcp_unit_client: Client[FastMCPTransport],
):
    """A custom docstring replaces only the default summary sentence, not the appended field/arg/return details."""
    tools = await mcp_unit_client.list_tools()
    descriptions: dict[str, str] = {tool.name: tool.description or "" for tool in tools}

    cases = [
        (
            "transaction_verification_step__get_field_1_and_2_and_set_the_sum_in_result",
            "Run the documented sync transaction.",
            SYNC_DESCRIPTION_SUFFIX,
        ),
        (
            "transaction_verification_step__lr_get_field_1_and_2_and_set_the_sum_in_result",
            "Run the documented long-running transaction.",
            LONG_RUNNING_DESCRIPTION_SUFFIX,
        ),
    ]

    for tool_name, docstring, suffix in cases:
        description = descriptions[tool_name]
        assert description != f"{docstring}{suffix}"
        assert description.startswith(f"{docstring} ")
        assert description.endswith(suffix)
        details = description.removeprefix(f"{docstring} ").removesuffix(suffix)
        assert details.startswith("Download step fields: ")
        assert "Upload step fields: " in details
        assert "Transaction args: " in details
        assert "Return type: " in details


async def test_mcp_server_transaction_tool_parameters_have_descriptions(mcp_unit_client: Client[FastMCPTransport]):
    tools = {tool.name: tool for tool in await mcp_unit_client.list_tools()}

    project_name_description = {"project_name": TRANSACTION_TOOL_PARAMETER_DESCRIPTIONS["project_name"]}
    cases = [
        # sync transactions
        ("transaction_verification_step__get_field_1_and_2_and_set_the_sum_in_result", project_name_description),
        ("custom_http_shared_instance_step__retrieve_value_custom_http_product_instance", project_name_description),
        (
            "transaction_verification_step__sum_two_floats_with_inputs_and_output",
            TRANSACTION_TOOL_PARAMETER_DESCRIPTIONS,
        ),
        ("transaction_verification_step__use_solution_configuration", project_name_description),
        # long-running transactions
        ("transaction_verification_step__lr_get_field_1_and_2_and_set_the_sum_in_result", project_name_description),
        (
            "custom_http_shared_instance_step__retrieve_value_custom_http_product_instance_long_running",
            project_name_description,
        ),
        (
            "transaction_verification_step__lr_sum_two_floats_with_inputs_and_output",
            TRANSACTION_TOOL_PARAMETER_DESCRIPTIONS,
        ),
        ("transaction_verification_step__lr_use_solution_configuration", project_name_description),
    ]

    for tool_name, expected_descriptions in cases:
        assert parameter_descriptions(tools[tool_name].inputSchema) == expected_descriptions


async def test_mcp_server_transaction_tool_parameters_have_output_schemas(mcp_unit_client: Client[FastMCPTransport]):
    tools = {tool.name: tool for tool in await mcp_unit_client.list_tools()}
    step_type = EndToEndSolution.get_steps_fields()["transaction_verification_step"]

    none_schema = {
        "properties": {"result": {"type": "null"}},
        "required": ["result"],
        "type": "object",
        "x-fastmcp-wrap-result": True,
    }
    number_schema = {
        "properties": {"result": {"type": "number"}},
        "required": ["result"],
        "type": "object",
        "x-fastmcp-wrap-result": True,
    }
    string_schema = {
        "properties": {"result": {"type": "string"}},
        "required": ["result"],
        "type": "object",
        "x-fastmcp-wrap-result": True,
    }
    boolean_schema = {
        "properties": {"result": {"type": "boolean"}},
        "required": ["result"],
        "type": "object",
        "x-fastmcp-wrap-result": True,
    }
    # a pydantic model return type gets its own schema, not one wrapped in a "result" property.
    custom_object_schema = {
        "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "z": {"type": "integer"}},
        "required": ["x", "y", "z"],
        "type": "object",
    }

    cases = [
        # sync, non-None return type
        ("sum_two_floats_with_inputs_and_output", float, number_schema),
        # sync, explicit `-> None` return type
        ("set_field_1_to_1", None, none_schema),
        # sync, no return type annotation at all
        ("n_second_sync", inspect.Signature.empty, none_schema),
        # sync, str return type
        ("read_text_file", str, string_schema),
        # sync, bool return type
        ("use_project_cached_at_ui", bool, boolean_schema),
        # sync, custom pydantic model return type
        ("build_and_return_custom_type", CustomTypeXYZ, custom_object_schema),
        # long-running, non-None return type: the tool itself always returns None, since the actual
        # result is only available later, via wait_for_longrunning_transaction.
        ("lr_sum_two_floats_with_inputs_and_output", float, none_schema),
        # long-running, explicit `-> None` return type
        ("lr_get_field_1_and_2_and_set_the_sum_in_result", None, none_schema),
        # long-running, no return type annotation at all
        ("n_second_async", inspect.Signature.empty, none_schema),
    ]

    for transaction_name, expected_return_annotation, expected_schema in cases:
        # guard against the tool's underlying transaction drifting away from the return type this case exercises.
        transaction = getattr(step_type, transaction_name)
        actual_return_annotation = inspect.signature(transaction).return_annotation
        assert actual_return_annotation is expected_return_annotation

        tool_name = f"transaction_verification_step__{transaction_name}"
        assert tools[tool_name].outputSchema == expected_schema


async def test_mcp_server_instructions_is_set(mcp_unit_client: Client[FastMCPTransport]):
    assert mcp_unit_client.initialize_result is not None
    assert mcp_unit_client.initialize_result.instructions == "Instructions for using the solution End-to-end solution."


async def test_mcp_server_instructions_can_be_customized(tmp_path: Path, mocker: MockerFixture):
    solution_md = tmp_path / "SOLUTION.md"
    solution_md.write_text("## Instructions\nmy-custom-instructions", encoding="utf-8")
    mocker.patch.object(definition, "__file__", str(tmp_path / "definition.py"))
    mcp = build_app(
        definition_module=definition,
        solution_class=EndToEndSolution,
        solution_api_url="http://localhost:8000",
    )
    async with Client(transport=mcp) as client:
        assert client.initialize_result is not None
        assert client.initialize_result.instructions == "my-custom-instructions"


async def test_mcp_server_has_expected_resources(mcp_unit_client: Client[FastMCPTransport]):
    resources = await mcp_unit_client.list_resources()
    resource_names = {resource.name for resource in resources}
    expected_resources = {
        "list_tool_sets": ("toolsets://definition", "Available tools for using the Solution."),
        "solution_workflow": ("solution://workflow", "Step by step workflow guideline for using the Solution."),
        "saf_concepts": (
            "saf://concepts",
            "Generic explanation of SAF solution concepts: projects, steps, fields, entity handles, transactions.",
        ),
    }
    assert resource_names == set(expected_resources.keys())
    for resource in resources:
        expected_uri, expected_description = expected_resources[resource.name]
        assert resource.uri.encoded_string() == expected_uri
        assert resource.description == expected_description


async def test_mcp_server_has_expected_prompts(mcp_unit_client: Client[FastMCPTransport]):
    prompts = await mcp_unit_client.list_prompts()
    assert not prompts


@pytest.mark.parametrize(("tool_name", "extra_args"), NONEXISTENT_STEP_CASES)
async def test_tools_raise_on_nonexistent_step(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
    tool_name: str,
    extra_args: dict[str, Any],
):
    _, mock_client_instance = mock_glow_client
    # explicitly set the step attribute to None so getattr(..., None) returns a falsy value
    mock_client_instance.get_project.return_value.steps.nonexistent_step = None

    call_args = {"project_name": "test-project", "step_name": "nonexistent_step", **extra_args}
    with pytest.raises(ToolError, match=re.escape("Step 'nonexistent_step' not found.")):
        await mcp_unit_client.call_tool(tool_name, call_args)


@pytest.mark.parametrize(("tool_name", "extra_args"), NONEXISTENT_PROJECT_CASES)
async def test_tools_raise_on_nonexistent_project(
    mcp_unit_client: Client[FastMCPTransport],
    mock_glow_client: tuple[MagicMock, MagicMock],
    tool_name: str,
    extra_args: dict[str, Any],
):
    _, mock_client_instance = mock_glow_client
    mock_client_instance.get_project.side_effect = NotFoundException("Project 'nonexistent_project' not found.")

    with pytest.raises(ToolError) as exc_info:
        await mcp_unit_client.call_tool(tool_name, {"project_name": "nonexistent_project", **extra_args})
    assert "not found" in str(exc_info.value).lower()
