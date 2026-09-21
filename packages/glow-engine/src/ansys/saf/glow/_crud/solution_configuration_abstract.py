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

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from ansys.saf.glow._crud.solution_configuration_models import SolutionConfiguration

TSolutionConfig = TypeVar("TSolutionConfig", bound=SolutionConfiguration)


class AbstractSolutionConfigurationCRUD(ABC, Generic[TSolutionConfig]):
    @abstractmethod
    async def initialize_database(self, default_solution_configuration: TSolutionConfig) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def get_solution_configuration(self) -> TSolutionConfig:
        raise NotImplementedError()

    @abstractmethod
    async def modify_solution_configuration(self, solution_configuration_modification: dict[str, Any]) -> None:
        raise NotImplementedError()
