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
from typing import Any

from ansys.saf.glow.solution import (
    Solution,
    SolutionConfiguration,
    StepModel,
    StepsModel,
    StepSpec,
    long_running,
    transaction,
)


class SolutionConfigurationStep(StepModel):
    @transaction(self=StepSpec())
    def read_solution_configuration(self, my_config: SolutionConfiguration) -> str:
        return my_config.__class__.__name__

    @long_running
    @transaction(self=StepSpec())
    def read_solution_configuration_lr(self, my_another_config: SolutionConfiguration) -> str:
        return my_another_config.__class__.__name__

    @transaction(self=StepSpec())
    @long_running
    def wait_for_signal_file(self, signal_file: Path, my_config: SolutionConfiguration) -> dict[str, Any]:
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
    solution_configuration_step: SolutionConfigurationStep


class SolutionConfigurationSolution(Solution):
    display_name: str = "SolutionConfiguration"
    steps: Steps
    solution_configuration: SolutionConfiguration = SolutionConfiguration()
