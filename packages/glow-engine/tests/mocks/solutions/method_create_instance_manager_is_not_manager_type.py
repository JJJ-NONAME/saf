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


class MyStep(StepModel):
    # this method declaration is incorrect because the
    # instance manager type isn't derived from InstanceManager
    @transaction()
    @create_instance("x", int)  # type: ignore
    def create(self, x: int) -> None:
        pass


class Steps(StepsModel):
    my_step: MyStep


class MethodCreateInstanceManagerNotManagerType(Solution):
    display_name: str = "Method: @create_instance - type of the manager isn't derived from InstanceManager"
    steps: Steps
