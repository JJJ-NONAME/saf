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

from time import sleep

from ansys.saf.glow.solution import (
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    create_instance,
    instance,
    long_running,
    transaction,
)
from tests.mocks.instance_managers.mock_product_manager import MockGrpcProductInstanceManager


class AsyncInstanceStep(StepModel):
    @transaction(self=StepSpec())
    @create_instance("x_y", MockGrpcProductInstanceManager)
    def create(self, x_y: MockGrpcProductInstanceManager) -> None:
        x_y.initialize()

    @transaction(self=StepSpec())
    @instance("x_y")
    @long_running
    def long_method_a(self, x_y: MockGrpcProductInstanceManager) -> None:
        sleep(10)

    @transaction(self=StepSpec())
    @instance("x_y")
    @long_running
    def long_method_b(self, x_y: MockGrpcProductInstanceManager) -> None:
        sleep(10)

    @transaction(self=StepSpec())
    @create_instance("a_b", MockGrpcProductInstanceManager)
    def alone(self, a_b: MockGrpcProductInstanceManager) -> None:
        a_b.initialize()


class AsyncInstanceSteps(StepsModel):
    instance_step: AsyncInstanceStep


class AsyncInstancesSolution(Solution):
    display_name: str = "instances"
    steps: AsyncInstanceSteps
