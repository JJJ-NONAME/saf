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

from typing import Self

from pydantic import model_validator

from ansys.saf.glow.solution import (
    Solution,
    StepModel,
    StepsModel,
)


class CrossFieldValidationStep(StepModel):
    """A step for testing cross field validation."""

    flag_a: bool = False
    flag_b: bool = False
    flag_c: bool = False

    @model_validator(mode="after")
    def validate_flags(self) -> Self:
        if self.flag_a and self.flag_b:
            raise ValueError("both flag_a and flag_b are set")
        if self.flag_c:
            raise ValueError("flag_c is set")
        return self


class Steps(StepsModel):
    cross_field_validation_step: CrossFieldValidationStep


class CrossFieldValidationSolution(Solution):
    display_name: str = "Cross Field Validation Solution"
    steps: Steps
