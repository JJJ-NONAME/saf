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
import re
import sys
import time

import pytest

from ansys.saf.glow.solution.hps import (
    HpsDesignPointSelection,
    HpsJobEvaluationStatus,
    HpsParametricStudyProject,
)
import tests.mocks.solution_with_hps_python_script.hps_parametric_study as hps_parametric_study_module

pytestmark = [
    pytest.mark.filterwarnings(
        "ignore:Unverified HTTPS request is being made to host 'localhost'.*:urllib3.exceptions.InsecureRequestWarning",
    ),
    pytest.mark.use_batch_job,
]


X = [4.0, 3.0, 5.0, 6.0, 7.0, 8.0]
Y = [6.0, 5.0, 7.0, 8.0, 9.0, 10.0]
EXPECTED_RESULT = [10.0, 8.0, 12.0, 14.0, 16.0, 18.0]
SORTED_EXPECTED_RESULT = [8.0, 10.0, 12.0, 14.0, 16.0, 18.0]


@pytest.fixture(scope="class")
def completed_hps_project():
    outer_attempts = 0
    while outer_attempts != 3:
        hps_project = HpsParametricStudyProject.start_hps_parametric_study(
            common_input_files={
                "script": Path(hps_parametric_study_module.__file__).parent
                / "method_assets"
                / "add_script_with_string_output.py",
            },
            input_parameter_values={"x": X, "y": Y},
            output_parameters={"result": float, "text_result": str},
            # we're assuming that under test the HPS evaluator will be using the same
            # version of python as the GLOW engine process
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            use_product_environment=False,
        )

        attempts = 1

        while not hps_project.finished and attempts < 120:
            time.sleep(5)
            attempts += 1

        if hps_project.fetch_values_of_parameter("result") == EXPECTED_RESULT:
            return hps_project
        outer_attempts += 1
    raise RuntimeError("Unable to get project into expected state after 3 attempts")


