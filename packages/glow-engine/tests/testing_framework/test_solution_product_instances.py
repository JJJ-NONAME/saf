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
import uuid

import pytest
import pytest_mock

from ansys.saf.glow._testing.solution import NotServiceNameAttrFoundError, NotVersionArgFoundError
from ansys.saf.glow.client import BadRequestException, InternalSolutionException
from tests.mocks.instance_managers.mock_product_manager import (
    MockGrpcProductInstanceManager,
    MockHttpNoServiceNameProductInstanceManager,
    MockHttpNoVersionArgProductInstanceManager,
    MockHttpProductInstanceManager,
    MockTcpProductInstanceManager,
)
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution

pytestmark = [pytest.mark.usefixtures("mock_product_instance", "set_solution_env_vars")]
CUSTOM_MANAGERS_MODULE = "tests.mocks.instance_managers.mock_product_manager"


class MockCustomDesign:
    def GetName(self) -> str:  # noqa: N802
        return "fake_design_name"


class MockCustomProject:
    def GetActiveDesign(self):  # noqa: N802
        return MockCustomDesign()


class MockCustomDesktop:
    def GetActiveProject(self):  # noqa: N802
        return MockCustomProject()


class MyMockCustomClient:
    def __init__(self):
        self._the_property = "2024.2"

    @property
    def the_property(self) -> str:
        return self._the_property

    @the_property.setter
    def the_property(self, value: str) -> None:
        self._the_property = value

    def process_input_file(self, input_file: str) -> str:
        return Path(input_file).read_text() + " [PROCESSED]"

    @property
    def odesktop(self):
        return MockCustomDesktop()


class MyMockCustomClient2(MyMockCustomClient):
    @property
    def the_properties(self) -> list[str]:
        return ["file1.txt", "file2.txt"]


@pytest.mark.usefixtures("mock_product_instance")
@pytest.mark.parametrize(
    "mock_product_instance",
    [
        {f"{CUSTOM_MANAGERS_MODULE}.MockHttpProductInstanceManager": MyMockCustomClient},
        {MockHttpProductInstanceManager: MyMockCustomClient2},
    ],
    ids=["module_str", "class"],
    indirect=True,
)
class TestSharedProductInstance:
    def test_create_and_use_product_instance(self, client_project: EndToEndSolution):
        http_step = client_project.steps.custom_http_shared_instance_step
        http_step.initialize_custom_http_product_instance()
        http_step.retrieve_value_custom_http_product_instance()
        assert http_step.value == "2024.2"

    def test_create_and_use_product_instance_in_same_transaction(self, client_project: EndToEndSolution):
        http_step = client_project.steps.custom_http_shared_instance_step
        http_step.initialize_custom_http_product_instance_and_use()
        assert http_step.value == "2024.2"

    def test_use_product_instance_before_creation(self, client_project: EndToEndSolution):
        http_step = client_project.steps.custom_http_shared_instance_step
        error_msg = (
            "The method has been called out of sequence. "
            "A shared product instance that this method uses has not been initialized."
        )
        with pytest.raises(BadRequestException, match=error_msg):
            http_step.retrieve_value_custom_http_product_instance()

    def test_use_product_instance_after_shutdown(self, client_project: EndToEndSolution):
        http_step = client_project.steps.custom_http_shared_instance_step
        http_step.initialize_custom_http_product_instance()
        http_step.retrieve_value_custom_http_product_instance()
        assert http_step.value == "2024.2"
        http_step.shutdown_custom_http_product_instance()
        error_msg = (
            "The method has been called out of sequence. "
            "A shared product instance that this method uses has not been initialized."
        )
        with pytest.raises(BadRequestException, match=error_msg):
            http_step.retrieve_value_custom_http_product_instance()

    def test_use_product_files(self, client_project: EndToEndSolution):
        http_step = client_project.steps.custom_http_shared_instance_step
        random_input_data = str(uuid.uuid4())
        http_step.initialize_custom_http_product_instance()
        http_step.input_file = client_project.storage_scope.store_stream(
            random_input_data.encode(),
        )
        http_step.use_product_files_custom_http_product_instance()
        assert client_project.storage_scope.get_text(http_step.output_file) == f"{random_input_data} [PROCESSED]"

    def test_create_and_use_product_instance_using_long_running_transactions(self, client_project: EndToEndSolution):
        http_step = client_project.steps.custom_http_shared_instance_step
        http_step.initialize_custom_http_product_instance().wait()
        http_step.retrieve_value_custom_http_product_instance_long_running().wait()
        assert http_step.value == "2024.2"

    def test_use_nested_objects_in_product_client(self, client_project: EndToEndSolution):
        http_step = client_project.steps.custom_http_shared_instance_step
        http_step.initialize_custom_http_product_instance()
        assert http_step.retrieve_nested_value_custom_http_product_instance() == "fake_design_name"


