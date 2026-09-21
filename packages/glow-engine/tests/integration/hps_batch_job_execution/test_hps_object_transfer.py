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
import sys
import time

import pytest

from ansys.saf.glow._hps_parametric_studies.api import HpsParametricStudyProject, HpsSimpleProject
from ansys.saf.glow._hps_parametric_studies.base import HpsInputFileSpecification, HpsJobEvaluationStatus
from tests.conftest import MOCKS_DIR, PACKAGE_ROOT
import tests.mocks.hps_scripts.add_using_objects as add_using_objects_module
from tests.mocks.hps_scripts.add_using_objects import AddInput, AddOutput

pytestmark = [pytest.mark.use_batch_job]


@pytest.mark.parametrize("instance_system_type", [pytest.param("HPS", marks=pytest.mark.use_hps)], indirect=True)
@pytest.mark.usefixtures("hps_authentication")
class TestHpsObjectTransfer:
    def test_string_echo(self, tmp_path: Path):
        inputs = ["AZ123456", "AZ XY", "A......Z", "A-Z", "A_Z", "A/Z", 'A"Z', "A'Z", "©2025", "AäZ"]
        hashes = [sum(ord(char) for char in s) % 100 for s in inputs]
        echo_string_script_content = """
from ansys.saf.glow.hps_execution import HpsExecution

class Add(HpsExecution):

    def execute(self):
        s = self.context.input_parameters["input"]
        assert self.context.input_parameters["hash"] == sum(ord(char) for char in s) % 100
        return {"output": s}
"""
        echo_string_script = tmp_path / "echo_string.py"
        echo_string_script.write_text(echo_string_script_content)

        hps_project = HpsParametricStudyProject.start_hps_parametric_study(
            common_input_files={"script": echo_string_script},
            input_parameter_values={
                "input": inputs,
                "hash": hashes,
            },
            output_parameters={"output": str},
        )

        while not hps_project.finished:
            time.sleep(5)

        assert all(
            status.evaluation_status == HpsJobEvaluationStatus.EVALUATED
            for status in hps_project.get_status_of_design_points()
        )

        output = hps_project.output  # type: ignore
        assert output == inputs

    def test_data_object_transfer_with_job(self):
        hps_project = HpsSimpleProject.start_hps_job(
            input_values={
                "script": HpsInputFileSpecification(
                    Path(add_using_objects_module.__file__),
                    (MOCKS_DIR / "hps_scripts" / "add_using_objects.py").relative_to(PACKAGE_ROOT).as_posix(),
                ),
                "input": AddInput(4, 6),
            },
            output_parameters={"output": AddOutput},
            # we're assuming that under test the HPS evaluator will be using the same
            # version of python as the GLOW engine process
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            use_product_environment=False,
        )

        while not hps_project.finished:
            time.sleep(5)

        assert hps_project.status.evaluation_status == HpsJobEvaluationStatus.EVALUATED

        output = hps_project.output  # type: ignore
        assert isinstance(output, AddOutput)
        assert output.result == 10
        assert output.positive is True

    def test_data_object_transfer_with_parametric_study(self):
        hps_project = HpsParametricStudyProject.start_hps_parametric_study(
            common_input_files={
                "script": HpsInputFileSpecification(
                    Path(add_using_objects_module.__file__),
                    (MOCKS_DIR / "hps_scripts" / "add_using_objects.py").relative_to(PACKAGE_ROOT).as_posix(),
                ),
            },
            input_parameter_values={
                "input": [AddInput(4, 6), AddInput(1, -6)],
            },
            output_parameters={"output": AddOutput},
            # we're assuming that under test the HPS evaluator will be using the same
            # version of python as the GLOW engine process
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            use_product_environment=False,
        )

        while not hps_project.finished:
            time.sleep(5)

        assert all(
            status.evaluation_status == HpsJobEvaluationStatus.EVALUATED
            for status in hps_project.get_status_of_design_points()
        )

        output1 = hps_project.output[0]  # type: ignore
        assert isinstance(output1, AddOutput)
        assert output1.result == 10
        assert output1.positive

        output2 = hps_project.output[1]  # type: ignore
        assert isinstance(output2, AddOutput)
        assert output2.result == -5
        assert not output2.positive
