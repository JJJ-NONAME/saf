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
    transaction,
)


class MyStep(StepModel):
    """This is a step for testing purpose."""

    @transaction(other_step=StepSpec())
    def increment(self, no_type_hint):  # type: ignore
        pass


class Steps(StepsModel):
    my_step: MyStep


class MethodParamNoTypeHint(Solution):
    display_name: str = "Method Param No Type Hint"
    steps: Steps
