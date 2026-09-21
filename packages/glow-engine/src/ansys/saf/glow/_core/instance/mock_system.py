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

import contextlib
import logging
import os
from pathlib import Path
import random
import tempfile

from ansys.saf.glow._config.const import GLOW_PRODUCT_HOST
from ansys.saf.glow._core.instance.iinstance_system import (
    GenericProductInstance,
    IProductInstance,
    IProductInstanceService,
    IProductInstanceSystem,
    IProductInstanceSystemFactory,
    IProductInstanceVersionDefinition,
)

logger = logging.getLogger(__name__)


class MockProductInstanceVersionDefinition(IProductInstanceVersionDefinition):
    def __init__(self, product_name: str, product_version: str) -> None:
        self._product_name = product_name
        self._version = product_version

    @property
    def name(self) -> str:
        return f"{self._product_name} : {self._version}"

    @property
    def product_version(self) -> str:
        return self._version


class MockProductInstanceService(IProductInstanceService):
    @property
    def port(self) -> int:
        # TODO: Allow to configure port somehow? always use one randomly?
        return 8080

    @property
    def host(self) -> str:
        return os.getenv(GLOW_PRODUCT_HOST, "localhost")


class MockProductInstance(GenericProductInstance):
    def __init__(self, product_name: str, service_name: str, version: str) -> None:
        self._product_name = product_name
        self._service_name = service_name
        self._version = version
        self._name = (
            f"instances/{self._product_name}__{self._service_name}__{self._version}__{str(random.randint(0, 9999))}"  # noqa: S311 # nosec
        )

    @property
    def _instance_file_path(self) -> Path:
        return Path(tempfile.gettempdir()) / f"glow_mock_product_{self._name.replace('/', '_')}"

    @classmethod
    def from_name(cls, instance_name: str) -> "MockProductInstance":
        product_name, service_name, version, _ = instance_name.removeprefix("instances/").split("__")
        instance = cls(product_name, service_name, version)
        instance._name = instance_name
        if not instance._instance_file_path.is_file():
            raise FileNotFoundError("Instance not found")
        return instance

    @property
    def name(self) -> str:
        return self._name

    @property
    def definition_name(self) -> str:
        return f"definitions/{self._product_name}{self._version}"

    @property
    def version(self) -> str:
        return self._version

    def is_healthy(self) -> bool:
        return True

    def wait_for_ready(self):
        self._instance_file_path.parent.mkdir(parents=True, exist_ok=True)
        self._instance_file_path.touch()

    @property
    def services(self) -> dict[str, IProductInstanceService]:
        return {self._service_name: MockProductInstanceService()}

    def delete(self, missing_ok: bool = False) -> None:
        if not self._instance_file_path.is_file() and not missing_ok:
            raise FileNotFoundError("Instance not found, cannot be deleted.")
        self._instance_file_path.unlink(missing_ok=missing_ok)


class MockSystem(IProductInstanceSystem):
    """Mock implementation of a product instance system for testing and development.

    This is a lightweight mock of a product instance system that simulates the behavior
    of actual systems like PIM (Platform Instance Management) or HPS (High Performance
    Computing Platform Services) without running any real product instances.

    The mock system uses temporary files on the filesystem to track which instances
    are "running". When an instance is created, a file is created in the temporary
    directory to represent its existence. When the instance is deleted, the file is
    removed. This provides a simple way to simulate instance lifecycle management
    without the overhead and complexity of actual product execution.
    """

    def list_definitions(self, product_name: str) -> list[IProductInstanceVersionDefinition]:
        return [
            MockProductInstanceVersionDefinition(product_name, version)
            for version in self._configurations_manager.list_versions(product_name)
        ]

    def create_instance(
        self,
        product_name: str,
        max_execution_time: int,
        product_version: str | None = None,
    ) -> IProductInstance:
        # TODO: Doesn't support max execution time
        product_version, version_configuration = self._configurations_manager.get_version_configuration(
            product_name,
            product_version,
        )
        if not any(product_version == definition.product_version for definition in self.list_definitions(product_name)):
            available_versions = [definition.product_version for definition in self.list_definitions(product_name)]
            raise ValueError(
                f"The product instance system does not support {product_name} in version {product_version}. "
                f"Available versions: {', '.join(available_versions) if available_versions else 'None'}.",
            )

        product_instance = MockProductInstance(product_name, version_configuration.service_name, product_version)
        # TODO: allow an instance to not be healthy?
        product_instance.wait_for_ready()
        return product_instance

    def get_instance(self, instance_name: str) -> IProductInstance | None:
        if not instance_name:
            return None

        instance: MockProductInstance | None = None
        with contextlib.suppress(FileNotFoundError):
            instance = MockProductInstance.from_name(instance_name)
        return instance

    def close(self) -> None:
        return


class MockSystemFactory(IProductInstanceSystemFactory):
    def create_system(self, uri: str) -> MockSystem:
        return MockSystem()
