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
    instance,
    transaction,
)
from tests.mocks.instance_managers.empty_instance_manager import EmptyInstanceManager


class MyStep(StepModel):
    @transaction()
    @create_instance("x", EmptyInstanceManager)
    def create(self, x: EmptyInstanceManager) -> None:
        x.initialize()

    # the following definition is incorrect
    # because the transaction decorator appears after the instance decorator
    @instance("x")  # type: ignore
    @transaction()
    def gotcha(self, x: EmptyInstanceManager) -> None:
        x.instance.change_state()


class Steps(StepsModel):
    my_step: MyStep


class MethodInstanceBeforeTransaction(Solution):
    display_name: str = "Method: @instance before @transaction"
    steps: Steps
