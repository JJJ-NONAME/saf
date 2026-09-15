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
from typing import TypeVar
from unittest.mock import MagicMock

import pytest

from ansys.saf.glow._core.instance.identification import (
    AbstractInstanceIdentificationClient,
    CreateInstanceRecord,
    InstanceRecord,
    UpdateInstanceRecord,
)
from ansys.saf.glow._core.instance.manager import InstanceManager, InstanceManagerBase
from ansys.saf.glow._core.instance.recoverystate import RecoveryStateInfo, TRecoveryStateInfo
from ansys.saf.glow._executor.local import transaction_local
from tests.mocks.pim.mock_multiple_version_pim import (
    EXPECTED_PRODUCT_NAME as MULTIPLE_VERSION_EXPECTED_PRODUCT_NAME,
)
from tests.mocks.pim.mock_multiple_version_pim import (
    MockPimMultipleVersionClientFactory,
)
from tests.mocks.pim.mock_pim import MockProductInstanceServiceIdentifiers
from tests.mocks.pim.mock_version_pim import (
    MockPimServiceIdentifiers,
    MockPimVersionClient,
    MockPimVersionClientFactory,
)


@pytest.fixture
def mock_transaction_local(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    method_dir = tmp_path_factory.mktemp("method")
    monkeypatch.setattr(transaction_local, "project_directory", Path(), raising=False)
    monkeypatch.setattr(transaction_local, "instance_system_factory", MagicMock(), raising=False)
    monkeypatch.setattr(transaction_local, "settings", MagicMock(), raising=False)
    monkeypatch.setattr(transaction_local, "project_display_name", "project_name", raising=False)
    return method_dir


class MockInstanceClient:
    def do_something(self) -> None:
        pass


T = TypeVar("T")


class NotImplementedIdentificationClient(AbstractInstanceIdentificationClient[TRecoveryStateInfo]):
    def get(self) -> InstanceRecord[TRecoveryStateInfo] | None:
        raise NotImplementedError()

    def add(self, instance_record: CreateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]:
        raise NotImplementedError()

    def update(self, instance_record: UpdateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()


class NotImplementedInstanceManagerBase(InstanceManagerBase[TRecoveryStateInfo]):
    def save_state_implement(self) -> None:
        raise NotImplementedError()

    def load_state_implement(self) -> None:
        raise NotImplementedError()

    def shutdown_implement(self) -> None:
        raise NotImplementedError()

    def get_untyped_client_object_for_base(self, hostname: str, port: int) -> None:
        raise NotImplementedError()

    @classmethod
    def get_product_name_implement(cls) -> str:
        raise NotImplementedError()

    def close_client(self) -> None:
        raise NotImplementedError()


class NotImplementedInstanceManager(InstanceManager[T, TRecoveryStateInfo]):
    def save_state_implement(self) -> None:
        raise NotImplementedError()

    def load_state_implement(self) -> None:
        raise NotImplementedError()

    def shutdown_implement(self) -> None:
        raise NotImplementedError()

    def get_client_object_implement(self, hostname: str, port: int) -> T:
        raise NotImplementedError()

    def close_client_object_implement(self) -> None:
        raise NotImplementedError()

    @classmethod
    def get_product_name_implement(cls) -> str:
        raise NotImplementedError()


class MockInstanceManager(NotImplementedInstanceManager[MockInstanceClient, RecoveryStateInfo]):
    recovery_state_info_type = RecoveryStateInfo

    def get_client_object_implement(self, hostname: str, port: int) -> MockInstanceClient:
        return MockInstanceClient()

    @classmethod
    def get_product_name_implement(cls) -> str:
        return MockProductInstanceServiceIdentifiers.expected_product_name


class MockIdClientNoPrexistingRecord(NotImplementedIdentificationClient[TRecoveryStateInfo]):
    def __init__(self) -> None:
        self._instance_record: InstanceRecord[TRecoveryStateInfo] | None = None

    def get(self) -> InstanceRecord[TRecoveryStateInfo] | None:
        return self._instance_record

    def add(self, instance_record: CreateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]:
        assert instance_record.pim_name == MockProductInstanceServiceIdentifiers.expected_pim_instance_name
        assert instance_record.service_name == MockProductInstanceServiceIdentifiers.expected_service_name
        assert instance_record.product_version == MockProductInstanceServiceIdentifiers.expected_version
        self._record_has_been_added = True
        record = InstanceRecord[TRecoveryStateInfo].model_validate(
            {
                **instance_record.model_dump(),
            },
        )
        self._instance_record = record
        return record

    @property
    def record_has_been_added(self) -> bool:
        return self._instance_record is not None


@pytest.mark.usefixtures("mock_transaction_local")
def test_instance_manager_product_version_property_returned_passed_to_pim_and_stored_as_expected_for_new_instance(
    mock_pim_version_client_factory: MockPimVersionClientFactory,
    monkeypatch: pytest.MonkeyPatch,
):
    version = "VERSION"

    def mock_add(instance_record: CreateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]:
        assert instance_record.pim_name == MockPimServiceIdentifiers.expected_pim_instance_name
        assert instance_record.service_name == MockPimServiceIdentifiers.expected_service_name
        assert instance_record.product_version == version
        return InstanceRecord[TRecoveryStateInfo].model_validate(
            {
                **instance_record.model_dump(),
            },
        )

    id_client = MockIdClientNoPrexistingRecord[RecoveryStateInfo]()
    monkeypatch.setattr(id_client, "add", mock_add)
    monkeypatch.setattr(transaction_local, "instance_system_factory", mock_pim_version_client_factory, raising=False)
    monkeypatch.setattr(transaction_local, "multiplexor_storage_factory", MagicMock(), raising=False)
    instance_manager = MockInstanceManager(_instance_identification=id_client)
    instance_manager._product_instance_system.set_expected_required_version(version)  # type: ignore

    # WHEN - initializing instance service
    instance_manager.initialize_service(MockPimServiceIdentifiers.expected_service_name, version)

    # THEN - instance manager has the correct version
    assert instance_manager.product_version == version


@pytest.mark.usefixtures("mock_transaction_local")
def test_instance_manager_unspecified_product_version_passed_to_pim_actual_version_and_stored_for_new_instance(
    mock_pim_version_client_factory: MockPimVersionClientFactory,
    monkeypatch: pytest.MonkeyPatch,
):
    def mock_add(instance_record: CreateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]:
        assert instance_record.pim_name == MockPimServiceIdentifiers.expected_pim_instance_name
        assert instance_record.service_name == MockPimServiceIdentifiers.expected_service_name
        assert instance_record.product_version == MockPimServiceIdentifiers.expected_version
        return InstanceRecord[TRecoveryStateInfo].model_validate(
            {
                **instance_record.model_dump(),
            },
        )

    def mock_get_product_name_implement() -> str:
        return MockPimServiceIdentifiers.expected_product_name

    MockIdClientNoPrexistingRecord.get_product_name_implement = mock_get_product_name_implement  # type: ignore
    id_client = MockIdClientNoPrexistingRecord[RecoveryStateInfo]()
    monkeypatch.setattr(id_client, "add", mock_add)
    monkeypatch.setattr(transaction_local, "instance_system_factory", mock_pim_version_client_factory, raising=False)
    monkeypatch.setattr(transaction_local, "multiplexor_storage_factory", MagicMock(), raising=False)
    instance_manager = MockInstanceManager(_instance_identification=id_client)
    instance_manager._product_instance_system.set_expected_required_version(None)  # type: ignore
    # WHEN - initializing instance service without specifying version
    instance_manager.initialize_service(MockPimServiceIdentifiers.expected_service_name)
    # THEN - instance manager has the correct version
    assert instance_manager.product_version == MockPimServiceIdentifiers.expected_version


@pytest.mark.usefixtures("mock_transaction_local")
def test_instance_manager_product_version_property_returned_and_fetched_as_expected_for_existing_instance(
    monkeypatch: pytest.MonkeyPatch,
    mock_pim_version_client: MockPimVersionClient,
    tmp_path: Path,
):
    # GIVEN - environment where a previous instance recorded
    class MockIdClientPrexistingRecord(NotImplementedIdentificationClient[TRecoveryStateInfo]):
        def get(self) -> InstanceRecord[TRecoveryStateInfo] | None:
            return InstanceRecord[TRecoveryStateInfo](
                name="projects/fake/url",
                pim_name=MockPimServiceIdentifiers.expected_pim_instance_name,
                service_name=MockPimServiceIdentifiers.expected_service_name,
                product_version=MockPimServiceIdentifiers.expected_version,
            )

    id_client = MockIdClientPrexistingRecord[RecoveryStateInfo]()
    monkeypatch.setattr(transaction_local, "project_directory", tmp_path / "project_id", raising=False)
    monkeypatch.setattr(transaction_local, "multiplexor_storage_factory", MagicMock(), raising=False)
    instance_manager = MockInstanceManager(_instance_identification=id_client)
    instance_manager._product_instance_system = mock_pim_version_client  # type: ignore
    instance_manager.reconnect()

    # WHEN - accessing the product version on the manager
    # THEN - the expected version is returned
    assert instance_manager.product_version == MockPimServiceIdentifiers.expected_version


@pytest.mark.usefixtures("mock_transaction_local")
def test_instance_manager_get_versions_method_returns_expected_versions(
    monkeypatch: pytest.MonkeyPatch,
    mock_pim_multiple_version_client_factory: MockPimMultipleVersionClientFactory,
):
    class InstanceManagerUnderTest(NotImplementedInstanceManager[MockInstanceClient, TRecoveryStateInfo]):
        @classmethod
        def get_product_name_implement(cls) -> str:
            return MULTIPLE_VERSION_EXPECTED_PRODUCT_NAME

    monkeypatch.setattr(
        transaction_local,
        "instance_system_factory",
        mock_pim_multiple_version_client_factory,
        raising=False,
    )
    assert set(InstanceManagerUnderTest.get_versions()) == {"1", "2"}
