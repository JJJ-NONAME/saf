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

from collections.abc import Iterator
from pathlib import Path
import re
from typing import Any, TypeVar
from unittest.mock import MagicMock
import uuid

import pytest
import pytest_mock

from ansys.saf.glow._core.blob_managers import HpsBlobManager
from ansys.saf.glow._executor.local import transaction_local
from ansys.saf.glow._hps_auth.hps_authenticator import NullHpsAuthenticator
from ansys.saf.glow._hps_parametric_studies.api import (
    NO_HPS_SIMPLE_PROJECT,
    NO_HPS_STUDY_PROJECT,
    HpsParametricStudyProject,
    HpsSimpleProject,
)
from ansys.saf.glow._hps_parametric_studies.base import (
    DynamicHpsParametricStudyProject,
    DynamicHpsSimpleProject,
    HpsInputDirectorySpecification,
    HpsInputFileSpecification,
    HpsInputSourceSpecification,
    HpsOutputDirectorySpecification,
    HpsOutputFileSpecification,
    HpsOutputSourceSpecification,
    HpsParameterValue,
    HpsProject,
    HpsProjectNotStartedError,
)
from ansys.saf.glow._hps_parametric_studies.study_definition import HpsParametricStudyDefinition
from ansys.saf.glow._hps_parametric_studies.system import HpsParametricStudySystem
from ansys.saf.glow.solution import EntityHandle

T = TypeVar("T")


def g() -> Iterator[dict[str, HpsParameterValue]]:
    yield {}


