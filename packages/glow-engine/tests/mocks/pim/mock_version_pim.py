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

from types import ModuleType

from ansys.saf.glow._core.instance.iinstance_system import (
    IProductInstance,
    IProductInstanceService,
    IProductInstanceSystem,
    IProductInstanceSystemFactory,
    IProductInstanceVersionDefinition,
)


class MockPimServiceIdentifiers:
    expected_pim_instance_name = "instances/PIM INSTANCE NAME"
    expected_product_name = "PRODUCT NAME"
    expected_service_name = "SERVICE_NAME"
    expected_host_name = "HOSTNAME"
    expected_port = 54321
    expected_definition_name = "DEFINITION NAME"
    expected_version = "VERSION"


class MockPimService(IProductInstanceService):
    @property
    def uri(self) -> str:
        return f"{MockPimServiceIdentifiers.expected_host_name}:{MockPimServiceIdentifiers.expected_port}"

    @property
    def host(self) -> str:
        return MockPimServiceIdentifiers.expected_host_name

    @property
    def port(self) -> int:
        return MockPimServiceIdentifiers.expected_port


class MockPimInstance(IProductInstance):
    def __init__(self, product_version: str) -> None:
        self._product_version = product_version

    @property
    def services(self) -> dict[str, IProductInstanceService]:
        return {MockPimServiceIdentifiers.expected_service_name: MockPimService()}

    def wait_for_ready(self):
        pass

    def is_healthy(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return MockPimServiceIdentifiers.expected_pim_instance_name

    @property
    def definition_name(self) -> str:
        return MockPimServiceIdentifiers.expected_definition_name

    @property
    def version(self) -> str:
        return self._product_version

    def delete(self, missing_ok: bool = False) -> None: ...


class MockPimDefinition(IProductInstanceVersionDefinition):
    @property
    def name(self) -> str:
        return MockPimServiceIdentifiers.expected_definition_name

    @property
    def product_version(self) -> str:
        return MockPimServiceIdentifiers.expected_version


class MockPimVersionClient(IProductInstanceSystem):
    def __init__(self):
        self._expected_required_product_version: str | None = None

    def get_instance(self, instance_name: str) -> MockPimInstance:
        assert instance_name == MockPimServiceIdentifiers.expected_pim_instance_name
        return self._create_instance()

    def set_expected_required_version(self, product_version: str | None = None):
        self._expected_required_product_version = product_version

    def _create_instance(self) -> MockPimInstance:
        version = (
            MockPimServiceIdentifiers.expected_version
            if self._expected_required_product_version is None
            else self._expected_required_product_version
        )
        return MockPimInstance(version)

    def create_instance(
        self,
        product_name: str,
        max_execution_time: int,
        product_version: str | None = None,
    ) -> MockPimInstance:
        assert self._expected_required_product_version == product_version
        return self._create_instance()

    def list_definitions(self, product_name: str) -> list[IProductInstanceVersionDefinition]:
        assert product_name == MockPimServiceIdentifiers.expected_product_name
        return [MockPimDefinition()]

    def load_configurations_from_solution(self, solution_module: ModuleType): ...

    def close(self): ...


class MockPimVersionClientFactory(IProductInstanceSystemFactory):
    def create_system(self, uri: str) -> MockPimVersionClient:
        return MockPimVersionClient()
