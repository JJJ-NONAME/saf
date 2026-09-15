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

"""Backend of the {{ cookiecutter.__step_name }} step."""


import logging
import time

from ansys.saf.glow.solution import EntityHandle, NO_ENTITY, StepModel, StepSpec, transaction
from ansys.saf.glow.solution.hps import (
    HpsSimpleProject,
    HpsExecutionSpecification,
    HpsOutputFileSpecification,
    NO_HPS_SIMPLE_PROJECT,
)

from {{ cookiecutter.__solution_namespace }}.{{ cookiecutter.__solution_module_name }}.solution.scripts.{{cookiecutter.__step_module_name}}_calculate_sum_simple import calculate_sum

logger = logging.getLogger(__name__)

class {{ cookiecutter.__step_definition_class_name }}(StepModel):
    """Step definition of the {{ cookiecutter.__step_name }} step."""

    first_arg: float = 0
    second_arg: float = 0
    result: float = 0
    file_result: str = ""

    hps_project: HpsSimpleProject = NO_HPS_SIMPLE_PROJECT

    status: str = "No Job Created"
    job_running: bool = False
    has_result: bool = False
    logs: str = ""

    def _push_status(self, status: str, stream_name: str) -> None:
        self.status = status
        self.transaction.raise_event(status, stream_name=stream_name)
        self.transaction.upload(["status"])

    @transaction(
        self=StepSpec(
            upload=["status", "result", "hps_project", "job_running", "has_result", "logs"],
            download=["first_arg", "second_arg"],
        ),
        enable_termination_event=True,
    )
    def {{ cookiecutter.__step_module_name }}_hps_simple_calculate(self) -> None:
        """Compute the sum of two numbers."""
        self.job_running = True
        self.has_result = False
        self.transaction.upload(["job_running", "has_result"])
        # execute the function that performs the calculation and generates outputs on HPS
        hps_execution_spec = HpsExecutionSpecification(
            function=calculate_sum,
            output_parameters={
                "result": float,
                "output_file": HpsOutputFileSpecification(
                    evaluation_path="output.txt",
                    return_type=EntityHandle,
                ),
                "logs_file": HpsOutputFileSpecification(
                    evaluation_path="logs.txt",
                    collect_interval=1,
                    return_type=EntityHandle,
                ),
            }
        )
        self.hps_project = hps_execution_spec.execute(
            first_arg=self.first_arg,
            second_arg=self.second_arg,
        )

        self._push_status(status="HPS Job submitted", stream_name="{{ cookiecutter.__step_module_name_hyphenated }}-hps-simple-status")

        logger.info("started monitoring HPS job")
        NUMBER_OF_ITERATIONS = 240
        iterations = 0
        while iterations != NUMBER_OF_ITERATIONS and not self.hps_project.finished:
            self._push_status(self.hps_project.status.evaluation_status.value, stream_name="{{ cookiecutter.__step_module_name_hyphenated }}-hps-simple-status")
            time.sleep(1)
            if self.hps_project.logs_file and self.hps_project.logs_file != NO_ENTITY:
                logs_content = self.storage_scope.get_text(self.hps_project.logs_file)
                self.logs = logs_content
                self.transaction.upload(["logs"])
                self._push_status(status=logs_content, stream_name="{{ cookiecutter.__step_module_name_hyphenated }}-hps-simple-logs")
            iterations += 1

        logger.info(f"HPS Job finished with status: {self.hps_project.status.evaluation_status.value}")

        if self.hps_project.finished:
            status = self.hps_project.status.evaluation_status.value
            self.result = self.hps_project.result  # type: ignore
            self.has_result = True
        else:
            status = "HPS Job took longer than expected"
            self.has_result = False

        self._push_status(status, stream_name="{{ cookiecutter.__step_module_name_hyphenated }}-hps-simple-status")
        self.job_running = False
        self.transaction.upload(["job_running", "has_result"])
        logger.info("completed monitoring HPS job")

    @transaction(self=StepSpec(upload=["file_result"], download=["hps_project"]), enable_termination_event=True)
    def {{ cookiecutter.__step_module_name }}_fetch_result_file(self):
        """Fetch the content of the output file generated on HPS."""
        self.file_result = self.storage_scope.get_text(self.hps_project.output_file)  # type: ignore
