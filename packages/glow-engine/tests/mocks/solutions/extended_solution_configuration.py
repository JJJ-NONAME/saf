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

from pathlib import Path
import time
from typing import Any, Self

from pydantic import field_validator, model_validator

from ansys.saf.glow.solution import (
    Solution,
    SolutionConfiguration,
    StepModel,
    StepsModel,
    StepSpec,
    long_running,
    transaction,
)


class ExtendedSolutionConfiguration(SolutionConfiguration):
    solution_schema_version: int = 1
    my_field: int = 0
    my_second_field: str = ""
    my_validated_field: str = "a"
    my_second_validated_field: str = "b"

    @field_validator("my_validated_field")
    @classmethod
    def validate_my_validated_field(cls, v: str) -> str:
        if not v.startswith("a"):
            raise ValueError("Field 'my_validated_field' must start with 'a'.")
        return v

    @model_validator(mode="after")
    def validate_my_second_validated_field(self) -> Self:
        if self.my_second_validated_field == self.my_validated_field:
            raise ValueError("Field 'my_second_validated_field' must be different from 'my_validated_field'.")
        return self


class ExtendedSolutionConfigurationStep(StepModel):
    @transaction(self=StepSpec())
    def read_extended_solution_configuration(self, my_config: ExtendedSolutionConfiguration) -> tuple[str, int]:
        return my_config.__class__.__name__, my_config.my_field

    @transaction(self=StepSpec())
    def change_solution_configuration(self, my_config: ExtendedSolutionConfiguration, my_field: int) -> None:
        my_config.my_field = my_field

    @transaction(self=StepSpec())
    @long_running
    def wait_for_signal_file(self, signal_file: Path, my_config: ExtendedSolutionConfiguration) -> dict[str, Any]:
        signal_file.write_text("inside transaction")
        signal_received = False
        for _ in range(500):
            try:
                signal_received = signal_file.read_text() == "stop"
            except PermissionError:
                continue
            if signal_received:
                return my_config.model_dump()
            time.sleep(0.1)
        raise RuntimeError("Stop signal was not received")


class Steps(StepsModel):
    extended_solution_configuration_step: ExtendedSolutionConfigurationStep


class ExtendedSolutionConfigurationSolution(Solution):
    display_name: str = "ExtendedSolutionConfiguration"
    steps: Steps
    solution_configuration: ExtendedSolutionConfiguration = ExtendedSolutionConfiguration()