@pytest.mark.parametrize(
    "mock_product_instance",
    [
        {f"{CUSTOM_MANAGERS_MODULE}.MockHttpProductInstanceManager": MyMockCustomClient},
        {MockHttpProductInstanceManager: MyMockCustomClient2},
    ],
    ids=["module_str", "class"],
    indirect=True,
)
class TestUnsharedProductInstance:
    def test_use_unshared_product_instance(self, client_project: EndToEndSolution):
        unshared_step = client_project.steps.custom_unshared_instance_step
        unshared_step.assign_value_from_unshared_custom_http_product_instance()
        assert unshared_step.value == "2024.2"

    def test_use_unshared_product_files(self, client_project: EndToEndSolution):
        unshared_step = client_project.steps.custom_unshared_instance_step
        random_input_data = str(uuid.uuid4())
        unshared_step.input_file = client_project.storage_scope.store_stream(
            random_input_data.encode(),
        )
        unshared_step.use_product_files_with_unshared()
        assert client_project.storage_scope.get_text(unshared_step.output_file) == f"{random_input_data} [PROCESSED]"


@pytest.mark.parametrize(
    "mock_product_instance",
    [
        {
            f"{CUSTOM_MANAGERS_MODULE}.MockHttpProductInstanceManager": MyMockCustomClient,
            f"{CUSTOM_MANAGERS_MODULE}.MockGrpcProductInstanceManager": MyMockCustomClient2,
        },
        {
            MockHttpProductInstanceManager: MyMockCustomClient,
            MockGrpcProductInstanceManager: MyMockCustomClient2,
        },
    ],
    ids=["module_str", "class"],
    indirect=True,
)
def test_create_and_use_two_different_instances_in_same_test(client_project: EndToEndSolution):
    http_step = client_project.steps.custom_http_shared_instance_step
    grpc_step = client_project.steps.custom_grpc_shared_instance_step
    http_step.initialize_custom_http_product_instance_and_use()
    assert http_step.value == "2024.2"
    assert grpc_step.initialize_and_retrieve_properties_custom_grpc_product_instance() == ["file1.txt", "file2.txt"]


@pytest.mark.parametrize(
    "mock_product_instance",
    [
        {f"{CUSTOM_MANAGERS_MODULE}.MockHttpProductInstanceManager": MyMockCustomClient},
        {MockHttpProductInstanceManager: MyMockCustomClient},
    ],
    ids=["module_str", "class"],
    indirect=True,
)
def test_http_product_instance(client_project: EndToEndSolution):
    http_step = client_project.steps.custom_http_shared_instance_step
    http_step.initialize_custom_http_product_instance_and_use()
    assert http_step.value == "2024.2"


@pytest.mark.parametrize(
    "mock_product_instance",
    [
        {f"{CUSTOM_MANAGERS_MODULE}.MockGrpcProductInstanceManager": MyMockCustomClient},
        {MockGrpcProductInstanceManager: MyMockCustomClient},
    ],
    ids=["module_str", "class"],
    indirect=True,
)
def test_grpc_product_instance(client_project: EndToEndSolution):
    grpc_step = client_project.steps.custom_grpc_shared_instance_step
    grpc_step.initialize_custom_grpc_product_instance_sync()
    grpc_step.retrieve_value_custom_grpc_product_instance()
    assert grpc_step.value == "2024.2"


@pytest.mark.parametrize(
    "mock_product_instance",
    [
        {f"{CUSTOM_MANAGERS_MODULE}.MockTcpProductInstanceManager": MyMockCustomClient},
        {MockTcpProductInstanceManager: MyMockCustomClient},
    ],
    ids=["module_str", "class"],
    indirect=True,
)
def test_tcp_product_instance(client_project: EndToEndSolution):
    tcp_step = client_project.steps.custom_tcp_shared_instance_step
    tcp_step.initialize_custom_tcp_product_instance()
    tcp_step.retrieve_value_custom_tcp_product_instance()
    assert tcp_step.value == "2024.2"