@pytest.mark.parametrize("instance_system_type", [pytest.param("HPS", marks=pytest.mark.use_hps)], indirect=True)
@pytest.mark.usefixtures("hps_authentication")
class TestHpsDesignPointSelection:
    def test_no_filter_results_in_all_values_of_one_parameter(self, completed_hps_project: HpsParametricStudyProject):
        assert completed_hps_project.fetch_values_of_parameter("result") == EXPECTED_RESULT

    def test_no_filter_results_in_all_values_of_two_parameters(self, completed_hps_project: HpsParametricStudyProject):
        assert completed_hps_project.fetch_values_of_parameters(["result", "x"]) == [EXPECTED_RESULT, X]

    def test_no_filter_results_in_all_values_of_no_parameters(self, completed_hps_project: HpsParametricStudyProject):
        assert completed_hps_project.fetch_values_of_parameters([]) == []

    def test_fetch_values_of_parameter_raises_exception_when_requesting_values_of_missing_parameter(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        with pytest.raises(AttributeError, match="HPS project does not have parameter or file corresponding to JUNK"):
            completed_hps_project.fetch_values_of_parameter("JUNK")

    def test_query_for_stopped_design_points_returns_all_design_points(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        assert completed_hps_project.fetch_values_of_parameters(
            ["result", "x"],
            HpsDesignPointSelection(
                eval_status=[
                    HpsJobEvaluationStatus.EVALUATED,
                    HpsJobEvaluationStatus.ABORTED,
                    HpsJobEvaluationStatus.FAILED,
                ],
            ),
        ) == [EXPECTED_RESULT, X]

    def test_query_for_in_progress_design_points_returns_no_design_points(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        assert completed_hps_project.fetch_values_of_parameters(
            ["result", "x"],
            HpsDesignPointSelection(
                eval_status=[
                    HpsJobEvaluationStatus.PROLOG,
                    HpsJobEvaluationStatus.RUNNING,
                    HpsJobEvaluationStatus.PENDING,
                ],
            ),
        ) == [[], []]

    @pytest.mark.skip(reason="not supported by HPS yet or not clear how to implement")
    def test_filtering_for_design_points_by_index_returns_those_design_points(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        assert completed_hps_project.fetch_values_of_parameters(
            ["result"],
            HpsDesignPointSelection(required_design_points=[3, 4]),
        ) == [[EXPECTED_RESULT[3], EXPECTED_RESULT[4]]]

    def test_filtering_for_design_points_by_index_raises_not_implemented_exception(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        with pytest.raises(
            NotImplementedError,
            match=re.escape("The required_design_points filter is not supported by HPS."),
        ):
            completed_hps_project.fetch_values_of_parameters(
                ["result"],
                HpsDesignPointSelection(required_design_points=[3, 4]),
            )

    def test_limiting_design_points_returns_restricted_set_of_design_points(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        assert completed_hps_project.fetch_values_of_parameter("result", HpsDesignPointSelection(limit=2)) == [
            EXPECTED_RESULT[0],
            EXPECTED_RESULT[1],
        ]

    def test_limiting_design_points_returns_restricted_set_of_design_points_when_querying_evaluation_status(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        assert [
            s.evaluation_status
            for s in completed_hps_project.get_status_of_design_points(HpsDesignPointSelection(limit=2))
        ] == [
            HpsJobEvaluationStatus.EVALUATED,
            HpsJobEvaluationStatus.EVALUATED,
        ]

    def test_offsetting_design_points_returns_offset_set_of_design_points(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        assert completed_hps_project.fetch_values_of_parameter(
            "result",
            HpsDesignPointSelection(offset=1, limit=2),
        ) == [
            EXPECTED_RESULT[1],
            EXPECTED_RESULT[2],
        ]

    def test_parameter_value_filter_returns_requested_design_points(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        assert completed_hps_project.fetch_values_of_parameter(
            "index",
            HpsDesignPointSelection(parameter_filter={"result.ge": 12.0}),
        ) == [2, 3, 4, 5]

    def test_parameter_value_filter_using_dot_equals_returns_requested_design_points(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        assert completed_hps_project.fetch_values_of_parameter(
            "index",
            HpsDesignPointSelection(parameter_filter={"result.=": 12.0}),
        ) == [2]

    def test_parameter_value_filter_using_equals_returns_requested_design_points(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        assert completed_hps_project.fetch_values_of_parameter(
            "index",
            HpsDesignPointSelection(parameter_filter={"result": 12.0}),
        ) == [2]

    @pytest.mark.skip(reason="not supported by HPS yet or not clear how to implement")
    def test_parameter_value_filter_using_in_returns_requested_design_points(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        assert completed_hps_project.fetch_values_of_parameter(
            "index",
            HpsDesignPointSelection(parameter_filter={"result.in": [12.0]}),
        ) == [2]

    def test_parameter_value_filter_using_in_returns_raises_exception(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        with pytest.raises(
            NotImplementedError,
            match=re.escape("The 'in' operator is not supported by HPS."),
        ):
            completed_hps_project.fetch_values_of_parameter(
                "index",
                HpsDesignPointSelection(parameter_filter={"result.in": [12.0]}),
            )

    def test_parameter_value_filter_using_text_equals_returns_requested_design_points(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        assert completed_hps_project.fetch_values_of_parameter(
            "index",
            HpsDesignPointSelection(parameter_filter={"text_result": "12.0"}),
        ) == [2]

    def test_parameter_value_filter_raises_exception_if_requested_to_filter_non_existent_parameter(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "JUNK is present in the selection filter argument but is not the name of a parameter. "
                "Available parameters are: result, text_result, index, x, y.",
            ),
        ):
            completed_hps_project.fetch_values_of_parameter(
                "index",
                HpsDesignPointSelection(parameter_filter={"JUNK.ge": 12.0}),
            )

    @pytest.mark.skip(reason="not supported by HPS")
    def test_sorting_design_points_produces_expected_result(self, completed_hps_project: HpsParametricStudyProject):
        assert (
            completed_hps_project.fetch_values_of_parameter("result", HpsDesignPointSelection(sort="result"))
            == SORTED_EXPECTED_RESULT
        )

    def test_sorting_design_points_raises_exception_if_requested_to_sort_by_missing_parameter(
        self,
        completed_hps_project: HpsParametricStudyProject,
    ):
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "JUNK is present in the selection sort argument but is not the name of a parameter. "
                "Available parameters are: result, text_result, index, x, y.",
            ),
        ):
            completed_hps_project.fetch_values_of_parameter("result", HpsDesignPointSelection(sort="JUNK"))
