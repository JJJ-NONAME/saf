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

import logging
import os
from pathlib import Path

from ansys.saf.glow.solution import Solution, StepModel, StepsModel, StepSpec, long_running, transaction
from ansys.saf.glow.solution.hps import HpsComputeResourceSet, HpsParametricStudyProject

logger = logging.getLogger(__name__)


class AStep(StepModel):
    @transaction(self=StepSpec())
    def set_env_vars(self) -> None:
        os.environ["GLOW_HPS_HOST"] = "localhost"
        os.environ["GLOW_HPS_PORT"] = "8443"
        os.environ["GLOW_HPS_USERNAME"] = "repadmin"
        os.environ["GLOW_HPS_PASSWORD"] = "repadmin"

    @long_running
    @transaction(self=StepSpec())
    def set_env_vars_lr(self) -> None:
        os.environ["GLOW_HPS_HOST"] = "localhost"
        os.environ["GLOW_HPS_PORT"] = "8443"
        os.environ["GLOW_HPS_USERNAME"] = "repadmin"
        os.environ["GLOW_HPS_PASSWORD"] = "repadmin"

    @transaction(self=StepSpec())
    def write_env_file(self) -> None:
        (Path.cwd() / ".env").write_text(
            """GLOW_HPS_HOST=localhost\n
               GLOW_HPS_PORT=8443\n
               GLOW_HPS_USERNAME=repadmin\n
               GLOW_HPS_PASSWORD=repadmin""",
        )

    @long_running
    @transaction(self=StepSpec())
    def write_env_file_lr(self) -> None:
        (Path.cwd() / ".env").write_text(
            """GLOW_HPS_HOST=localhost\n
               GLOW_HPS_PORT=8443\n
               GLOW_HPS_USERNAME=repadmin\n
               GLOW_HPS_PASSWORD=repadmin""",
        )

    @transaction(self=StepSpec())
    def check_hps_system(self) -> list[HpsComputeResourceSet]:
        return HpsParametricStudyProject.get_compute_resource_sets()


class Steps(StepsModel):
    a_step: AStep


class SetEnvVarsSolution(Solution):
    display_name: str = "SetEnvVarsSolution"
    steps: Steps
