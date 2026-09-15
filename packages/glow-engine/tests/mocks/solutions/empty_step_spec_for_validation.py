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

from ansys.saf.glow.solution import (
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    create_instance,
    instance,
    transaction,
)
from tests.mocks.instance_managers.empty_instance_manager import EmptyInstanceManager


class FirstStep(StepModel):
    result: str = "NOTHING"

    @transaction()
    @create_instance("mock_product", EmptyInstanceManager)
    def initialize(self, mock_product: EmptyInstanceManager) -> None:
        mock_product.initialize()

    @transaction(self=StepSpec(upload=["result"]))
    @instance("mock_product")
    def get_result(self, mock_product: EmptyInstanceManager) -> None:
        pass


class Steps(StepsModel):
    first_step: FirstStep


class EmptySpecSolution(Solution):
    display_name: str = "Simple Instances"
    steps: Steps
