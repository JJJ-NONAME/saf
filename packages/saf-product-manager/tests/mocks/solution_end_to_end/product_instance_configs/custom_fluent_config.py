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

from ansys.saf.product_configuration.fluent import (
    Fluent2DDPSolverInstanceConfiguration,
    Fluent2DDPSolverInstanceVersionConfiguration,
)
from ansys.saf.product_configuration.interfaces import IProductInstanceVersionConfiguration


class CustomFluent2DDPSolverInstanceVersionConfiguration(Fluent2DDPSolverInstanceVersionConfiguration):
    @property
    def execution_command(self) -> str:
        return f"{super().execution_command} --my-custom-arg"


# This should inherit from the built-in Fluent2DDPSolverInstanceConfiguration and not from
# IProductInstanceConfiguration. If changed at some point, create another config to keep covering
# this scenario.
class CustomFluent2DDPSolverInstanceConfiguration(Fluent2DDPSolverInstanceConfiguration):
    @property
    def product_name(self) -> str:
        return "custom-fluent-2ddp-solver"

    def get_version_configuration(self, version: str) -> IProductInstanceVersionConfiguration:
        return CustomFluent2DDPSolverInstanceVersionConfiguration(version)