@pytest.mark.parametrize(
    "mock_product_instance",
    [
        {f"{CUSTOM_MANAGERS_MODULE}.MockHttpProductInstanceManager": MyMockCustomClient},
        {MockHttpProductInstanceManager: MyMockCustomClient},
    ],
    ids=["module_str", "class"],
    indirect=True,
)
@pytest.mark.parametrize("version", [None, "1", "2", "5"])
@pytest.mark.parametrize("using_kwarg", [True, False], ids=["implicit", "explicit"])
def test_create_shared_with_different_versions(
    client_project: EndToEndSolution,
    version: str | None,
    using_kwarg: bool,
    is_msg_in_logs: Callable[[str], bool],
):
    http_step = client_project.steps.custom_http_shared_instance_step
    if version != "5":
        expected_version = version if version else "222"
        assert (
            http_step.launch_shared_and_retrieve_version_custom_http_product_instance(
                version=version,
                using_kwarg=using_kwarg,
            )
            == expected_version
        )
    else:
        error_msg = (
            "The product instance system does not support custom-http-product in version 5. "
            "Available versions: 1, 2, 222."
        )
        with pytest.raises(InternalSolutionException):
            http_step.launch_shared_and_retrieve_version_custom_http_product_instance(
                version=version,
                using_kwarg=using_kwarg,
            )
        assert is_msg_in_logs(error_msg)


@pytest.mark.parametrize(
    "mock_product_instance",
    [
        {f"{CUSTOM_MANAGERS_MODULE}.MockHttpProductInstanceManager": MyMockCustomClient},
        {MockHttpProductInstanceManager: MyMockCustomClient},
    ],
    ids=["module_str", "class"],
    indirect=True,
)
@pytest.mark.parametrize("version", [None, "1", "2", "5"])
def test_create_unshared_with_different_versions(
    client_project: EndToEndSolution,
    version: str | None,
    is_msg_in_logs: Callable[[str], bool],
):
    unshared_step = client_project.steps.custom_unshared_instance_step
    if version != "5":
        expected_version = version if version else "222"
        assert (
            unshared_step.launch_unshared_and_retrieve_version_custom_http_product_instance(
                version=version,
            )
            == expected_version
        )
    else:
        error_msg = (
            "The product instance system does not support custom-http-product in version 5. "
            "Available versions: 1, 2, 222."
        )
        with pytest.raises(InternalSolutionException):
            unshared_step.launch_unshared_and_retrieve_version_custom_http_product_instance(
                version=version,
            )
        assert is_msg_in_logs(error_msg)


@pytest.mark.parametrize(
    "mock_product_instance",
    [{f"{CUSTOM_MANAGERS_MODULE}.MockHttpProductInstanceManager": MyMockCustomClient}],
    ids=["module_str"],
    indirect=True,
)
def test_create_shared_with_unsupported_product(
    client_project: EndToEndSolution,
    mocker: pytest_mock.MockerFixture,
    is_msg_in_logs: Callable[[str], bool],
):
    http_step = client_project.steps.custom_http_shared_instance_step
    mocker.patch(
        f"{CUSTOM_MANAGERS_MODULE}.MockHttpProductInstanceManager._instance_manager_impl_type.get_product_name_implement",
        return_value="unsupported_product",
    )
    with pytest.raises(InternalSolutionException):
        http_step.initialize_max_exec_time_custom_http_product_instance()
    assert is_msg_in_logs("No configuration matches product unsupported_product")


@pytest.mark.parametrize(
    "mock_product_instance",
    [{f"{CUSTOM_MANAGERS_MODULE}.MockHttpProductInstanceManager": MyMockCustomClient}],
    ids=["module_str"],
    indirect=True,
)
def test_create_unshared_with_unsupported_product(
    client_project: EndToEndSolution,
    mocker: pytest_mock.MockerFixture,
    is_msg_in_logs: Callable[[str], bool],
):
    unshared_step = client_project.steps.custom_unshared_instance_step
    mocker.patch(
        f"{CUSTOM_MANAGERS_MODULE}.MockHttpProductInstanceManager._instance_manager_impl_type.get_product_name_implement",
        return_value="unsupported_product",
    )
    with pytest.raises(InternalSolutionException):
        unshared_step.use_unshared_custom_product_instance()
    assert is_msg_in_logs("No configuration matches product unsupported_product")


@pytest.mark.parametrize(
    "mock_product_instance",
    [{MockHttpNoVersionArgProductInstanceManager: MyMockCustomClient}],
    ids=["module_str"],
    indirect=True,
)
@pytest.mark.xfail(raises=NotVersionArgFoundError)
def test_create_shared_with_manager_without_version_arg(client_project: EndToEndSolution):
    client_project.steps.custom_http_shared_instance_step.launch_and_use_http_product_without_version_arg()


@pytest.mark.parametrize(
    "mock_product_instance",
    [{MockHttpNoServiceNameProductInstanceManager: MyMockCustomClient}],
    ids=["module_str"],
    indirect=True,
)
@pytest.mark.xfail(raises=NotServiceNameAttrFoundError)
def test_create_shared_with_manager_without_service_name(client_project: EndToEndSolution):
    client_project.steps.custom_http_shared_instance_step.launch_and_use_http_product_without_service_name()
