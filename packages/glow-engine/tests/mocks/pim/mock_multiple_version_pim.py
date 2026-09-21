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

EXPECTED_PRODUCT_NAME = "PRODUCT NAME"


class MockPimDefinition(IProductInstanceVersionDefinition):
    def __init__(self, version: str) -> None:
        self._version = version

    @property
    def product_version(self) -> str:
        return self._version

    @property
    def name(self) -> str:
        return EXPECTED_PRODUCT_NAME


class MockPimMultipleVersionInstance(IProductInstance):
    @property
    def services(self) -> dict[str, IProductInstanceService]: ...

    def wait_for_ready(self): ...

    def is_healthy(self) -> bool:
        return True

    @property
    def name(self) -> str: ...

    @property
    def definition_name(self) -> str: ...

    @property
    def version(self) -> str: ...

    def delete(self, missing_ok: bool = False) -> None: ...


class MockPimMultipleVersionClient(IProductInstanceSystem):
    def list_definitions(self, product_name: str) -> list[IProductInstanceVersionDefinition]:
        assert product_name == EXPECTED_PRODUCT_NAME
        return [MockPimDefinition("1"), MockPimDefinition("2")]

    def get_instance(self, instance_name: str) -> MockPimMultipleVersionInstance: ...

    def create_instance(
        self,
        product_name: str,
        max_execution_time: int,
        product_version: str | None = None,
    ) -> MockPimMultipleVersionInstance: ...

    def load_configurations_from_solution(self, solution_module: ModuleType): ...

    def close(self): ...


class MockPimMultipleVersionClientFactory(IProductInstanceSystemFactory):
    def create_system(self, uri: str) -> MockPimMultipleVersionClient:
        return MockPimMultipleVersionClient()
