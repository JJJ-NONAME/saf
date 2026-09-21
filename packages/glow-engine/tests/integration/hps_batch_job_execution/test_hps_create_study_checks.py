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
from typing import Any
from unittest import mock

import pytest

from ansys.saf.glow._core.blob_managers import HpsBlobManager
from ansys.saf.glow._hps_parametric_studies.api import HpsParametricStudyProject, HpsSimpleProject
from ansys.saf.glow._hps_parametric_studies.base import (
    HpsInputDirectory,
    HpsInputFile,
    HpsInputFileSpecification,
    HpsOutputFileSpecification,
    HpsParameterValue,
)
from ansys.saf.glow._hps_parametric_studies.study_definition import (
    HpsParametricStudyDefinition,
    PythonSourceSpecification,
)
import tests.mocks.solution_with_hps_python_script.hps_parametric_study as hps_parametric_study_module

METHOD_ASSETS = Path(hps_parametric_study_module.__file__).parent / "method_assets"

pytestmark = [pytest.mark.use_batch_job]


@pytest.mark.parametrize("instance_system_type", [pytest.param("HPS", marks=pytest.mark.use_hps)], indirect=True)
@pytest.mark.usefixtures("hps_authentication")
class TestHpsStudyChecks:
    def test_exception_raised_when_evaluation_paths_overlap_between_input_files(self):
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "The evaluation path 'x/y/z.txt' of the input file A "
                "is the same as the evaluation path of the input file, B.",
            ),
        ):
            HpsSimpleProject.start_hps_job(
                input_values={
                    "script": METHOD_ASSETS / "echo_input_sources.py",
                    "A": HpsInputFileSpecification(METHOD_ASSETS / "echo.py", evaluation_path="x/y/z.txt"),
                    "B": HpsInputFileSpecification(METHOD_ASSETS / "echo_context.py", evaluation_path="x/y/z.txt"),
                },
                output_parameters={},
            )

    def test_exception_raised_when_evaluation_paths_overlap_between_input_file_and_exec_python_script(
        self,
    ):
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "The evaluation path 'exec_python.py' of the input file A is the "
                "same as the evaluation path of the input file created by GLOW, inner_script_file.",
            ),
        ):
            HpsSimpleProject.start_hps_job(
                input_values={
                    "script": METHOD_ASSETS / "echo_input_sources.py",
                    "A": HpsInputFileSpecification(METHOD_ASSETS / "echo.py", evaluation_path="exec_python.py"),
                },
                output_parameters={},
            )

    def test_exception_raised_when_evaluation_paths_overlap_between_input_file_and_builtin_file(
        self,
    ):
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "The evaluation path 'inner_context.json' of the input file A "
                "is the same as the evaluation path of the input file created by GLOW, inner_context.",
            ),
        ):
            HpsSimpleProject.start_hps_job(
                input_values={
                    "script": METHOD_ASSETS / "echo_input_sources.py",
                    "A": HpsInputFileSpecification(METHOD_ASSETS / "echo.py", evaluation_path="inner_context.json"),
                },
                output_parameters={},
            )

    def test_exception_raised_when_two_output_files_have_the_same_evaluation_path(self):
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "The evaluation path 'x/y/z.txt' of the output file A "
                "is the same as the evaluation path of the output file, B.",
            ),
        ):
            HpsSimpleProject.start_hps_job(
                input_values={
                    "script": METHOD_ASSETS / "echo_input_sources.py",
                },
                output_parameters={
                    "A": HpsOutputFileSpecification("x/y/z.txt"),
                    "B": HpsOutputFileSpecification("x/y/z.txt"),
                },
            )

    @pytest.mark.parametrize("path", ["/x/y/z.txt", "x:\\y\\z.txt"])
    def test_exception_raised_when_input_evaluation_path_is_absolute(self, path: str):
        with pytest.raises(
            RuntimeError,
            match=re.escape(f"The evaluation path of file A must be relative, but it is '{path}'."),
        ):
            HpsSimpleProject.start_hps_job(
                input_values={
                    "script": METHOD_ASSETS / "echo_input_sources.py",
                    "A": HpsInputFileSpecification(METHOD_ASSETS / "echo.py", evaluation_path=path),
                },
                output_parameters={},
            )

    def test_exception_raised_when_output_evaluation_path_is_absolute(self):
        with pytest.raises(
            RuntimeError,
            match=re.escape("The evaluation path of file myfile must be relative, but it is '/x/x.txt'."),
        ):
            HpsSimpleProject.start_hps_job(
                input_values={
                    "script": METHOD_ASSETS / "echo_input_sources.py",
                },
                output_parameters={
                    "myfile": HpsOutputFileSpecification("/x/x.txt"),
                },
            )

    def test_exception_raised_when_input_file_key_overlaps_with_builtin_file(self):
        with pytest.raises(
            RuntimeError,
            match=re.escape("The key 'inner_context' is used for a built-in input file."),
        ):
            HpsSimpleProject.start_hps_job(
                input_values={
                    "script": METHOD_ASSETS / "echo_input_sources.py",
                    "inner_context": METHOD_ASSETS / "echo.py",
                },
                output_parameters={},
            )

    def test_exception_raised_when_output_file_key_overlaps_with_builtin_file(self):
        with pytest.raises(
            RuntimeError,
            match=re.escape("The key 'output.txt' is used for a built-in output file."),
        ):
            HpsSimpleProject.start_hps_job(
                input_values={"script": METHOD_ASSETS / "echo_input_sources.py"},
                output_parameters={"output.txt": HpsOutputFileSpecification()},
            )

    def test_exception_when_input_parameter_and_input_file_keys_overlap(self):
        with pytest.raises(
            RuntimeError,
            match=re.escape("found 2 parameters called s"),
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files={
                    "script": METHOD_ASSETS / "echo_input_sources.py",
                    "s": METHOD_ASSETS / "echo.py",
                },
                input_parameter_values={"s": [1, 2]},
                output_parameters={},
            )

    def test_exception_raised_when_using_reserved_word_as_param(self):
        reserved_key = "index"
        with pytest.raises(
            RuntimeError,
            match=f"the reserved name '{reserved_key}' has been used as the name of a parameter",
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files={"script": METHOD_ASSETS / "echo_input_sources.py"},
                input_parameter_values={"s": [1, 2]},
                output_parameters={reserved_key: HpsOutputFileSpecification()},
            )

    def test_exception_raised_when_output_params_is_none(self):
        study_builder = HpsParametricStudyDefinition()
        with pytest.raises(RuntimeError, match="output parameters not set"):
            _ = study_builder.output_parameters

    def test_python_version_applied(self, hps_blob_manager: HpsBlobManager):
        input_values = {"script": METHOD_ASSETS / "echo_input_sources.py", "x": 6.0, "y": 99.0}
        study_builder = HpsParametricStudyDefinition()
        common_input_files, input_parameter_values = study_builder.split_simple_input_values(
            input_values,  # pyright: ignore[reportArgumentType]
        )

        parametric_study_definition_mock = (
            "ansys.saf.glow._hps_parametric_studies.study_definition.HpsParametricStudyDefinition"
        )
        with (
            mock.patch(f"{parametric_study_definition_mock}._build_definitions") as build_definitions,
            mock.patch(
                f"{parametric_study_definition_mock}._create_job",
            ) as create_job,
        ):
            python_source = PythonSourceSpecification(
                use_product_environment=False,
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
                use_ansys_python=False,
                product_environment_version=None,
                use_latest_python=False,
            )
            study_builder.add_study_to_project(
                604800,
                common_input_files,
                input_parameter_values,
                output_parameters={"result": float},
                hps_blob_manager=hps_blob_manager,
                python_source=python_source,
            )

        assert study_builder.python_version == f"{sys.version_info.major}.{sys.version_info.minor}"

        build_definitions.assert_called_once()
        create_job.assert_called_once()

    def test_exception_raised_when_job_definition_not_created(self):
        parametric_study_definition_mock = (
            "ansys.saf.glow._hps_parametric_studies.study_definition.HpsParametricStudyDefinition"
        )
        with (
            mock.patch(
                f"{parametric_study_definition_mock}._create_task_and_job_definitions",
            ) as create_task,
            pytest.raises(
                RuntimeError,
                match="job definition has not been created",
            ),
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files={"script": METHOD_ASSETS / "echo_input_sources.py"},
                input_parameter_values={"x": [6.0], "y": [99.0]},
                output_parameters={"result": float},
            )

        create_task.assert_called_once()

    def test_requirements_file_is_created(self, hps_blob_manager: HpsBlobManager):
        input_values: dict[str, HpsInputFile | HpsInputDirectory | HpsParameterValue] = {
            "script": METHOD_ASSETS / "echo_input_sources.py",
            "x": 6.0,
            "y": 99.0,
        }
        study_builder = HpsParametricStudyDefinition()
        common_input_files, input_parameter_values = study_builder.split_simple_input_values(
            input_values,
        )

        dependencies_arr = ["numpy", "requests"]
        parametric_study_definition_mock = (
            "ansys.saf.glow._hps_parametric_studies.study_definition.HpsParametricStudyDefinition"
        )
        with (
            mock.patch(
                f"{parametric_study_definition_mock}._create_task_and_job_definitions",
            ) as create_task,
            mock.patch(
                f"{parametric_study_definition_mock}._create_job",
            ) as create_job,
        ):
            python_source = PythonSourceSpecification(
                use_product_environment=False,
                python_version=None,
                use_ansys_python=False,
                product_environment_version=None,
                use_latest_python=False,
            )
            study_builder.add_study_to_project(
                604800,
                common_input_files,
                input_parameter_values,
                output_parameters={"result": float},
                hps_blob_manager=hps_blob_manager,
                dependencies=dependencies_arr,
                python_source=python_source,
            )

            with study_builder.get_project_api() as project_api:
                requirements_file = next(
                    (
                        file
                        for file in project_api.get_files(  # pyright: ignore[reportUnknownMemberType]
                            content=True,
                        )
                        if file.name == "requirements"
                    ),
                    None,
                )

        assert requirements_file.name == "requirements"  # pyright: ignore[reportOptionalMemberAccess]
        assert requirements_file.content.decode().splitlines() == dependencies_arr  # type: ignore

        create_job.assert_called_once()
        create_task.assert_called_once()

    def test_exception_raised_when_output_params_is_invalid_type(self):
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "output_parameters must be a dictionary with string keys and values "
                "which are either a type, an HpsOutputFileSpecification "
                "or an HpsOutputDirectorySpecification.",
            ),
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files={"script": METHOD_ASSETS / "echo_input_sources.py"},
                input_parameter_values={"s": [1, 2]},
                output_parameters=[],  # pyright: ignore[reportArgumentType]
            )

    def test_exception_raised_when_input_parameter_values_is_invalid_type(self):
        with pytest.raises(
            AttributeError,
            match=re.escape(
                "'float' object has no attribute 'items'",
            ),
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files={"script": METHOD_ASSETS / "echo_input_sources.py"},
                input_parameter_values=(3.0, 99.0),  # pyright: ignore[reportArgumentType]
                output_parameters={"result": float},
            )

    def test_exception_raised_when_common_input_params_is_invalid_type(self):
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "common_input_files must be a dictionary with string keys and Path, "
                "HpsInputFileSpecification, "
                "HpsInputDirectorySpecification or EntityHandle values.",
            ),
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files=[METHOD_ASSETS / "echo_input_sources.py"],  # pyright: ignore[reportArgumentType]
                input_parameter_values={},
                output_parameters={"s": HpsOutputFileSpecification()},
            )

    def test_exception_raised_when_input_params_is_invalid_type_when_split_input(self):
        input_values = [METHOD_ASSETS / "echo_input_sources.py", 6.0, 99.0]
        study_builder = HpsParametricStudyDefinition()
        with pytest.raises(
            RuntimeError,
            match=re.escape("input_values must be a dictionary."),
        ):
            study_builder.split_simple_input_values(input_values)  # pyright: ignore[reportArgumentType]

    @pytest.mark.parametrize("dependencies", ["XXX", [1]])
    def test_exception_when_python_dependencies_are_not_list_of_strings(
        self,
        dependencies: Any,
    ):
        with pytest.raises(
            RuntimeError,
            match=re.escape("The dependencies argument must be a list of strings."),
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files={"script": METHOD_ASSETS / "echo_input_sources.py"},
                input_parameter_values={},
                output_parameters={"s": HpsOutputFileSpecification()},
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
                dependencies=dependencies,
            )

    @pytest.mark.parametrize("products", ["XXX", [1]])
    def test_exception_when_products_are_not_list_of_software(
        self,
        products: Any,
    ):
        with pytest.raises(
            RuntimeError,
            match=re.escape("The products argument must be a list of software."),
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files={"script": METHOD_ASSETS / "echo_input_sources.py"},
                input_parameter_values={},
                output_parameters={"s": HpsOutputFileSpecification()},
                products=products,
            )

    def test_exception_when_use_product_environment_and_dependencies_are_both_specified(self):
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "You cannot use the product environment and specify "
                "dependencies (additional packages cannot be added to the product environment).",
            ),
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files={"script": METHOD_ASSETS / "echo_input_sources.py"},
                input_parameter_values={},
                output_parameters={"s": HpsOutputFileSpecification()},
                dependencies=["numpy"],
                use_product_environment=True,
            )

    def test_exception_when_use_product_environment_and_python_version_are_both_specified(self):
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "You cannot use the product environment and specify "
                "a python version. Setting the 'product_environment_version' argument allows you to "
                "select the python interpreter deployed in a specific product environment.",
            ),
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files={"script": METHOD_ASSETS / "echo_input_sources.py"},
                input_parameter_values={},
                output_parameters={"s": HpsOutputFileSpecification()},
                use_product_environment=True,
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            )

    def test_exception_when_not_use_product_environment_and_product_environment_version_are_both_specified(
        self,
    ):
        with pytest.raises(
            RuntimeError,
            match=re.escape("You cannot specify the product environment version when not using product environment."),
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files={"script": METHOD_ASSETS / "echo_input_sources.py"},
                input_parameter_values={},
                output_parameters={"s": HpsOutputFileSpecification()},
                use_product_environment=False,
                product_environment_version="0.0",
            )

    def test_exception_when_use_product_environment_and_use_ansys_python_are_both_activated(self):
        with pytest.raises(
            RuntimeError,
            match=re.escape("You cannot use the product environment with Ansys Python. "),
        ):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files={"script": METHOD_ASSETS / "echo_input_sources.py"},
                input_parameter_values={},
                output_parameters={"s": HpsOutputFileSpecification()},
                use_product_environment=True,
                use_ansys_python=True,
            )

    def test_ansys_python_is_selected_when_activating_use_ansys_python(
        self,
        hps_blob_manager: HpsBlobManager,
    ):
        input_values = {"script": METHOD_ASSETS / "echo_input_sources.py", "x": 6.0, "y": 99.0}
        study_builder = HpsParametricStudyDefinition()
        common_input_files, input_parameter_values = study_builder.split_simple_input_values(input_values)

        class_to_mock = "ansys.saf.glow._hps_parametric_studies.study_definition.HpsParametricStudyDefinition"
        with (
            mock.patch(f"{class_to_mock}._build_definitions") as build_definitions,
            mock.patch(
                f"{class_to_mock}._create_job",
            ) as create_job,
        ):
            python_source = PythonSourceSpecification(
                use_product_environment=False,
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
                use_ansys_python=True,
                product_environment_version=None,
                use_latest_python=False,
            )
            study_builder.add_study_to_project(
                604800,
                common_input_files,
                input_parameter_values,
                output_parameters={"result": float},
                hps_blob_manager=hps_blob_manager,
                python_source=python_source,
            )

        assert study_builder.software_requirements[0].name == "Ansys Python"
        assert study_builder.software_requirements[0].version == f"{sys.version_info.major}.{sys.version_info.minor}"

        build_definitions.assert_called_once()
        create_job.assert_called_once()
