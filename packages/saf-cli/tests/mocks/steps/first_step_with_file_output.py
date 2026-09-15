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

"""Backend of job submission step."""

from ansys.saf.glow.solution import NO_ENTITY, EntityHandle, StepModel, StepSpec, transaction


class FirstStep(StepModel):
    """HPS job submission step model for executing jobs on HPS."""

    first_arg: float = 0
    second_arg: float = 0
    result: float = 0
    result_file: EntityHandle = NO_ENTITY

    @transaction(self=StepSpec(upload=["result", "result_file"], download=["first_arg", "second_arg"]))
    def calculate(self) -> None:
        self.result = self.first_arg + self.second_arg
        self.result_file = self.storage_scope.store_stream(str(self.result).encode("utf-8"))
