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
from unittest.mock import MagicMock

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.exceptions import ToolError
import pytest
import pytest_mock

from ansys.saf.glow.client import LongRunning
from ansys.saf.glow.solution import MethodStatus
from tests.e2e.mcp.conftest import assert_mcp_response, assert_no_mcp_response
from tests.mocks.solution_end_to_end.solution.transaction_verification_step import TransactionVerificationStep


@pytest.fixture(autouse=True)
def mock_transaction_step(mock_glow_client: tuple[MagicMock, MagicMock]) -> MagicMock:
    _, mock_instance = mock_glow_client
    mock_step = mock_instance.get_project.return_value.steps.transaction_verification_step
    mock_step._step_model_type = TransactionVerificationStep
    return mock_step


async def test_wait_for_longrunning_transaction_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mocker: pytest_mock.MockerFixture,
):
    mock_get_state = mocker.patch.object(
        LongRunning,
        "get_state",
        autospec=True,
        return_value=MagicMock(status=MethodStatus.Running),
    )
    mock_wait = mocker.patch.object(LongRunning, "wait", autospec=True, return_value=None)

    result = await mcp_unit_client.call_tool(
        "wait_for_longrunning_transaction",
        {
            "project_name": "test-project",
            "step_name": "transaction_verification_step",
            "transaction_name": "lr_get_field_1_and_2_and_set_the_sum_in_result",
        },
    )
    assert_no_mcp_response(result)
    mock_get_state.assert_called_once()
    mock_wait.assert_called_once()


