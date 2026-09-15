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

import uuid

from pydantic import field_validator

from ansys.saf.glow.solution import (
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    transaction,
)


class FirstStep(StepModel):
    x: int = 88
    my_string: str = "my_string"
    unused_value: float = 2
    str_int: str = "1"

    @field_validator("unused_value")  # type: ignore
    @classmethod
    def must_be_greater_than_0(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"{v} must be greater than 0")
        return v

    @transaction(self=StepSpec(download=["x"], upload=["my_string"]))
    def copy_x_to_string(self) -> None:
        self.my_string = str(self.x)

    @transaction(self=StepSpec(upload=["my_string"]))
    def generate_random_string(self) -> None:
        self.my_string = str(uuid.uuid4())


class SecondStep(StepModel):
    x: int = 88
    my_string: str = "my_string"

    @transaction(self=StepSpec(download=["x"], upload=["my_string"]))
    def copy_x_to_string(self) -> None:
        self.my_string = str(self.x)

    @transaction(self=StepSpec(upload=["my_string"]))
    def generate_random_string(self) -> None:
        self.my_string = str(uuid.uuid4())


class Steps(StepsModel):
    first_step: FirstStep
    second_step: SecondStep


class OriginalSolution(Solution):
    display_name: str = "Original"
    steps: Steps
