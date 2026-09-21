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
    SolutionConfiguration,
    StepModel,
    StepsModel,
    StepSpec,
    transaction,
)


class WrongSolutionConfiguration(SolutionConfiguration):
    solution_schema_version: str = "1"  # type: ignore


class WrongSolutionConfigurationStep(StepModel):
    @transaction(self=StepSpec())
    def read_wrong_solution_configuration(self, my_config: WrongSolutionConfiguration) -> None:
        pass


class Steps(StepsModel):
    wrong_solution_configuration_step: WrongSolutionConfigurationStep


class WrongSolutionConfigurationSolution(Solution):
    display_name: str = "WrongSolutionConfiguration"
    steps: Steps
    solution_configuration: WrongSolutionConfiguration = WrongSolutionConfiguration()
