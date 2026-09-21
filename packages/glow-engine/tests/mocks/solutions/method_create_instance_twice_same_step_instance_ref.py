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
    create_instance,
    transaction,
)
from tests.mocks.instance_managers.empty_instance_manager import EmptyInstanceManager


class MyStep(StepModel):
    # this method declaration is incorrect because there are two
    # references to the other_step.x instance
    @transaction()
    @create_instance("other_step.x", EmptyInstanceManager, identifier="a")
    @create_instance("other_step.x", EmptyInstanceManager, identifier="b")
    def create(self, a: EmptyInstanceManager, b: EmptyInstanceManager) -> None:
        a.initialize()
        b.initialize()


class OtherStep(StepModel):
    pass


class Steps(StepsModel):
    my_step: MyStep
    other_step: OtherStep


class MethodCreateInstanceTwiceSameStepInstanceReference(Solution):
    display_name: str = "Method: @create_instance twice referring to the same instance on another step"
    steps: Steps
