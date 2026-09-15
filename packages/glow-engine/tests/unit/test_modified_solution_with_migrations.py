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
from typing import Any

from pydantic import ValidationError
import pytest

from ansys.saf.glow._server.exceptions import MalformedSolutionError
from ansys.saf.glow._server.solution import SolutionService
from tests.mocks.solutions import (
    modify_add_field_with_migration,
    modify_add_step_with_migration,
    modify_apply_migration_to_solution_with_migration,
    modify_display_name_with_migration,
    modify_field_default_value_based_on_another_field_with_migration,
    modify_field_type_incompatible_with_migration,
    modify_field_validator_incompatible_with_migration,
    modify_remove_field_with_migration,
    modify_remove_step_with_migration,
    modify_with_failing_migration,
    modify_with_migration_and_validation,
    modify_with_migration_and_validation_check_order,
    modify_with_three_migrations_missing_first,
    modify_with_two_migrations,
)
from tests.unit.conftest import validate_project_model


@pytest.mark.parametrize("with_migration", [True], indirect=True, ids=["with_migrations"])
class TestModifiedSolutionWithMigrations:
    @pytest.mark.parametrize("solution_service", [modify_display_name_with_migration], indirect=True)
    def test_modify_display_name(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert solution_to_update["solution"]["display_name"] == "Original"
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_display_name_with_migration.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
        )
        assert project.solution.display_name == "NotOriginal"
        assert project.solution.version == 3

    @pytest.mark.parametrize("solution_service", [modify_add_field_with_migration], indirect=True)
    def test_add_field(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert "extra_value" not in solution_to_update["solution"]["steps"]["second_step"]
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_add_field_with_migration.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
        )
        assert project.solution.steps.second_step.extra_value == "my_value"
        assert project.solution.version == 3

    @pytest.mark.parametrize("solution_service", [modify_remove_field_with_migration], indirect=True)
    def test_remove_field(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert "unused_value" in solution_to_update["solution"]["steps"]["first_step"]
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_remove_field_with_migration.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
        )
        assert not hasattr(project.solution.steps.first_step, "unused_value")
        assert project.solution.version == 3

    @pytest.mark.parametrize("solution_service", [modify_add_step_with_migration], indirect=True)
    def test_add_step(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert "third_step" not in solution_to_update["solution"]["steps"]
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_add_step_with_migration.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
        )
        assert hasattr(project.solution.steps, "third_step")
        assert project.solution.version == 3

    @pytest.mark.parametrize("solution_service", [modify_remove_step_with_migration], indirect=True)
    def test_remove_step(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert "second_step" in solution_to_update["solution"]["steps"]
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_remove_step_with_migration.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
        )
        assert not hasattr(project.solution.steps, "second_step")
        assert project.solution.version == 3

    @pytest.mark.parametrize(
        "solution_service",
        [modify_field_default_value_based_on_another_field_with_migration],
        indirect=True,
    )
    def test_modify_field_default_value_base_on_another_field_with_migration(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert solution_to_update["solution"]["steps"]["first_step"]["x"] == 88
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_field_default_value_based_on_another_field_with_migration.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
        )
        assert project.solution.steps.first_step.x == 89
        assert project.solution.version == 3

    @pytest.mark.parametrize("solution_service", [modify_field_type_incompatible_with_migration], indirect=True)
    def test_modify_incompatible_field_type_with_migration(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert solution_to_update["solution"]["steps"]["first_step"]["my_string"] == "my_string"
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_field_type_incompatible_with_migration.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
        )
        assert project.solution.steps.first_step.my_string == 5
        assert project.solution.version == 3

    @pytest.mark.parametrize("solution_service", [modify_field_validator_incompatible_with_migration], indirect=True)
    def test_modify_field_default_to_pass_validator_with_migration(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert solution_to_update["solution"]["steps"]["first_step"]["unused_value"] == 0.5
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_field_validator_incompatible_with_migration.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
        )
        assert project.solution.steps.first_step.unused_value == 2
        assert project.solution.version == 3

    @pytest.mark.parametrize("solution_service", [modify_with_two_migrations], indirect=True)
    def test_modify_solution_with_two_migrations(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert solution_to_update["solution"]["steps"]["first_step"]["x"] == 88
        assert "is_new_field" not in solution_to_update["solution"]["steps"]["first_step"]
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_with_two_migrations.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
        )
        assert project.solution.steps.first_step.x == 100
        assert project.solution.steps.first_step.is_new_field
        assert project.solution.version == 4

    @pytest.mark.parametrize("solution_service", [modify_with_failing_migration], indirect=True)
    def test_update_solution_version_with_failing_migration_preserves_project_files_dir_on_upgrade(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        new_file = project_files_dir / "new_file.txt"
        new_file.touch()
        error_message = (
            "Could not migrate: migration transformation MigrateWithError failed with error: 'File not found'"
        )
        with pytest.raises(ValidationError, match=error_message):
            validate_project_model(
                modify_with_failing_migration.OriginalSolution,
                solution_to_update,
                solution_service,
                project_files_dir,
            )
        assert project_files_dir.is_dir()
        assert new_file.is_file()

    @pytest.mark.parametrize("solution_service", [modify_with_failing_migration], indirect=True)
    def test_update_solution_version_with_failing_migration_does_not_preserve_project_files_dir_on_import(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        new_file = project_files_dir / "new_file.txt"
        new_file.touch()
        error_message = (
            "Could not migrate: migration transformation MigrateWithError failed with error: 'File not found'"
        )
        with pytest.raises(ValidationError, match=error_message):
            validate_project_model(
                modify_with_failing_migration.OriginalSolution,
                solution_to_update,
                solution_service,
                project_files_dir,
                mode="import",
            )
        assert not project_files_dir.is_dir()

    @pytest.mark.parametrize(
        "automatic_project_migration",
        [True, False],
        ids=["automatic_project_migration_enabled", "automatic_project_migration_disabled"],
    )
    @pytest.mark.parametrize("solution_service", [modify_with_migration_and_validation], indirect=True)
    def test_update_solution_through_migration_and_validation(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert solution_to_update["solution"]["steps"]["first_step"]["my_string"] == "my_string"
        assert "extra_int" not in solution_to_update["solution"]["steps"]["first_step"]
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        if automatic_project_migration:
            project = validate_project_model(
                modify_with_migration_and_validation.OriginalSolution,
                solution_to_update,
                solution_service,
                project_files_dir,
                automatic_project_migration=automatic_project_migration,
            )
            assert project.solution.steps.first_step.my_string == 88
            assert project.solution.steps.first_step.extra_int == 50
            assert project.solution.version == 3
        else:
            error_message = (
                "Could not migrate: migration transformation MigrateFieldType failed with error: ''extra_int''"
            )
            with pytest.raises(ValidationError, match=error_message):
                validate_project_model(
                    modify_with_migration_and_validation_check_order.OriginalSolution,
                    solution_to_update,
                    solution_service,
                    project_files_dir,
                    automatic_project_migration,
                )

    @pytest.mark.parametrize("automatic_project_migration", [True], ids=["automatic_project_migration_enabled"])
    @pytest.mark.parametrize("solution_service", [modify_with_migration_and_validation_check_order], indirect=True)
    def test_update_solution_through_migration_and_validation_migrations_are_first(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
        automatic_project_migration: bool,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert solution_to_update["solution"]["steps"]["first_step"]["my_string"] == "my_string"
        assert "extra_int" not in solution_to_update["solution"]["steps"]["first_step"]
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        # Fails because migration transformations are applied first and use a value that is created during
        # the Solution validation.
        error_message = "Could not migrate: migration transformation MigrateFieldType failed with error: ''extra_int''"
        with pytest.raises(ValidationError, match=error_message):
            validate_project_model(
                modify_with_migration_and_validation_check_order.OriginalSolution,
                solution_to_update,
                solution_service,
                project_files_dir,
                automatic_project_migration=automatic_project_migration,
            )

    @pytest.mark.parametrize("solution_service", [modify_with_three_migrations_missing_first], indirect=True)
    def test_update_solution_with_too_old_version(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        assert solution_to_update["solution"]["version"] == 2
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        # Fails because migration transformations are applied first and use a value that is created during
        # the Solution validation.
        error_message = (
            "The solution definition is invalid: the solution version of the project (2) is lower than the lowest "
            "migratable version (3)"
        )
        with pytest.raises(MalformedSolutionError, match=re.escape(error_message)):
            validate_project_model(
                modify_with_three_migrations_missing_first.OriginalSolution,
                solution_to_update,
                solution_service,
                project_files_dir,
            )

    @pytest.mark.parametrize("solution_service", [modify_apply_migration_to_solution_with_migration], indirect=True)
    def test_modify_solution_that_has_migration(
        self,
        solution_service: SolutionService,
        solution_to_update: dict[str, Any],
        tmp_path: Path,
    ):
        assert solution_to_update["solution"]["version"] == 2
        assert solution_to_update["solution"]["migrations"] == [{"version": 1, "migration_transformation": {}}]
        assert solution_to_update["solution"]["steps"]["first_step"]["unused_value"] == 0.5
        project_files_dir = tmp_path / "fake_project_files_dir"
        project_files_dir.mkdir(exist_ok=True)
        project = validate_project_model(
            modify_apply_migration_to_solution_with_migration.OriginalSolution,
            solution_to_update,
            solution_service,
            project_files_dir,
        )
        # The migrations field of the solution to update was overwritten by the latest solution definition,
        # and only the migration from version 2 to 3 was applied
        assert not (project_files_dir / "new_file.py").is_file()
        assert len(project.solution.migrations) == 2
        assert project.solution.steps.first_step.unused_value == 2
        assert project.solution.version == 3
