# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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
from collections.abc import Callable
from pathlib import Path

import pytest

from ansys.saf.glow.client import BadRequestException, InternalSolutionException, LongRunning
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution
from tests.mocks.solution_end_to_end.solution.transaction_verification_step import (
    LOGGING_DEBUG_TESTING_STRING,
    LOGGING_WARNING_TESTING_STRING,
    CustomTypeABC,
    CustomTypeXYZ,
)

pytestmark = pytest.mark.usefixtures("set_solution_env_vars")


def test_solution(client_project: EndToEndSolution, project_display_name: str):
    assert client_project.project_display_name == project_display_name


def test_set_and_retrieve_basic_step_fields(client_project: EndToEndSolution):
    # retrieve step field
    assert client_project.steps.transaction_verification_step.field_1 == 0
    assert client_project.steps.transaction_verification_step.get_fields(["field_2"]) == {"field_2": 0}

    # set step field
    client_project.steps.transaction_verification_step.set_fields({"field_1": 1.0})
    client_project.steps.transaction_verification_step.field_2 = 1.0


def test_sync_transactions(client_project: EndToEndSolution):
    # call transaction that downloads and uploads fields
    assert (
        client_project.steps.transaction_verification_step.get_method_state(
            "get_field_1_and_2_and_set_the_sum_in_result",
        ).status
        == "run-required"
    )
    client_project.steps.transaction_verification_step.set_fields({"field_1": 1.0, "field_2": 2.0})
    assert client_project.steps.transaction_verification_step.result == 0
    client_project.steps.transaction_verification_step.get_field_1_and_2_and_set_the_sum_in_result()
    assert client_project.steps.transaction_verification_step.result == 3.0
    assert (
        client_project.steps.transaction_verification_step.get_method_state(
            "get_field_1_and_2_and_set_the_sum_in_result",
        ).status
        == "completed"
    )

    # call transaction with inputs and outputs
    assert (
        client_project.steps.transaction_verification_step.sum_two_floats_with_inputs_and_output(
            field_1=2.0,
            field_2=3.0,
        )
        == 5.0
    )


def test_long_running_transactions(client_project: EndToEndSolution):
    # call long-running transaction that downloads and uploads fields
    client_project.steps.transaction_verification_step.set_fields({"field_1": 1.0, "field_2": 2.0})
    assert (
        client_project.steps.transaction_verification_step.get_method_state(
            "lr_get_field_1_and_2_and_set_the_sum_in_result",
        ).status
        == "run-required"
    )
    assert client_project.steps.transaction_verification_step.result == 0
    method = client_project.steps.transaction_verification_step.lr_get_field_1_and_2_and_set_the_sum_in_result()
    # FIXME: show a long-running transaction running in background and the test advancing doing other things

    assert isinstance(method, LongRunning)
    # method.wait()  No need to call wait() due to the mentioned bug
    assert method.get_state().status == "completed"
    assert method.is_complete()
    assert client_project.steps.transaction_verification_step.result == 3.0
    assert (
        client_project.steps.transaction_verification_step.get_method_state(
            "lr_get_field_1_and_2_and_set_the_sum_in_result",
        ).status
        == "completed"
    )


def test_errors(client_project: EndToEndSolution):
    # set field to invalid value
    with pytest.raises(BadRequestException, match="Input should be a valid number, unable to parse string as a number"):
        client_project.steps.transaction_verification_step.field_1 = "invalid"  # type: ignore
    assert client_project.steps.transaction_verification_step.field_1 == 0

    # call transaction that fails and shows generic error since DEBUG is not enabled
    error_msg = "The solution encountered an internal error and was unable to complete the request."
    with pytest.raises(InternalSolutionException, match=error_msg):
        client_project.steps.transaction_verification_step.read_text_file()
    assert client_project.steps.transaction_verification_step.get_method_state("read_text_file").status == "failed"
    assert (
        str(
            client_project.steps.transaction_verification_step.get_method_state("read_text_file").exception_message,
        ).strip()
        == error_msg
    )


def test_bdm_fields_and_transactions(client_project: EndToEndSolution, project_files_dir: Path):
    # no project files
    assert not list(project_files_dir.rglob("*"))

    # set entityhandle from client
    my_input_file = client_project.storage_scope.get_storage_root() / "my_input_file.txt"
    my_input_file.write_text("This is a test file.")
    client_project.steps.transaction_verification_step.text_file = client_project.storage_scope.store(my_input_file)
    # file is stored in the project files directory
    file_path = next(file for file in project_files_dir.rglob("*") if file.name == "my_input_file.txt")
    assert file_path.is_file()
    assert file_path.read_text() == "This is a test file."

    # call transaction that uses entity handles and retrieve it in the client
    client_project.steps.transaction_verification_step.process_file()
    assert (
        client_project.storage_scope.get_text(client_project.steps.transaction_verification_step.text_file_2)
        == "NOT This is a test file."
    )
    # file is stored in the project files directory
    file_path = next(file for file in project_files_dir.rglob("*") if file.name == "my_second_file.txt")
    assert file_path.is_file()
    assert file_path.read_text() == "NOT This is a test file."


