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
    long_running,
    transaction,
)
from tests.mocks.instance_managers.mock_product_manager import MockGrpcProductInstanceManager


class StepWithInstanceMethod(StepModel):
    @transaction(self=StepSpec())
    @create_instance("x", MockGrpcProductInstanceManager)
    def initialize_x_instance(self, x: MockGrpcProductInstanceManager):
        x.initialize()

    @transaction(self=StepSpec())
    @instance("x")
    def use_instance(self, x: MockGrpcProductInstanceManager) -> None:
        pass

    @transaction(self=StepSpec())
    @long_running
    @instance("x")
    def use_instance_with_long_running(self, x: MockGrpcProductInstanceManager) -> None:
        pass


class Steps(StepsModel):
    my_step: StepWithInstanceMethod


class InstanceMethodWithoutInitializationSolution(Solution):
    display_name: str = "Method: @instance"
    steps: Steps
