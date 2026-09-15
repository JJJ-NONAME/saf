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

from fastapi.testclient import TestClient
import pytest

from ansys.saf.glow._config.const import DatabaseType
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._core.field_state import FieldState
from tests.mocks.solutions import (
    modify_add_field_with_migration,
    modify_add_step_with_migration,
    modify_apply_migration_to_solution_with_migration,
    modify_display_name_with_migration,
    modify_field_default_value_based_on_another_field_with_migration,
    modify_field_type_incompatible_with_migration,
    modify_field_validator_incompatible_with_migration,
    modify_original_including_migrations,
    modify_remove_field_with_migration,
    modify_remove_step_with_migration,
    modify_with_failing_migration,
    modify_with_migration_and_validation,
    modify_with_migration_and_validation_check_order,
    modify_with_three_migrations_missing_first,
    modify_with_two_migrations,
)
from tests.unit.conftest import get_project
from tests.unit.routes.conftest import ProjectFixture, upgrade_or_import_project

pytestmark = [
    pytest.mark.parametrize(
        "mock_module_settings",
        [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
        ids=["sqlite", "postgres"],
        indirect=True,
    ),
    pytest.mark.parametrize("source", ["db", "import"]),
]
solution = modify_original_including_migrations


class TestModifiedSolutionWithMigrations:
    @pytest.mark.parametrize("client_func", [modify_display_name_with_migration], indirect=True)
    def test_modify_display_name(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has a different solution display_name
        # THEN: Project can be successfully retrieved but solution display_name is the old one
        project = get_project(client_func, project_fixture.project_name)
        assert project["solution"]["display_name"] == "Original"
        assert project["solution"]["version"] == 2
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: The display name has been updated
        project = get_project(client_func, project_info["name"])
        assert project["solution"]["display_name"] == "NotOriginal"
        assert project["solution"]["version"] == 3

    @pytest.mark.parametrize("client_func", [modify_add_field_with_migration], indirect=True)
    def test_add_field(self, project_fixture: ProjectFixture, client_func: TestClient, safx_path: Path, source: str):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has 1 extra field in one of the steps
        # THEN: Project CANNOT be successfully retrieved, the field is in the data
        response = client_func.get(f"/{project_fixture.project_name}")
        assert response.status_code == 422
        error_message = response.json()["detail"]
        assert "solution.steps.second_step" in error_message
        assert (
            "Value error, extra step fields are not allowed without upgrading the solution. "
            "Extra step fields: {'extra_value'}" in error_message
        )
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: Solution data has field with default value
        project = get_project(client_func, project_info["name"])
        second_step = project["solution"]["steps"]["second_step"]
        assert "extra_value" in second_step
        assert second_step["extra_value"] == "my_value"
        assert second_step["state"]["extra_value"] == FieldState.UPTODATE
        assert project["solution"]["version"] == 3

    @pytest.mark.parametrize("client_func", [modify_remove_field_with_migration], indirect=True)
    def test_remove_field(self, project_fixture: ProjectFixture, client_func: TestClient, safx_path: Path, source: str):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has 1 fewer field in one of the steps
        # THEN: Project CANNOT be retrieved
        response = client_func.get(f"/{project_fixture.project_name}")
        assert response.status_code == 422
        error_message = response.json()["detail"]
        assert "solution.steps.first_step.unused_value" in error_message
        assert "Extra inputs are not permitted" in error_message
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: Project CAN be retrieved and field has been removed
        project = get_project(client_func, project_info["name"])
        assert "unused_value" not in project["solution"]["steps"]["first_step"]
        assert "unused_value" not in project["solution"]["steps"]["first_step"]["state"]
        assert project["solution"]["version"] == 3

    @pytest.mark.parametrize("client_func", [modify_add_step_with_migration], indirect=True)
    def test_add_step(self, project_fixture: ProjectFixture, client_func: TestClient, safx_path: Path, source: str):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has 1 extra step
        # THEN: Project CANNOT be successfully retrieved
        response = client_func.get(f"/{project_fixture.project_name}")
        assert response.status_code == 422
        error_message = response.json()["detail"]
        assert "solution.steps.third_step" in error_message
        assert "Field required" in error_message
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: Project CAN be retrieved and step has been added with default values.
        project = get_project(client_func, project_info["name"])
        assert project["solution"]["steps"]["third_step"]["x"] == 88
        assert project["solution"]["steps"]["third_step"]["state"]["x"] == FieldState.OUTOFDATE
        assert project["solution"]["version"] == 3

    @pytest.mark.parametrize("client_func", [modify_remove_step_with_migration], indirect=True)
    def test_remove_step(self, project_fixture: ProjectFixture, client_func: TestClient, safx_path: Path, source: str):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has 1 fewer step
        # THEN: Project CANNOT be successfully retrieved, but step is still in the data
        response = client_func.get(f"/{project_fixture.project_name}")
        assert response.status_code == 422
        error_message = response.json()["detail"]
        assert "solution.steps.second_step" in error_message
        assert "Extra inputs are not permitted" in error_message
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: Project CAN be retrieved and step has been removed
        project = get_project(client_func, project_info["name"])
        assert "second_step" not in project["solution"]["steps"]
        assert project["solution"]["version"] == 3

    @pytest.mark.parametrize(
        "client_func",
        [modify_field_default_value_based_on_another_field_with_migration],
        indirect=True,
    )
    def test_modify_field_default_value_base_on_another_field_with_migration(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that changes the default value for one field
        # THEN: Project can be successfully retrieved, but field value is the old one
        project = get_project(client_func, project_fixture.project_name)
        assert project["solution"]["steps"]["first_step"]["x"] == 88
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: Project CAN be retrieved and step field has been updated.
        project = get_project(client_func, project_info["name"])
        assert project["solution"]["steps"]["first_step"]["x"] == 89
        assert project["solution"]["version"] == 3

    @pytest.mark.parametrize("client_func", [modify_field_type_incompatible_with_migration], indirect=True)
    def test_modify_incompatible_field_type_with_migration(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has a new field type, incompatible with the old one
        # THEN: Project cannot be successfully retrieved
        assert client_func.get(f"/{project_fixture.project_name}").status_code == 422
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: Project CAN be retrieved and step field has been updated.
        project = get_project(client_func, project_info["name"])
        assert project["solution"]["steps"]["first_step"]["my_string"] == 5
        assert project["solution"]["version"] == 3

    @pytest.mark.parametrize("client_func", [modify_field_validator_incompatible_with_migration], indirect=True)
    def test_modify_field_default_to_pass_validator_with_migration(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that adds a validator to one of the step fields
        #       that invalidates the old default value
        # THEN: Project cannot be retrieved
        assert client_func.get(f"/{project_fixture.project_name}").status_code == 422
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: Project CAN be retrieved and step field has a valid value
        project = get_project(client_func, project_info["name"])
        assert project["solution"]["steps"]["first_step"]["unused_value"] == 2
        assert project["solution"]["version"] == 3

    @pytest.mark.parametrize("client_func", [modify_with_two_migrations], indirect=True)
    def test_modify_solution_with_two_migrations(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has a new field type, incompatible with the old one
        # THEN: Project cannot be successfully retrieved
        assert client_func.get(f"/{project_fixture.project_name}").status_code == 422
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: Project CAN be retrieved and step fields and version have been updated.
        project = get_project(client_func, project_info["name"])
        assert project["solution"]["steps"]["first_step"]["x"] == 100
        assert project["solution"]["steps"]["first_step"]["my_string"] == 5
        assert project["solution"]["steps"]["first_step"]["is_new_field"]
        assert project["solution"]["version"] == 4

    @pytest.mark.parametrize("client_func", [modify_with_failing_migration], indirect=True)
    def test_update_solution_version_with_failing_migration_preserves_project_files_dir_on_upgrade(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        source: str,
    ):
        if source == "import":
            pytest.skip(reason="Project files directory is not preserved on import.")
        # GIVEN: A project created from a original solution including a file in the project files directory
        # WHEN: Using a modified version of the solution that has a failing migration
        new_file = project_fixture.project_files_dir / "new_file.py"
        new_file.touch()
        # THEN: Project cannot be successfully retrieved
        assert client_func.get(f"/{project_fixture.project_name}").status_code == 422
        # WHEN: Upgrading/importing
        # THEN: Project cannot be upgraded or imported because of the failing migration
        error_message = (
            "Could not migrate: migration transformation MigrateWithError failed with error: 'File not found'"
        )
        response = client_func.post(f"/{project_fixture.project_name}:upgrade")
        assert response.status_code == 422
        assert error_message in response.text
        # THEN: The project files directory is preserved
        assert new_file.is_file()

    @pytest.mark.parametrize(
        "settings",
        [{"glow_enable_automatic_project_migration": True}, {"glow_enable_automatic_project_migration": False}],
        ids=["automatic_solution_upgrade_enabled", "automatic_solution_upgrade_disabled"],
        indirect=True,
    )
    @pytest.mark.parametrize("client_func", [modify_with_migration_and_validation], indirect=True)
    def test_update_solution_through_migration_and_validation(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
        settings: Settings,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has 1 extra field and an incompatible field type change
        # THEN: Project CANNOT be successfully retrieved
        assert client_func.get(f"/{project_fixture.project_name}").status_code == 422
        # WHEN: Upgrading/importing
        if settings.glow_enable_automatic_project_migration:
            # THEN: Project CAN be retrieved and step has been added with default values.
            project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
            assert project_info is not None
            project = get_project(client_func, project_info["name"])
            assert project["solution"]["steps"]["first_step"]["my_string"] == 88
            assert project["solution"]["steps"]["first_step"]["extra_int"] == 50
            assert project["solution"]["version"] == 3
        else:
            # THEN: it fails because automatic schema upgrade is disabled so the field is not added
            error_message = "Step 'first_step' is missing fields ['extra_int'], and contains extra fields"
            upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path, 422, error_message)

    @pytest.mark.parametrize(
        "settings",
        [{"glow_enable_automatic_project_migration": True}],
        ids=["automatic_solution_upgrade_enabled"],
        indirect=True,
    )
    @pytest.mark.parametrize("client_func", [modify_with_migration_and_validation_check_order], indirect=True)
    def test_update_solution_through_migration_and_validation_migrations_are_first(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has 1 extra field and an incompatible field type change
        # THEN: Project CANNOT be successfully retrieved
        assert client_func.get(f"/{project_fixture.project_name}").status_code == 422
        # WHEN: Upgrading/importing
        # THEN: Fails because migration transformations are applied first and use a value that is created during
        #       the Solution validation.
        if source == "db":
            response = client_func.post(f"/{project_fixture.project_name}:upgrade")
        else:
            with safx_path.open("rb") as f:
                response = client_func.post(
                    "/projects:import",
                    files={"safx_file": f},
                    data={"display_name": "Unused Display Name"},
                )
        assert response.status_code == 422
        assert (
            "Could not migrate: migration transformation MigrateFieldType failed with error: ''extra_int''"
            in response.text
        )

    @pytest.mark.parametrize("client_func", [modify_with_three_migrations_missing_first], indirect=True)
    def test_update_solution_with_too_old_version(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution to upgrade/import a solution of a version that is not
        #       covered by the migrations
        # THEN: Project CANNOT be successfully retrieved
        assert client_func.get(f"/{project_fixture.project_name}").status_code == 422

        # WHEN: Upgrading/importing
        # THEN: Fails because no migration transformations applies to the version of the solution to update
        if source == "db":
            response = client_func.post(f"/{project_fixture.project_name}:upgrade")
        else:
            with safx_path.open("rb") as f:
                response = client_func.post(
                    "/projects:import",
                    files={"safx_file": f},
                    data={"display_name": "Unused Display Name"},
                )
        assert response.status_code == 500
        assert (
            "The solution definition is invalid: the solution version of the project (2) is lower than the lowest "
            "migratable version (3)"
        ) in response.text

    @pytest.mark.parametrize("client_func", [modify_apply_migration_to_solution_with_migration], indirect=True)
    def test_modify_solution_that_has_migration(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has a new field type, incompatible with the old one
        # THEN: Project cannot be successfully retrieved
        assert client_func.get(f"/{project_fixture.project_name}").status_code == 422
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: The migrations field of the solution to update was overwritten by the latest solution definition,
        #       and only the migration from version 2 to 3 was applied
        project = get_project(client_func, project_info["name"])
        if source == "db":
            new_file = project_fixture.project_files_dir / "new_file.py"
        else:
            project_id: str = project["name"].split("/")[-1]
            new_file = project_fixture.project_files_path / project_id / "new_file.py"
        assert not new_file.is_file()
        assert project["solution"]["steps"]["first_step"]["unused_value"] == 2
        assert project["solution"]["version"] == 3
