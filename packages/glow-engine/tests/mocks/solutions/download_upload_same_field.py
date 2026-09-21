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

from ansys.saf.glow.solution import Solution, StepModel, StepsModel, StepSpec, transaction


class AStep(StepModel):
    """This is a step for testing purpose."""

    a1: int = 99

    @transaction(self=StepSpec(download=["a1"], upload=["a1"]))
    def a_method(self) -> None: ...


class Steps(StepsModel):
    a_step: AStep


class DownloadUploadSameFieldSolution(Solution):
    display_name: str = "Download Upload Same Field"
    steps: Steps
