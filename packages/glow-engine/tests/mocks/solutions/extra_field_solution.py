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

from ansys.saf.glow.solution import Solution, StepModel, StepsModel


class ExtraFieldStep(StepModel):
    """This is a step for testing purpose."""

    x: int = 99


class Steps(StepsModel):
    extra_field_step: ExtraFieldStep


class ExtraFieldSolution(Solution):
    display_name: str = "Extra Field"
    steps: Steps
    extra_field: int = 1
