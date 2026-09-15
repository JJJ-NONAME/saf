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

from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from unittest import mock

from fastapi.testclient import TestClient
import pytest

from ansys.saf.glow._config.const import DatabaseType
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._core.field_state import FieldState
from ansys.saf.glow._executor.method_runner import MethodRunner
from tests.mocks.solutions import (
    modify_add_field,
    modify_add_old_step_back_with_incompatible_type,
    modify_add_step,
    modify_add_transaction,
    modify_display_name,
    modify_field_default_value,
    modify_field_type_compatible,
    modify_field_type_incompatible,
    modify_field_validator_compatible,
    modify_field_validator_incompatible,
    modify_file_solution_name,
    modify_original,
    modify_remove_field,
    modify_remove_step,
    modify_remove_transaction,
    modify_transaction_signature,
    modify_version,
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
    pytest.mark.parametrize(
        "settings",
        [{"glow_enable_automatic_project_migration": True}, {"glow_enable_automatic_project_migration": False}],
        ids=["automatic_solution_upgrade_enabled", "automatic_solution_upgrade_disabled"],
        indirect=True,
    ),
]
solution = modify_original


class TestModifiedSolution:
    @pytest.mark.parametrize("source", ["db", "import"])
    @pytest.mark.parametrize("client_func", [modify_display_name], indirect=True)
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
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: The display name has been updated
        project = get_project(client_func, project_info["name"])
        assert project["solution"]["display_name"] == "NotOriginal"

    @pytest.mark.parametrize("source", ["db", "import"])
    @pytest.mark.parametrize("client_func", [modify_version], indirect=True)
    def test_modify_version(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has a different solution version
        # THEN: Project can be successfully retrieved but solution version is the old one
        project = get_project(client_func, project_fixture.project_name)
        assert project["solution"]["version"] == 1
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: The version has been updated
        project = get_project(client_func, project_info["name"])
        assert project["solution"]["version"] == 2

    @pytest.mark.parametrize("source", ["db", "import"])
    @pytest.mark.parametrize("client_func", [modify_add_field], indirect=True)
    def test_add_field(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
        settings: Settings,
    ):
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
        if settings.glow_enable_automatic_project_migration:
            # THEN: Solution data has the new field with default value
            project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
            assert project_info is not None
            project = get_project(client_func, project_info["name"])
            second_step = project["solution"]["steps"]["second_step"]
            assert "extra_value" in second_step
            assert second_step["extra_value"] == "my_value"
            assert second_step["state"]["extra_value"] == FieldState.UPTODATE
        else:
            # THEN: it fails because automatic schema upgrade is disabled so the field is not added
            error_message = "Step 'second_step' is missing fields ['extra_value'], and contains extra fields []"
            upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path, 422, error_message)

    @pytest.mark.parametrize("source", ["db", "import"])
    @pytest.mark.parametrize("client_func", [modify_remove_field], indirect=True)
    def test_remove_field(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
        settings: Settings,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has 1 fewer field in one of the steps
        # THEN: Project CANNOT be retrieved
        response = client_func.get(f"/{project_fixture.project_name}")
        assert response.status_code == 422
        error_message = response.json()["detail"]
        assert "solution.steps.first_step.unused_value" in error_message
        assert "Extra inputs are not permitted" in error_message
        # WHEN: Upgrading/importing
        if settings.glow_enable_automatic_project_migration:
            # THEN: Project CAN be retrieved and field has been removed
            project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
            assert project_info is not None
            project = get_project(client_func, project_info["name"])
            assert "unused_value" not in project["solution"]["steps"]["first_step"]
            assert "unused_value" not in project["solution"]["steps"]["first_step"]["state"]
        else:
            # THEN: it fails because automatic schema upgrade is disabled so the field is not removed
            error_message = "Step 'first_step' is missing fields [], and contains extra fields ['unused_value']"
            upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path, 422, error_message)

    @pytest.mark.parametrize("source", ["db", "import"])
    @pytest.mark.parametrize("client_func", [modify_add_step], indirect=True)
    def test_add_step(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
        settings: Settings,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has 1 extra step
        # THEN: Project CANNOT be successfully retrieved
        response = client_func.get(f"/{project_fixture.project_name}")
        assert response.status_code == 422
        error_message = response.json()["detail"]
        assert "solution.steps.third_step" in error_message
        assert "Field required" in error_message
        # WHEN: Upgrading/importing
        if settings.glow_enable_automatic_project_migration:
            # THEN: Project CAN be retrieved and step has been added with default values.
            project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
            assert project_info is not None
            project = get_project(client_func, project_info["name"])
            assert project["solution"]["steps"]["third_step"]["x"] == 88
            assert project["solution"]["steps"]["third_step"]["state"]["x"] == FieldState.OUTOFDATE
        else:
            # THEN: it fails because automatic schema upgrade is disabled so the step is not added
            error_message = "Project is missing steps ['third_step'], and contains extra steps []"
            upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path, 422, error_message)

    @pytest.mark.parametrize("source", ["db", "import"])
    @pytest.mark.parametrize("client_func", [modify_remove_step], indirect=True)
    def test_remove_step(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
        settings: Settings,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has 1 fewer step
        # THEN: Project CANNOT be successfully retrieved, but step is still in the data
        response = client_func.get(f"/{project_fixture.project_name}")
        assert response.status_code == 422
        error_message = response.json()["detail"]
        assert "solution.steps.second_step" in error_message
        assert "Extra inputs are not permitted" in error_message
        # WHEN: Upgrading/importing
        if settings.glow_enable_automatic_project_migration:
            # THEN: Project CAN be retrieved and step has been removed
            project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
            assert project_info is not None
            project = get_project(client_func, project_info["name"])
            assert "second_step" not in project["solution"]["steps"]
        else:
            # THEN: it fails because automatic schema upgrade is disabled so the step is not added
            error_message = "Project is missing steps [], and contains extra steps ['second_step']"
            upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path, 422, error_message)

    @pytest.mark.parametrize("client_func", [modify_add_transaction], indirect=True)
    def test_add_transaction(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has 1 extra transaction in one of the steps
        # THEN: Project can be successfully retrieved, but transaction is not in the data because they only appear
        #       if they have been previously invoked
        project = get_project(client_func, project_fixture.project_name)
        assert not project["method_states"]

        # WHEN: New transaction can be invoked
        with mock.patch.object(MethodRunner, "invoke"):
            assert (
                client_func.post(f"/{project_fixture.project_name}/steps/first-step:increase-unused-value").status_code
                == 200
            )
        assert (
            client_func.patch(
                f"/{project_fixture.project_name}/steps/first-step:increase-unused-value",
                json={"status": "completed"},
            ).status_code
            == 200
        )

        # THEN: Solution data has the transaction
        project = get_project(client_func, project_fixture.project_name)
        assert project["method_states"]["first_step"]["increase_unused_value"]["status"] == "completed"

    @pytest.mark.parametrize("client_func", [modify_remove_transaction], indirect=True)
    def test_remove_transaction(self, project_fixture: ProjectFixture, client_func: TestClient):
        # GIVEN: A project created from a original solution, and an invoked transaction
        assert (
            project_fixture.client.post(
                f"/{project_fixture.project_name}/steps/first-step:generate-random-string",
            ).status_code
            == 200
        )
        project_info = project_fixture.client.get(f"/{project_fixture.project_name}").json()

        # WHEN: Using a modified version of the solution that has 1 fewer transaction, which was executed previously
        # THEN: Project can be successfully retrieved, but method status is still in the data
        assert project_info == client_func.get(f"/{project_info['name']}").json()
        project = get_project(client_func, project_info["name"])
        assert project["method_states"]["first_step"]["generate_random_string"]["status"] == "completed"

        # WHEN: Doing request that updates the solution data
        assert client_func.patch(f"/{project_info['name']}/steps/first-step", json={"x": 100}).status_code == 200

        # THEN: Solution data still has the transaction info because it's not cleaned up, but the transaction
        #       cannot be executed anymore.
        assert project["method_states"]["first_step"]["generate_random_string"]["status"] == "completed"
        assert client_func.post(f"/{project_info['name']}/steps/first-step:generate-random-string").status_code == 404

    @pytest.mark.parametrize("client_func", [modify_field_default_value], indirect=True)
    def test_modify_field_default_value(self, project_fixture: ProjectFixture, client_func: TestClient):
        # GIVEN: A project created from a original solution
        project_info = project_fixture.properties
        # WHEN: Using a modified version of the solution that changes the default value for one field
        # THEN: Project can be successfully retrieved, but field value is the old one
        assert project_info == client_func.get(f"/{project_fixture.project_name}").json()
        project = get_project(client_func, project_info["name"])
        assert project["solution"]["steps"]["first_step"]["x"] == 88

        # WHEN: Doing request that updates other solution data
        assert (
            client_func.patch(f"/{project_info['name']}/steps/first-step", json={"my_string": "test"}).status_code
            == 200
        )

        # THEN: Solution data still has old value
        project = get_project(client_func, project["name"])
        assert project["solution"]["steps"]["first_step"]["x"] == 88

        # WHEN: Creating a new project of the modified solution
        new_project_info = client_func.post("/projects", json={"display_name": "extra_project"}).json()
        # THEN: Project has the new default_value
        project = get_project(client_func, new_project_info["name"])
        assert project["solution"]["steps"]["first_step"]["x"] == 100

    @pytest.mark.parametrize("source", ["db", "import"])
    @pytest.mark.parametrize("client_func", [modify_field_type_incompatible], indirect=True)
    def test_attempt_to_modify_incompatible_field_type(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has a new field type, non-castable from the old one
        # THEN: Project cannot be successfully retrieved
        assert client_func.get(f"/{project_fixture.project_name}").status_code == 422
        # THEN: Project cannot be upgraded or imported
        if source == "db":
            response = client_func.post(f"/{project_fixture.project_name}:upgrade")
        else:
            with safx_path.open("rb") as f:
                response = client_func.post(
                    "/projects:import",
                    files={"safx_file": f},
                    data={"display_name": "My Solution"},
                )
        error_message = "Input should be a valid integer, unable to parse string as an integer"
        assert error_message in response.text
        assert response.status_code == 422

    @pytest.mark.parametrize("source", ["db", "import"])
    @pytest.mark.parametrize("client_func", [modify_field_type_compatible], indirect=True)
    def test_modify_field_type_compatible(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
        safx_path: Path,
        source: str,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that has a new field type, castable from the old one
        # THEN: Project CAN be successfully retrieved
        assert client_func.get(f"/{project_fixture.project_name}").status_code == 200
        project_info = get_project(client_func, project_fixture.project_name)
        assert project_info["solution"]["steps"]["first_step"]["x"] == 88.0
        assert project_info["solution"]["steps"]["first_step"]["str_int"] == "1"
        # WHEN: Upgrading/importing
        project_info = upgrade_or_import_project(source, client_func, project_fixture.project_name, safx_path)
        assert project_info is not None
        # THEN: Project CAN be retrieved and the step field default value is modified.
        project = get_project(client_func, project_info["name"])
        assert project["solution"]["steps"]["first_step"]["x"] == 88.0
        assert project["solution"]["steps"]["first_step"]["str_int"] == 1

    @pytest.mark.parametrize("client_func", [modify_transaction_signature], indirect=True)
    def test_modify_transaction_signature(self, project_fixture: ProjectFixture, client_func: TestClient):
        # GIVEN: A project created from a original solution and an invoked transaction
        assert client_func.post(f"/{project_fixture.project_name}/steps/first-step:copy-x-to-string").status_code == 200
        project = project_fixture.client.get(f"/{project_fixture.project_name}").json()

        # WHEN: Using a modified version of the solution that modifies that same transaction
        # THEN: Project can be successfully retrieved, and transaction appears as executed
        assert project == client_func.get(f"/{project['name']}").json()
        project_info = get_project(client_func, project["name"])
        assert project_info["method_states"]["first_step"]["copy_x_to_string"]["status"] == "completed"

        # WHEN: Doing request that updates the solution data
        assert client_func.patch(f"/{project['name']}/steps/first-step", json={"x": 100}).status_code == 200

        # THEN: Solution data still has the transaction info, without any sign of being outdated, since
        #       we don't save any information about the transactions themselves in the project.
        project_info = get_project(client_func, project["name"])
        assert project_info["method_states"]["first_step"]["copy_x_to_string"]["status"] == "completed"

    @pytest.mark.parametrize("client_func", [modify_field_validator_incompatible], indirect=True)
    def test_modify_field_validator_incompatible(
        self,
        project_fixture: ProjectFixture,
        client_func: TestClient,
    ):
        # GIVEN: A project created from a original solution
        project = project_fixture.properties

        # WHEN: Using a modified version of the solution that adds a validator to one of the step fields
        #       that invalidates the old default value
        # THEN: Project cannot be retrieved
        assert client_func.get(f"/{project['name']}").status_code == 422
        # THEN: Project cannot be upgraded
        response = client_func.post(f"/{project['name']}:upgrade")
        assert response.status_code == 422

        # WHEN: Modifying original project to comply with new validator
        assert (
            project_fixture.client.patch(f"/{project['name']}/steps/first-step", json={"unused_value": 1.5}).status_code
            == 200
        )
        project = project_fixture.client.get(f"/{project['name']}").json()
        # THEN: Project can be successfully retrieved
        assert project == client_func.get(f"/{project['name']}").json()

    @pytest.mark.parametrize("client_func", [modify_field_validator_compatible], indirect=True)
    def test_modify_field_validator_compatible(self, project_fixture: ProjectFixture, client_func: TestClient):
        # GIVEN: A project created from a original solution
        # WHEN: Using a modified version of the solution that adds a validator to one of the step fields
        #       that validates the old default value
        # THEN: Project can be retrieved
        assert client_func.get(f"/{project_fixture.project_name}").status_code == 200

    def test_sequence_of_modifications_that_cannot_be_accumulated(
        self,
        get_client_func: Callable[[ModuleType], TestClient],
        settings: Settings,
    ):
        if not settings.glow_enable_automatic_project_migration:
            pytest.skip(reason="This test exposes the issues of automatic schema upgrade. Skipping when disabled.")
        # original solution has second step
        with get_client_func(modify_original) as c_v1:
            project_v1 = c_v1.post("/projects", json={"display_name": "Project V1"}).json()
            c_v1.get(f"/{project_v1['name']}/steps/second-step").raise_for_status()
            assert c_v1.get(f"/{project_v1['name']}/steps/second-step").json()["my_string"] == "my_string"

        # first modification removes the step
        with get_client_func(modify_remove_step) as c_v1_1:
            project_v1_1 = c_v1_1.post("/projects", json={"display_name": "Project V1_1"}).json()
            assert c_v1_1.get(f"/{project_v1_1['name']}/steps/second-step").status_code == 404

        # second modification brings back the step but one of the step fields has an incompatible type
        with get_client_func(modify_add_old_step_back_with_incompatible_type) as c_v2:
            # project from v1_1 CAN be upgraded and the step is added back with the field having the new type
            c_v2.post(f"/{project_v1_1['name']}:upgrade").raise_for_status()
            c_v2.get(f"/{project_v1_1['name']}/steps/second-step").raise_for_status()
            assert c_v2.get(f"/{project_v1_1['name']}/steps/second-step").json()["my_string"] == 5
            # project from v1 CANNOT be upgraded
            assert c_v2.post(f"/{project_v1['name']}:upgrade").status_code == 422

    @pytest.mark.parametrize("client_func", [modify_file_solution_name], indirect=True)
    def test_attempt_to_import_solution_a_using_compatible_solution_b(
        self,
        client_func: TestClient,
        safx_path: Path,
    ):
        # GIVEN: A project created from a original solution
        # WHEN: Importing a solution with a different solution subclass name but is otherwise compatible
        error_message = (
            "The type of the Solution to validate 'OriginalSolution' does not match "
            "the current Solution type 'NotOriginalSolution'."
        )
        with safx_path.open("rb") as f:
            response = client_func.post(
                "/projects:import",
                files={"safx_file": f},
                data={"display_name": "Unused Display Name"},
            )
        assert response.status_code == 422
        assert error_message in response.text