def test_method_assets(client_project: EndToEndSolution):
    # retrieve decrypted within transaction
    client_project.steps.transaction_verification_step.read_asset_file()
    assert client_project.steps.transaction_verification_step.text_content == "AssetFile1"

    # TODO: key and keyless decryption, etc.


def test_custom_object(client_project: EndToEndSolution):
    # set within transaction and retrieve from client
    assert client_project.steps.transaction_verification_step.optional_compound_custom_object is None
    client_project.steps.transaction_verification_step.comp_obj_with_init()
    assert client_project.steps.transaction_verification_step.optional_compound_custom_object == CustomTypeABC(
        a=1,
        b=CustomTypeXYZ(x=1, y=0, z=0),
        c=3,
    )

    # set from client and retrieve from transaction
    client_project.steps.transaction_verification_step.optional_compound_custom_object = CustomTypeABC(
        a=2,
        b=CustomTypeXYZ(x=4, y=0, z=0),
        c=4,
    )
    assert client_project.steps.transaction_verification_step.run_custom_object() == 10.0


@pytest.mark.parametrize("configure_solution", [{"GLOW_DEBUG": "True"}], ids=["with_debug"], indirect=True)
def test_configuring_solution(client_project: EndToEndSolution):
    step = client_project.steps.transaction_verification_step
    # call transaction that fails and we have access to all info since DEBUG is enabled
    error_msg = "accessing storage using NO_ENTITY handle"
    with pytest.raises(InternalSolutionException, match=error_msg):
        step.read_text_file()
    assert step.get_method_state("read_text_file").status == "failed"
    assert step.get_method_state("read_text_file").exception_message == error_msg


def test_accessing_solution_logs(client_project: EndToEndSolution, is_msg_in_logs: Callable[[str], bool]):
    assert not is_msg_in_logs(LOGGING_DEBUG_TESTING_STRING)
    client_project.steps.transaction_verification_step.log_some_debug()
    # can access logs from GLOW framework and from the solution,
    # in different namespaces (ansys.saf.glow vs tests.mocks.solution_end_to_end)
    expected_msg = (
        "DEBUG - ansys.saf.glow._executor.method_runner - "
        "Executing method transaction_verification_step:log_some_debug..."
    )
    assert is_msg_in_logs(expected_msg)
    expected_msg = (
        "DEBUG - tests.mocks.solution_end_to_end.solution.transaction_verification_step - "
        f"{LOGGING_DEBUG_TESTING_STRING}"
    )
    assert is_msg_in_logs(expected_msg)


@pytest.mark.parametrize("solution_logs", ["warning"], indirect=True)
def test_accessing_solution_logs_with_custom_level(
    client_project: EndToEndSolution,
    is_msg_in_logs: Callable[[str], bool],
):
    assert not is_msg_in_logs(LOGGING_DEBUG_TESTING_STRING)
    assert not is_msg_in_logs(LOGGING_WARNING_TESTING_STRING)
    client_project.steps.transaction_verification_step.log_some_debug()
    client_project.steps.transaction_verification_step.log_a_warning()
    # custom level applies to both loggers, ansys.x and root (which includes tests.mocks)
    assert not is_msg_in_logs("Executing method transaction_verification_step:log_some_debug...")
    assert not is_msg_in_logs(LOGGING_DEBUG_TESTING_STRING)
    expected_msg = (
        "WARNING - tests.mocks.solution_end_to_end.solution.transaction_verification_step - "
        f"{LOGGING_WARNING_TESTING_STRING}"
    )
    assert is_msg_in_logs(expected_msg)


@pytest.mark.parametrize("configure_solution", [{"GLOW_DEBUG": "True"}], ids=["with_debug"], indirect=True)
class TestConfiguringSolutionInClass:
    def test_configuring_solution_within_class(self, client_project: EndToEndSolution):
        # call transaction that fails and we have access to all info since DEBUG is enabled
        error_msg = "accessing storage using NO_ENTITY handle"
        with pytest.raises(InternalSolutionException, match=error_msg):
            client_project.steps.transaction_verification_step.read_text_file()
