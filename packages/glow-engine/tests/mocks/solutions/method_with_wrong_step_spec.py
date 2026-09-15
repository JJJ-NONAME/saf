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

from ansys.saf.glow.solution import (  # type ignore
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    transaction,
)


class OtherStep(StepModel):
    """This is a step for testing purpose."""


class MyStep(StepModel):
    """This is a step for testing purpose."""

    @transaction(wrong_step_spec=StepSpec())
    def increment(self, other_step: OtherStep) -> None:
        pass


class Steps(StepsModel):
    my_step: MyStep
    other_step: OtherStep


class MethodWithWrongStepSpec(Solution):
    display_name: str = "Method With Wrong StepSpec"
    steps: Steps