@pytest.fixture(autouse=True)
def mock_transaction_local(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    monkeypatch.setattr(transaction_local, "hps_blob_manager", MagicMock(), raising=False)


class TestHpsWithoutSolution:
    def test_serialized_no_simple_project_is_equal_to_no_simple_project(
        self,
        hps_blob_manager: HpsBlobManager,
    ):
        serialized = NO_HPS_SIMPLE_PROJECT.model_dump_json()
        deserialized = HpsSimpleProject.model_validate_json(serialized)
        assert deserialized == NO_HPS_SIMPLE_PROJECT
        dynamic_deserialized = DynamicHpsSimpleProject(deserialized, hps_blob_manager, NullHpsAuthenticator())
        assert dynamic_deserialized == NO_HPS_SIMPLE_PROJECT
        with pytest.raises(HpsProjectNotStartedError, match="The HPS project has not been started."):
            _ = DynamicHpsSimpleProject(
                NO_HPS_SIMPLE_PROJECT,
                hps_blob_manager,
                NullHpsAuthenticator(),
            ).exists

    def test_serialized_no_study_project_is_equal_to_no_study_project(self, hps_blob_manager: HpsBlobManager):
        serialized = NO_HPS_STUDY_PROJECT.model_dump_json()
        deserialized = HpsParametricStudyProject.model_validate_json(serialized)
        assert deserialized == NO_HPS_STUDY_PROJECT
        dynamic_deserialized = DynamicHpsParametricStudyProject(deserialized, hps_blob_manager, NullHpsAuthenticator())
        assert dynamic_deserialized == NO_HPS_STUDY_PROJECT
        with pytest.raises(HpsProjectNotStartedError, match="The HPS project has not been started."):
            _ = DynamicHpsParametricStudyProject(
                NO_HPS_STUDY_PROJECT,
                hps_blob_manager,
                NullHpsAuthenticator(),
            ).exists

    @pytest.mark.parametrize(
        ("common_input_files", "input_parameter_values", "output_parameters", "expected_error"),
        [
            (
                [],
                {},
                {},
                "common_input_files must be a dictionary with string keys and Path, "
                "HpsInputFileSpecification, "
                "HpsInputDirectorySpecification or EntityHandle values.",
            ),
            (
                {1: 1},
                {},
                {},
                "common_input_files must be a dictionary with string keys and Path, "
                "HpsInputFileSpecification, "
                "HpsInputDirectorySpecification or EntityHandle values.",
            ),
            (
                {"s": 1},
                {},
                {},
                "common_input_files must be a dictionary with string keys and Path, "
                "HpsInputFileSpecification, "
                "HpsInputDirectorySpecification or EntityHandle values.",
            ),
            (
                {"s": "s"},
                {},
                {},
                "common_input_files must be a dictionary with string keys and Path, "
                "HpsInputFileSpecification, "
                "HpsInputDirectorySpecification or EntityHandle values.",
            ),
            (
                {},
                [],
                {},
                "input_parameter_values_must_be an iterable or a dictionary with string keys and list values.",
            ),
            (
                {},
                {1: 1},
                {},
                "input_parameter_values_must_be an iterable or a dictionary with string keys and list values.",
            ),
            (
                {},
                {"s": 1},
                {},
                "input_parameter_values_must_be an iterable or a dictionary with string keys and list values.",
            ),
            (
                {},
                {},
                [],
                "output_parameters must be a dictionary with string keys and values which "
                "are either a type, an HpsOutputFileSpecification or an HpsOutputDirectorySpecification.",
            ),
            (
                {},
                {},
                {1: 1},
                "output_parameters must be a dictionary with string keys and values which "
                "are either a type, an HpsOutputFileSpecification or an HpsOutputDirectorySpecification.",
            ),
            (
                {},
                {},
                {"s": "s"},
                "output_parameters must be a dictionary with string keys and values which "
                "are either a type, an HpsOutputFileSpecification or an HpsOutputDirectorySpecification.",
            ),
        ],
    )
    def test_start_hps_parametric_study_raises_error_with_incorrect_arguments(
        self,
        common_input_files: Any,
        input_parameter_values: Any,
        output_parameters: Any,
        expected_error: str,
        monkeypatch: pytest.MonkeyPatch,
    ):
        # we patch here to avoid a connection to the HPS system but allow checking at the start of add_study_to_project
        monkeypatch.setattr(HpsParametricStudyDefinition, "__init__", lambda _, **kwargs: None)  # type: ignore
        with pytest.raises(RuntimeError, match=re.escape(expected_error)):
            HpsParametricStudyProject.start_hps_parametric_study(
                common_input_files,
                input_parameter_values,
                output_parameters,
            )

    @pytest.mark.parametrize(
        ("input_values", "output_parameters", "expected_error"),
        [
            ([], {}, "input_values must be a dictionary."),
            (
                {1: 1},
                {},
                "input_values must be a dictionary with string keys",
            ),
            (
                {},
                [],
                "output_parameters must be a dictionary with string keys and values which "
                "are either a type, an HpsOutputFileSpecification or an HpsOutputDirectorySpecification.",
            ),
            (
                {},
                {1: 1},
                "output_parameters must be a dictionary with string keys and values which "
                "are either a type, an HpsOutputFileSpecification or an HpsOutputDirectorySpecification.",
            ),
            (
                {},
                {"s": "s"},
                "output_parameters must be a dictionary with string keys and values which "
                "are either a type, an HpsOutputFileSpecification or an HpsOutputDirectorySpecification.",
            ),
        ],
    )
    def test_start_hps_job_raises_error_with_incorrect_arguments(
        self,
        input_values: Any,
        output_parameters: Any,
        expected_error: str,
        monkeypatch: pytest.MonkeyPatch,
    ):
        # we patch here to avoid a connection to the HPS system but allow checking at the start of add_study_to_project
        monkeypatch.setattr(HpsParametricStudyDefinition, "__init__", lambda _, **kwargs: None)  # type: ignore
        with pytest.raises(RuntimeError, match=re.escape(expected_error)):
            HpsSimpleProject.start_hps_job(input_values, output_parameters)

    def test_hps_input_file_specification_raises_error_with_incorrect_source(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(HpsParametricStudyDefinition, "__init__", lambda _, **kwargs: None)  # type: ignore
        with pytest.raises(
            RuntimeError,
            match="The source argument of HpsInputFileSpecification must be "
            "a Path or EntityHandle. "
            "The source argument of HpsInputDirectorySpecification must be "
            "an EntityHandle or Path.",
        ):
            HpsSimpleProject.start_hps_job(
                input_values={"x": HpsInputFileSpecification("name")},  # type: ignore
                output_parameters={},  # type: ignore
            )

    @pytest.mark.parametrize("input_type", [HpsInputFileSpecification, HpsInputDirectorySpecification])
    def test_hps_input_file_specification_raises_error_with_incorrect_evaluation_path(
        self,
        input_type: type[HpsInputSourceSpecification[T]],
    ):
        with pytest.raises(
            RuntimeError,
            match=f"The evaluation_path argument of {input_type.__name__} must be None or a string.",
        ):
            input_type(Path(), 1)  # type: ignore

    @pytest.mark.parametrize("output_type", [HpsOutputFileSpecification, HpsOutputDirectorySpecification])
    def test_hps_output_file_specification_raises_error_with_incorrect_evaluation_path(
        self,
        output_type: type[HpsOutputSourceSpecification],
    ):
        with pytest.raises(
            RuntimeError,
            match=f"The evaluation_path argument of {output_type.__name__} must be None or a string.",
        ):
            output_type(1)  # type: ignore

    @pytest.mark.parametrize("output_type", [HpsOutputFileSpecification, HpsOutputDirectorySpecification])
    def test_hps_output_file_specification_raises_error_with_incorrect_collect_interval(
        self,
        output_type: type[HpsOutputSourceSpecification],
    ):
        with pytest.raises(
            RuntimeError,
            match=f"The collect_interval argument of {output_type.__name__} must be a non-negative integer.",
        ):
            output_type(collect_interval=-1)  # type: ignore

    def test_hps_input_dir_non_dir_input_path_raises_error(self, tmp_path: Path):
        temp_file = tmp_path / "file.txt"
        temp_file.touch()
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "The source of HpsInputDirectorySpecification must be a directory, "
                f"but got Path({temp_file}) which does not refer to a directory.",
            ),
        ):
            HpsInputDirectorySpecification(source=temp_file)

    def test_hps_input_dir_non_dir_input_handle_raises_error(self):
        handle = EntityHandle(
            original_name="not_a_dir",
            is_blob=True,
            entity_id=uuid.uuid4(),
            opaque_identifier="opaque_id",
        )
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "The source of HpsInputDirectorySpecification must be a directory, "
                f"but got EntityHandle({handle.original_name}) which does not refer to a directory.",
            ),
        ):
            HpsInputDirectorySpecification(source=handle)


@pytest.mark.parametrize("project_type", [HpsSimpleProject, HpsParametricStudyProject])
def test_hps_compute_resource_sets_custom_hps_info(project_type: type[HpsProject], mocker: pytest_mock.MockerFixture):
    mocked_get_hps_client = mocker.patch.object(HpsParametricStudySystem, "get_hps_client")
    project_type.get_compute_resource_sets(
        hps_server_url="test_url",
        client_id="test_client",
    )
    mocked_get_hps_client.assert_called_once_with(
        hps_server_url="test_url",
        client_id="test_client",
    )
