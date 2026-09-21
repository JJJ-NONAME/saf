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
    instance,
    transaction,
)
from tests.mocks.instance_managers.empty_instance_manager import EmptyInstanceManager


class MyStep(StepModel):
    # the following definition is incorrect
    # the instance x is not created
    @transaction()
    @instance("x")
    def use(self, x: EmptyInstanceManager) -> None:
        pass


class Steps(StepsModel):
    my_step: MyStep


class MethodInstanceSaveToNotState(Solution):
    display_name: str = "Method: @instance - there is no matching @create_instance"
    steps: Steps
