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


import json
import logging
import time

from ansys.saf.glow.solution import EntityHandle, long_running, NO_ENTITY, StepModel, StepSpec, transaction
from ansys.saf.glow.solution.hps import (
    HpsExecutionSpecification,
    HpsJobEvaluationStatus,
    HpsOutputFileSpecification,
    HpsParametricStudyProject,
    NO_HPS_STUDY_PROJECT,
)

from {{ cookiecutter.__solution_namespace }}.{{ cookiecutter.__solution_module_name }}.solution.scripts.{{cookiecutter.__step_module_name}}_calculate_sum import calculate_sum

logger = logging.getLogger(__name__)


NUMBER_OF_DESIGN_POINTS = 4
TERMINAL_STATUSES = {
    HpsJobEvaluationStatus.EVALUATED.value,
    HpsJobEvaluationStatus.FAILED.value,
    HpsJobEvaluationStatus.ABORTED.value,
    HpsJobEvaluationStatus.TIMEOUT.value,
}

class {{ cookiecutter.__step_definition_class_name }}(StepModel):
    """Step definition of the {{ cookiecutter.__step_name }} step."""

    first_args: list[float] = [0.0] * NUMBER_OF_DESIGN_POINTS
    second_args: list[float] = [0.0] * NUMBER_OF_DESIGN_POINTS
    results: list[float | None] = [None] * NUMBER_OF_DESIGN_POINTS
    output_file_handles: list[EntityHandle] = [NO_ENTITY] * NUMBER_OF_DESIGN_POINTS
    statuses: list[str] = ["No Job Created"] * NUMBER_OF_DESIGN_POINTS

    hps_project: HpsParametricStudyProject = NO_HPS_STUDY_PROJECT

    job_running: bool = False
    has_result: bool = False
    logs: str = ""

    def _push_statuses(self, statuses: list[str], stream_name: str) -> None:
        self.statuses = statuses
        self.transaction.raise_event(json.dumps(statuses), stream_name=stream_name)
        self.transaction.upload(["statuses"])

    def _monitor_until_terminal_status(self) -> list[str]:
        """Monitor statuses and logs until all design points reach a terminal state."""
        logger.info("started monitoring HPS parametric study")
        last_full_logs = ""
        while True:
            time.sleep(1)

            statuses = [status.evaluation_status.value for status in self.hps_project.get_status_of_design_points()]
            self._push_statuses(statuses=statuses, stream_name="{{ cookiecutter.__step_name_hyphenated }}-hps-parametric-status")

            logs_chunks: list[str] = []
            for index, logs_handle in enumerate(self.hps_project.logs_file):
                if logs_handle and logs_handle != NO_ENTITY:
                    content = self.storage_scope.get_text(logs_handle)
                    logs_chunks.append(f"Design point {index + 1}:\n{content}")
            if logs_chunks:
                logs_content = "\n\n".join(logs_chunks)
                delta = logs_content[len(last_full_logs):]
                if delta:
                    self.logs = logs_content
                    self.transaction.upload(["logs"])
                    self.transaction.raise_event(json.dumps(delta), stream_name="{{ cookiecutter.__step_name_hyphenated }}-hps-parametric-logs")
                    last_full_logs = logs_content

            if all(status in TERMINAL_STATUSES for status in statuses):
                return statuses

    @transaction(
        self=StepSpec(
            upload=["statuses", "results", "hps_project", "job_running", "has_result", "logs", "output_file_handles"],
            download=["first_args", "second_args"],
        ),
    )
    @long_running
    def hps_parametric_calculate(self) -> None:
        """Run a four-point parametric study on HPS."""
        self.job_running = True
        self.has_result = False
        self.transaction.upload(["job_running", "has_result"])

        self.results = [None] * NUMBER_OF_DESIGN_POINTS
        self.output_file_handles = [NO_ENTITY] * NUMBER_OF_DESIGN_POINTS
        self.logs = ""

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
        self.hps_project = hps_execution_spec.execute_parametric_study(
            first_arg=self.first_args,
            second_arg=self.second_args,
        )

        self.statuses = ["submitted"] * NUMBER_OF_DESIGN_POINTS
        self._push_statuses(statuses=self.statuses, stream_name="{{ cookiecutter.__step_name_hyphenated }}-hps-parametric-status")

        final_statuses = self._monitor_until_terminal_status()
        self.results = [
            result if status == HpsJobEvaluationStatus.EVALUATED.value else None
            for status, result in zip(final_statuses, self.hps_project.result)
        ]
        self.has_result = any(result is not None for result in self.results)
        self.transaction.raise_event(
            json.dumps(self.results),
            stream_name="{{ cookiecutter.__step_name_hyphenated }}-hps-parametric-results",
        )
        self.output_file_handles = list(self.hps_project.output_file)
        self._push_statuses(final_statuses, stream_name="{{ cookiecutter.__step_name_hyphenated }}-hps-parametric-status")
        self.job_running = False
        logger.info("completed monitoring HPS parametric study")