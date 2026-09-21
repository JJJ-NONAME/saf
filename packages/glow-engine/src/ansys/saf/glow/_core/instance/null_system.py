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
    IProductInstanceSystem,
    IProductInstanceSystemFactory,
    IProductInstanceVersionDefinition,
)
from ansys.saf.glow._server.exceptions import InternalError


class NullSystem(IProductInstanceSystem):
    """Dummy implementation of a Product Instance System that is used when GLOW_PRODUCT_INSTANCE_SYSTEM_PORT is None"""

    ERROR_MESSAGE: str = (
        "The product instance system is not setup properly. "
        "Make sure that GLOW_PRODUCT_INSTANCE_SYSTEM_PORT env var is pointing to a valid URL"
    )

    def load_configurations_from_solution(self, solution_module: ModuleType): ...

    def list_definitions(self, product_name: str) -> list[IProductInstanceVersionDefinition]:
        raise InternalError(self.ERROR_MESSAGE)

    def create_instance(
        self,
        product_name: str,
        max_execution_time: int,
        product_version: str | None = None,
    ) -> IProductInstance:
        raise InternalError(self.ERROR_MESSAGE)

    def get_instance(self, instance_name: str) -> IProductInstance | None:
        raise InternalError(self.ERROR_MESSAGE)

    def close(self) -> None: ...


class NullSystemFactory(IProductInstanceSystemFactory):
    def create_system(self, uri: str) -> NullSystem:
        return NullSystem()
