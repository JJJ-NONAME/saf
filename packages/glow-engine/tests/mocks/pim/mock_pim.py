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

import traceback

from ansys.saf.glow._core.instance.iinstance_system import (
    IProductInstance,
    IProductInstanceService,
    IProductInstanceSystem,
    IProductInstanceVersionDefinition,
)


class MockProductInstanceServiceIdentifiers:
    expected_pim_instance_name = "instances/PIM INSTANCE NAME"
    expected_product_name = "PRODUCT NAME"
    expected_service_name = "SERVICE_NAME"
    expected_host_name = "HOSTNAME"
    expected_port = 54321
    expected_version = "PRODUCT VERSION"
    expected_definition_name = "DEFINITION NAME"
    existing_pim_instance_name = "instances/OLD PIM INSTANCE NAME"
    existing_port = 99999


class MockProductInstanceService(IProductInstanceService):
    def __init__(self, port: int) -> None:
        self._port = port

    @property
    def host(self) -> str:
        return MockProductInstanceServiceIdentifiers.expected_host_name

    @property
    def port(self) -> int:
        return self._port


class MockProductInstance(IProductInstance):
    def __init__(self, name: str, port: int, version: str) -> None:
        self._ready = port == MockProductInstanceServiceIdentifiers.existing_port
        self._port = port
        self._version = version
        self._name = name
        self._deleted = False
        self._delete_point: list[str] = []

    @property
    def deleted(self) -> bool:
        return self._deleted

    @property
    def ready(self) -> bool:
        return self._ready

    def is_healthy(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return self._name

    def wait_for_ready(self) -> None:
        self._ready = True

    def delete(self, missing_ok: bool = False) -> None:
        assert not self._deleted, f"instance previously deleted at {self._delete_point}"
        assert self._ready
        assert self._port == MockProductInstanceServiceIdentifiers.existing_port
        self._ready = False
        self._deleted = True
        self._delete_point = traceback.format_stack()

    @property
    def services(self) -> dict[str, IProductInstanceService]:
        assert self._ready
        return {MockProductInstanceServiceIdentifiers.expected_service_name: MockProductInstanceService(self._port)}

    @property
    def definition_name(self) -> str:
        return MockProductInstanceServiceIdentifiers.expected_definition_name

    @property
    def version(self) -> str:
        return self._version


class MockProductDefinition:
    @property
    def name(self) -> str:
        return MockProductInstanceServiceIdentifiers.expected_definition_name

    @property
    def product_version(self) -> str:
        return MockProductInstanceServiceIdentifiers.expected_version


class MockProductInstanceSystem(IProductInstanceSystem):
    def __init__(self):
        self._instance_created = False
        self._existing_instance = MockProductInstance(
            MockProductInstanceServiceIdentifiers.existing_pim_instance_name,
            MockProductInstanceServiceIdentifiers.existing_port,
            MockProductInstanceServiceIdentifiers.expected_version,
        )
        self._expected_instance = MockProductInstance(
            MockProductInstanceServiceIdentifiers.expected_pim_instance_name,
            MockProductInstanceServiceIdentifiers.expected_port,
            MockProductInstanceServiceIdentifiers.expected_version,
        )
        self._max_execution_time = None
        self.return_existing = True

    def create_instance(
        self,
        product_name: str,
        max_execution_time: int,
        product_version: str | None = None,
    ) -> MockProductInstance:
        assert product_version is None
        assert product_name == MockProductInstanceServiceIdentifiers.expected_product_name
        self._instance_created = True
        self._max_execution_time = max_execution_time

        try:
            self._expected_instance.wait_for_ready()
        except Exception:
            try:
                self._expected_instance.delete()
            finally:
                raise

        return self._expected_instance

    def get_instance(self, instance_name: str) -> MockProductInstance | None:
        if self.return_existing:
            assert instance_name == MockProductInstanceServiceIdentifiers.existing_pim_instance_name
            return self._existing_instance
        else:
            assert instance_name == MockProductInstanceServiceIdentifiers.expected_pim_instance_name
            return self._expected_instance

    @property
    def instance_created(self) -> bool:
        return self._instance_created

    @property
    def max_execution_time(self) -> int | None:
        return self._max_execution_time

    def port_is_serviced(self, port: int) -> bool:
        if port == MockProductInstanceServiceIdentifiers.existing_port:
            assert self._existing_instance is not None
            return not self._existing_instance.deleted

        if port == MockProductInstanceServiceIdentifiers.expected_port:
            return self.instance_created and self._expected_instance.ready and not self._expected_instance.deleted

        return False

    def list_definitions(self, product_name: str) -> list[IProductInstanceVersionDefinition]:
        assert product_name == MockProductInstanceServiceIdentifiers.expected_product_name
        return [MockProductDefinition()]

    def delete_existing_instance(self) -> None:
        assert self._existing_instance is not None
        self._existing_instance.delete()
        self._existing_instance = None

    def close(self): ...
