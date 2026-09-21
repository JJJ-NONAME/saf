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
import time

from ansys.hps.client import ClientError  # pyright: ignore[reportMissingTypeStubs]

from ansys.saf.glow._hps_parametric_studies.api import NO_HPS_SIMPLE_PROJECT, HpsSimpleProject
from ansys.saf.glow.solution import StepModel, StepSpec, long_running, transaction
from ansys.saf.glow.solution.hps import HpsJobEvaluationStatus

logger = logging.getLogger(__name__)


class HpsSimpleProjectStep(StepModel):
    hps_project: HpsSimpleProject = NO_HPS_SIMPLE_PROJECT
    python_name: str | None = None
    python_version: str | None = None
    n_jobs: int = 999
    hps_status: str = ""

    @transaction(self=StepSpec(upload=["hps_project"]))
    def start_job_using_ansys_python_and_bdm(self, ansys_python_version: str) -> None:
        """Compute the sum of two numbers."""
        self.hps_project = HpsSimpleProject.start_hps_job(
            input_values={"script": self.transaction.get_asset_entity_handle("get_python_path.py")},
            output_parameters={"python_name": str, "python_version": str},
            python_version=ansys_python_version,
            use_product_environment=False,
            use_ansys_python=True,
        )

    @transaction(self=StepSpec(upload=["hps_project"]))
    @long_running
    def start_job_using_regular_python(self, python_version: str) -> None:
        """Compute the sum of two numbers."""
        self.hps_project = HpsSimpleProject.start_hps_job(
            input_values={"script": self.transaction.get_asset_entity_handle("get_python_path.py")},
            output_parameters={"python_name": str, "python_version": str},
            use_product_environment=False,
            python_version=python_version,
            use_ansys_python=False,
        )

    @transaction(self=StepSpec(upload=["python_name", "python_version"], download=["hps_project"]))
    def query_hps(self) -> None:
        """Query the parameter study and update results."""
        was_finished = self.hps_project.finished
        status = self.hps_project.status
        python_name = None
        python_version = None
        if status.evaluation_status == HpsJobEvaluationStatus.EVALUATED:
            python_name = self.hps_project.python_name  # type: ignore
            python_version = self.hps_project.python_version  # type: ignore

        if python_name is None:
            assert not was_finished
        else:
            assert self.hps_project.finished

        self.python_name = python_name
        self.python_version = python_version

    @transaction(self=StepSpec(download=["hps_project"]))
    def query_hps_status(self) -> str:
        """Query the parameter study and update status."""
        return self.hps_project.status.evaluation_status.value

    @transaction(self=StepSpec(download=["hps_project"], upload=["hps_status"]))
    @long_running
    def query_hps_status_on_loop(self, timeout: int = 60) -> None:
        """Query the parameter study and update status."""
        start_time = time.time()
        while (time.time() - start_time) < timeout or self.hps_status != "evaluated":
            try:
                self.hps_status = self.hps_project.status.evaluation_status.value
            except ClientError as e:
                # avoid race condition where HPS Client detects the expiration and fails to refresh before GLOW does.
                logger.warning(str(e))
            time.sleep(1)
