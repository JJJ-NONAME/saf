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

from pydantic import field_validator

from ansys.saf.glow.solution import (
    Solution,
    SolutionConfiguration,
    StepModel,
    StepsModel,
    StepSpec,
    transaction,
)


class NotDefinedSolutionConfiguration(SolutionConfiguration):
    solution_schema_version: int = 1
    my_field: int = 0
    my_validated_field: str = "a"

    @field_validator("my_validated_field")
    @classmethod
    def validate_my_validated_field(cls, v: str) -> str:
        if not v.startswith("a"):
            raise ValueError("Field 'my_validated_field' must start with 'a'.")
        return v


class NotDefinedSolutionConfigurationStep(StepModel):
    @transaction(self=StepSpec())
    def read_extended_solution_configuration(self, my_config: NotDefinedSolutionConfiguration) -> None:
        print(my_config)


class Steps(StepsModel):
    not_defined_solution_configuration_step: NotDefinedSolutionConfigurationStep


class NotDefinedSolutionConfigurationSolution(Solution):
    display_name: str = "NotDefinedSolutionConfiguration"
    steps: Steps