async def test_wait_for_longrunning_transaction_tool_with_return_value(
    mcp_unit_client: Client[FastMCPTransport],
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch.object(LongRunning, "get_state", autospec=True, return_value=MagicMock(status=MethodStatus.Running))
    mocker.patch.object(LongRunning, "wait", autospec=True, return_value=5.0)

    result = await mcp_unit_client.call_tool(
        "wait_for_longrunning_transaction",
        {
            "project_name": "test-project",
            "step_name": "transaction_verification_step",
            "transaction_name": "lr_sum_two_floats_with_inputs_and_output",
        },
    )
    assert_mcp_response(result, "5.0", has_structure_content=True, structured_result=5.0)


async def test_wait_for_longrunning_transaction_tool_with_timeout(
    mcp_unit_client: Client[FastMCPTransport],
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch.object(LongRunning, "get_state", autospec=True, return_value=MagicMock(status=MethodStatus.Running))
    mocker.patch.object(
        LongRunning,
        "wait",
        autospec=True,
        side_effect=TimeoutError(
            "Waiting for the long running method 'lr_get_field_1_and_2_and_set_the_sum_in_result' timed out.",
        ),
    )

    with pytest.raises(ToolError, match="timed out"):
        await mcp_unit_client.call_tool(
            "wait_for_longrunning_transaction",
            {
                "project_name": "test-project",
                "step_name": "transaction_verification_step",
                "transaction_name": "lr_get_field_1_and_2_and_set_the_sum_in_result",
                "timeout": 1,
            },
        )


async def test_wait_for_longrunning_transaction_tool_with_sync_transaction(
    mcp_unit_client: Client[FastMCPTransport],
):
    with pytest.raises(ToolError, match="is not a long-running transaction"):
        await mcp_unit_client.call_tool(
            "wait_for_longrunning_transaction",
            {
                "project_name": "test-project",
                "step_name": "transaction_verification_step",
                "transaction_name": "get_field_1_and_2_and_set_the_sum_in_result",
            },
        )


async def test_wait_for_longrunning_transaction_tool_that_fails(
    mcp_unit_client: Client[FastMCPTransport],
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch.object(LongRunning, "get_state", autospec=True, return_value=MagicMock(status=MethodStatus.Running))
    mocker.patch.object(
        LongRunning,
        "wait",
        autospec=True,
        side_effect=RuntimeError("The solution encountered an internal error"),
    )

    with pytest.raises(ToolError, match="The solution encountered an internal error"):
        await mcp_unit_client.call_tool(
            "wait_for_longrunning_transaction",
            {
                "project_name": "test-project",
                "step_name": "transaction_verification_step",
                "transaction_name": "lr_raise_exception",
            },
        )


async def test_wait_for_longrunning_transaction_tool_with_not_started_transaction(
    mcp_unit_client: Client[FastMCPTransport],
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch.object(
        LongRunning,
        "get_state",
        autospec=True,
        return_value=MagicMock(status=MethodStatus.RunRequired),
    )

    with pytest.raises(ToolError, match="has not been started"):
        await mcp_unit_client.call_tool(
            "wait_for_longrunning_transaction",
            {
                "project_name": "test-project",
                "step_name": "transaction_verification_step",
                "transaction_name": "lr_get_field_1_and_2_and_set_the_sum_in_result",
            },
        )


async def test_wait_for_longrunning_transaction_tool_with_non_existent_transaction(
    mcp_unit_client: Client[FastMCPTransport],
):
    with pytest.raises(ToolError, match="is not a long-running transaction"):
        await mcp_unit_client.call_tool(
            "wait_for_longrunning_transaction",
            {
                "project_name": "test-project",
                "step_name": "transaction_verification_step",
                "transaction_name": "my_non_existent_transaction",
            },
        )


async def test_sync_transaction_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mock_transaction_step: MagicMock,
):
    mock_transaction_step.get_field_1_and_2_and_set_the_sum_in_result.return_value = None

    result = await mcp_unit_client.call_tool(
        "transaction_verification_step__get_field_1_and_2_and_set_the_sum_in_result",
        {"project_name": "test-project"},
    )
    assert_no_mcp_response(result)
    mock_transaction_step.get_field_1_and_2_and_set_the_sum_in_result.assert_called_once_with()


async def test_sync_transaction_tool_that_fails(
    mcp_unit_client: Client[FastMCPTransport],
    mock_transaction_step: MagicMock,
):
    mock_transaction_step.raise_exception.side_effect = RuntimeError("The solution encountered an internal error")
    with pytest.raises(ToolError, match="The solution encountered an internal error"):
        await mcp_unit_client.call_tool(
            "transaction_verification_step__raise_exception",
            {"project_name": "test-project"},
        )


async def test_sync_transaction_tool_with_custom_args_and_return_value(
    mcp_unit_client: Client[FastMCPTransport],
    mock_transaction_step: MagicMock,
):
    mock_transaction_step.sum_two_floats_with_inputs_and_output.return_value = 5.0

    result = await mcp_unit_client.call_tool(
        "transaction_verification_step__sum_two_floats_with_inputs_and_output",
        {"project_name": "test-project", "field_1": 2, "field_2": 3},
    )
    assert_mcp_response(result, "5.0", has_structure_content=True, structured_result=5.0)
    mock_transaction_step.sum_two_floats_with_inputs_and_output.assert_called_once_with(field_1=2, field_2=3)


async def test_longrunning_transaction_tool(
    mcp_unit_client: Client[FastMCPTransport],
    mock_transaction_step: MagicMock,
):
    mock_transaction_step.lr_get_field_1_and_2_and_set_the_sum_in_result.return_value = None

    result = await mcp_unit_client.call_tool(
        "transaction_verification_step__lr_get_field_1_and_2_and_set_the_sum_in_result",
        {"project_name": "test-project"},
    )
    assert_no_mcp_response(result)
    mock_transaction_step.lr_get_field_1_and_2_and_set_the_sum_in_result.assert_called_once_with()


async def test_longrunning_transaction_tool_with_custom_args_and_return_value(
    mcp_unit_client: Client[FastMCPTransport],
    mock_transaction_step: MagicMock,
    mocker: pytest_mock.MockerFixture,
):
    mock_transaction_step.lr_sum_two_floats_with_inputs_and_output.return_value = None

    result = await mcp_unit_client.call_tool(
        "transaction_verification_step__lr_sum_two_floats_with_inputs_and_output",
        {"project_name": "test-project", "field_1": 2, "field_2": 3},
    )
    assert_no_mcp_response(result)
    mock_transaction_step.lr_sum_two_floats_with_inputs_and_output.assert_called_once_with(field_1=2, field_2=3)

    mocker.patch.object(LongRunning, "get_state", autospec=True, return_value=MagicMock(status=MethodStatus.Running))
    mocker.patch.object(LongRunning, "wait", autospec=True, return_value=5.0)

    result = await mcp_unit_client.call_tool(
        "wait_for_longrunning_transaction",
        {
            "project_name": "test-project",
            "step_name": "transaction_verification_step",
            "transaction_name": "lr_sum_two_floats_with_inputs_and_output",
        },
    )
    assert_mcp_response(result, "5.0", has_structure_content=True, structured_result=5.0)
