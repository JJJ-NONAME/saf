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

import copy
from pathlib import Path
import re
from typing import Any

from pydantic import ValidationError
import pytest

from ansys.saf.glow._server.models import ProjectModel
from ansys.saf.glow._server.solution import SolutionService
from tests.mocks.solutions import (
    modify_add_field,
    modify_add_step,
    modify_display_name,
    modify_field_default_value,
    modify_field_type_compatible,
    modify_field_type_incompatible,
    modify_field_validator_compatible,
    modify_field_validator_incompatible,
    modify_file_solution_name,
    modify_remove_field,
    modify_remove_step,
    modify_version,
)
from tests.unit.conftest import validate_project_model
from tests.unit.contruct_migration_context import get_construct_migration_context


@pytest.mark.parametrize(
    "automatic_project_migration",
    [True, False],
    ids=["automatic_project_migration_enabled", "automatic_project_migration_disabled"],
)
@pytest.mark.parametrize("with_migration", [False], indirect=True, ids=["without_migrations"])
class TestModifiedSolution:
    @pytest.mark.parametrize("solution_service", [modify_version], indirect=True)
    def test_modify_version(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert solution_to_update["solution"]["version"] == 1
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_version.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
            automatic_project_migration,
        )
        assert project.solution.version == 2

    @pytest.mark.parametrize("solution_service", [modify_display_name], indirect=True)
    def test_modify_display_name(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert solution_to_update["solution"]["display_name"] == "Original"
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_display_name.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
            automatic_project_migration,
        )
        assert project.solution.display_name == "NotOriginal"

    @pytest.mark.parametrize("solution_service", [modify_add_field], indirect=True)
    def test_add_field(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert "extra_value" not in solution_to_update["solution"]["steps"]["second_step"]
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        if automatic_project_migration:
            project = validate_project_model(
                modify_add_field.OriginalSolution,
                solution_to_update,
                solution_service,
                project_files_dir,
                automatic_project_migration,
            )
            assert project.solution.steps.second_step.extra_value == "my_value"
        else:
            with pytest.raises(
                ValidationError,
                match=re.escape("Step 'second_step' is missing fields ['extra_value'], and contains extra fields []"),
            ):
                project = validate_project_model(
                    modify_add_field.OriginalSolution,
                    solution_to_update,
                    solution_service,
                    project_files_dir,
                    automatic_project_migration,
                )

    @pytest.mark.parametrize("solution_service", [modify_remove_field], indirect=True)
    def test_remove_field(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert "unused_value" in solution_to_update["solution"]["steps"]["first_step"]
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        if automatic_project_migration:
            project = validate_project_model(
                modify_remove_field.OriginalSolution,
                solution_to_update,
                solution_service,
                project_files_dir,
                automatic_project_migration,
            )
            assert not hasattr(project.solution.steps.first_step, "unused_value")
        else:
            with pytest.raises(
                ValidationError,
                match=re.escape("Step 'first_step' is missing fields [], and contains extra fields ['unused_value']"),
            ):
                project = validate_project_model(
                    modify_remove_field.OriginalSolution,
                    solution_to_update,
                    solution_service,
                    project_files_dir,
                    automatic_project_migration,
                )

    @pytest.mark.parametrize("solution_service", [modify_add_step], indirect=True)
    def test_add_step(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert "third_step" not in solution_to_update["solution"]["steps"]
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        if automatic_project_migration:
            project = validate_project_model(
                modify_add_step.OriginalSolution,
                solution_to_update,
                solution_service,
                project_files_dir,
                automatic_project_migration,
            )
            assert hasattr(project.solution.steps, "third_step")
        else:
            with pytest.raises(
                ValidationError,
                match=re.escape("Project is missing steps ['third_step'], and contains extra steps []"),
            ):
                project = validate_project_model(
                    modify_add_step.OriginalSolution,
                    solution_to_update,
                    solution_service,
                    project_files_dir,
                    automatic_project_migration,
                )

    @pytest.mark.parametrize("solution_service", [modify_remove_step], indirect=True)
    def test_remove_step(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert solution_to_update["solution"]["version"] == 1
        assert "second_step" in solution_to_update["solution"]["steps"]
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        if automatic_project_migration:
            project = validate_project_model(
                modify_remove_step.OriginalSolution,
                solution_to_update,
                solution_service,
                project_files_dir,
                automatic_project_migration,
            )
            assert not hasattr(project.solution.steps, "second_step")
        else:
            with pytest.raises(
                ValidationError,
                match=re.escape("Project is missing steps [], and contains extra steps ['second_step']"),
            ):
                project = validate_project_model(
                    modify_remove_step.OriginalSolution,
                    solution_to_update,
                    solution_service,
                    project_files_dir,
                    automatic_project_migration,
                )

    @pytest.mark.parametrize("solution_service", [modify_field_default_value], indirect=True)
    def test_attempt_to_modify_field_default_value_does_not_work(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert solution_to_update["solution"]["steps"]["first_step"]["x"] == 88
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = ProjectModel[modify_field_default_value.OriginalSolution].model_validate(
            copy.deepcopy(solution_to_update),
            context={
                "mode": "upgrade",
                "default_solution": solution_service.default_instance,
                "migration_context_constructor": get_construct_migration_context(project_files_dir),
                "automatic_project_migration": automatic_project_migration,
            },
        )
        assert project.solution.steps.first_step.x == 88

    @pytest.mark.parametrize("solution_service", [modify_field_type_compatible], indirect=True)
    def test_modify_compatible_field_type(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert solution_to_update["solution"]["steps"]["first_step"]["x"] == 88
        assert isinstance(solution_to_update["solution"]["steps"]["first_step"]["x"], int)
        assert solution_to_update["solution"]["steps"]["first_step"]["str_int"] == "1"
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = ProjectModel[modify_field_type_compatible.OriginalSolution].model_validate(
            copy.deepcopy(solution_to_update),
            context={
                "mode": "upgrade",
                "default_solution": solution_service.default_instance,
                "migration_context_constructor": get_construct_migration_context(project_files_dir),
                "automatic_project_migration": automatic_project_migration,
            },
        )
        assert project.solution.steps.first_step.x == 88
        assert isinstance(project.solution.steps.first_step.x, float)
        assert project.solution.steps.first_step.str_int == 1

    @pytest.mark.parametrize("solution_service", [modify_field_type_incompatible], indirect=True)
    def test_attempt_to_modify_incompatible_field_type_fails(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert solution_to_update["solution"]["steps"]["first_step"]["my_string"] == "my_string"
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        with pytest.raises(
            ValidationError,
            match="Input should be a valid integer, unable to parse string as an integer",
        ):
            ProjectModel[modify_field_type_incompatible.OriginalSolution].model_validate(
                copy.deepcopy(solution_to_update),
                context={
                    "mode": "upgrade",
                    "default_solution": solution_service.default_instance,
                    "migration_context_constructor": get_construct_migration_context(project_files_dir),
                    "automatic_project_migration": automatic_project_migration,
                },
            )

    @pytest.mark.parametrize("solution_service", [modify_field_validator_incompatible], indirect=True)
    def test_modify_field_validator_incompatible(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert solution_to_update["solution"]["steps"]["first_step"]["unused_value"] == 0.5
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        with pytest.raises(ValidationError, match="0.5 must be greater than 1"):
            ProjectModel[modify_field_validator_incompatible.OriginalSolution].model_validate(
                copy.deepcopy(solution_to_update),
                context={
                    "mode": "upgrade",
                    "default_solution": solution_service.default_instance,
                    "migration_context_constructor": get_construct_migration_context(project_files_dir),
                    "automatic_project_migration": automatic_project_migration,
                },
            )

    @pytest.mark.parametrize("solution_service", [modify_field_validator_compatible], indirect=True)
    def test_modify_field_validator_compatible(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert solution_to_update["solution"]["steps"]["first_step"]["unused_value"] == 0.5
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = ProjectModel[modify_field_validator_compatible.OriginalSolution].model_validate(
            copy.deepcopy(solution_to_update),
            context={
                "mode": "upgrade",
                "default_solution": solution_service.default_instance,
                "migration_context_constructor": get_construct_migration_context(project_files_dir),
                "automatic_project_migration": automatic_project_migration,
            },
        )
        assert project.solution.steps.first_step.unused_value == 0.5

    @pytest.mark.parametrize("solution_service", [modify_file_solution_name], indirect=True)
    def test_attempt_to_validate_solution_a_using_compatible_solution_b(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert solution_to_update["solution"]["steps"]["first_step"]["unused_value"] == 0.5
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        error_message = (
            "The type of the Solution to validate 'OriginalSolution' does not match "
            "the current Solution type 'NotOriginalSolution'."
        )
        with pytest.raises(ValidationError, match=error_message):
            ProjectModel[modify_file_solution_name.NotOriginalSolution].model_validate(
                copy.deepcopy(solution_to_update),
                context={
                    "mode": "upgrade",
                    "default_solution": solution_service.default_instance,
                    "migration_context_constructor": get_construct_migration_context(project_files_dir),
                    "automatic_project_migration": automatic_project_migration,
                },
            )
