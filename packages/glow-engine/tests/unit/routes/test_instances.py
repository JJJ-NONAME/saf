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

from fastapi import status
from httpx2 import Response
import pytest
from pytest_mock import MockerFixture

from ansys.saf.glow._config.const import DatabaseType
from ansys.saf.glow._crud.crud import Crud
import tests.mocks.solutions.instances as instances
from tests.unit.routes.conftest import ProjectFixture

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = instances


def _check_not_found(response: Response) -> None:
    assert response.status_code == 404
    assert response.json()["detail"] == "Instance 'x_y' on Step 'instance_step' is not found."


def _check_status(response: Response, expected_status_code: int = 200) -> None:
    message = f"Expected {expected_status_code}. Actual status {response.status_code}. Response text {response.text}"
    assert response.status_code == expected_status_code, message


def _check_response(
    response: Response,
    instance_payload: dict[str, str],
) -> None:
    _check_status(response)
    json = response.json()
    assert isinstance(json, dict)
    assert set(json.keys()) == {  # pyright: ignore[reportUnknownArgumentType]
        "pim_name",
        "name",
        "service_name",
        "max_execution_time",
        "recovery_state_info",
        "product_version",
    }
    assert json["pim_name"] == instance_payload["pim_name"]
    assert json["name"] == instance_payload["name"]
    assert json["service_name"] == instance_payload["service_name"]
    assert json["product_version"] == instance_payload["product_version"]
    assert json["max_execution_time"] == int(instance_payload["max_execution_time"])
    assert json["recovery_state_info"] == instance_payload["recovery_state_info"]


def _check_invalid_name_response(response: Response, invalid_field: str) -> None:
    _check_status(response, 422)
    response_text = response.text
    assert "string_pattern_mismatch" in response_text
    assert invalid_field in response_text
    assert "String should match pattern" in response_text


def test_getting_instance_when_not_set_results_in_not_found(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    instance_url, _ = get_instance_payload(project_fixture)
    response = project_fixture.client.get(instance_url)
    _check_not_found(response)


def test_getting_instance_during_creation_when_not_set_results_in_no_content(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    instance_url, _ = get_instance_payload(project_fixture)
    response = project_fixture.client.get(instance_url, params={"ignore_not_found": True})
    _check_status(response, expected_status_code=204)


@pytest.mark.parametrize("pim_name", ["instances/XYZ", ""])
def test_getting_instance_when_set_results_in_set_value(
    pim_name: str,
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - instance playload
    instance_url, instance_payload = get_instance_payload(project_fixture)
    instance_payload["pim_name"] = pim_name

    # WHEN - posting the payload
    response = project_fixture.client.post(instance_url, json=instance_payload)

    # THEN - the response returns the given pim_name
    _check_response(response, instance_payload)

    # WHEN - getting the same instance
    response = project_fixture.client.get(instance_url)

    # THEN - the response returns the given pim_name
    _check_response(response, instance_payload)


def test_getting_instance_when_set_then_deleted_results_in_not_found(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - existing instance
    instance_url, instance_payload = get_instance_payload(project_fixture)

    response = project_fixture.client.post(instance_url, json=instance_payload)
    _check_status(response)

    # WHEN - deleting the instance
    response = project_fixture.client.delete(instance_url)

    # THEN - the response status is OK
    _check_status(response)

    # AND - getting the instance results in not found
    response = project_fixture.client.get(instance_url)
    _check_not_found(response)


def test_deleting_instance_removes_instance_state_directory(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - existing instance with a matching state directory on disk
    instance_url, instance_payload = get_instance_payload(project_fixture)
    response = project_fixture.client.post(instance_url, json=instance_payload)
    _check_status(response)

    state_dirname = instance_payload["recovery_state_info"]["product_instance_state_dirname"]  # type: ignore
    state_dir = project_fixture.project_files_dir / state_dirname
    state_file = state_dir / "project.txt"
    state_dir.mkdir(parents=True)
    state_file.write_text("state")

    # WHEN - deleting the instance
    response = project_fixture.client.delete(instance_url)

    # THEN - the response status is OK and the state directory is removed
    _check_status(response)
    assert not state_dir.exists()


def test_deleting_instance_without_recovery_state_info_is_ok(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - existing instance without recovery_state_info
    instance_url, instance_payload = get_instance_payload(project_fixture)
    instance_payload["recovery_state_info"] = None  # type: ignore
    response = project_fixture.client.post(instance_url, json=instance_payload)
    _check_status(response)

    # WHEN - deleting the instance
    response = project_fixture.client.delete(instance_url)

    # THEN - delete succeeds and instance is removed
    _check_status(response)
    response = project_fixture.client.get(instance_url)
    _check_not_found(response)


def test_deleting_instance_with_non_existing_state_directory_is_ok(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - existing instance whose recovery dir does not exist on disk
    instance_url, instance_payload = get_instance_payload(project_fixture)
    missing_state_dirname = "is_non_existing_directory"
    instance_payload["recovery_state_info"]["product_instance_state_dirname"] = missing_state_dirname  # type: ignore
    response = project_fixture.client.post(instance_url, json=instance_payload)
    _check_status(response)

    missing_state_dir = project_fixture.project_files_dir / missing_state_dirname
    assert not missing_state_dir.exists()

    # WHEN - deleting the instance
    response = project_fixture.client.delete(instance_url)

    # THEN - delete succeeds even though the state directory never existed
    _check_status(response)
    response = project_fixture.client.get(instance_url)
    _check_not_found(response)


def test_deleting_instance_when_state_directory_removal_fails_is_ok(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
    mocker: MockerFixture,
):
    # GIVEN - existing instance with a state directory and a failing rmtree
    instance_url, instance_payload = get_instance_payload(project_fixture)
    failing_state_dirname = "is_failing_delete_dir"
    instance_payload["recovery_state_info"]["product_instance_state_dirname"] = failing_state_dirname  # type: ignore
    response = project_fixture.client.post(instance_url, json=instance_payload)
    _check_status(response)

    failing_state_dir = project_fixture.project_files_dir / failing_state_dirname
    failing_state_dir.mkdir(parents=True, exist_ok=True)
    (failing_state_dir / "marker.txt").write_text("state")

    mocked_rmtree = mocker.patch("ansys.saf.glow._crud.instance_helper.shutil.rmtree", side_effect=OSError("boom"))
    mocked_warning = mocker.patch("ansys.saf.glow._crud.instance_helper.logger.warning")

    # WHEN - deleting the instance
    response = project_fixture.client.delete(instance_url)

    # THEN - delete succeeds despite failing local directory cleanup
    _check_status(response)
    response = project_fixture.client.get(instance_url)
    _check_not_found(response)
    assert failing_state_dir.is_dir()
    mocked_rmtree.assert_called_once_with(failing_state_dir)

    # THEN - warning message is logged
    mocked_warning.assert_called_once()
    warning_message = mocked_warning.call_args[0][0]
    assert "Failed to remove instance state directory" in warning_message
    assert "boom" in warning_message


@pytest.mark.parametrize("state_directory_name", ["../outside_delete_guard", "", "nested_dir/my_second_dir"])
def test_deleting_instance_with_invalid_path_is_ignored(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
    state_directory_name: str,
    mocker: MockerFixture,
):
    # GIVEN - existing instance with traversal-like state directory path
    instance_url, instance_payload = get_instance_payload(project_fixture)
    instance_payload["recovery_state_info"]["product_instance_state_dirname"] = state_directory_name  # type: ignore
    response = project_fixture.client.post(instance_url, json=instance_payload)
    _check_status(response)
    mocked_warning = mocker.patch("ansys.saf.glow._crud.instance_helper.logger.warning")

    # WHEN - deleting the instance
    response = project_fixture.client.delete(instance_url)

    # THEN - delete succeeds
    _check_status(response)
    response = project_fixture.client.get(instance_url)
    _check_not_found(response)

    # THEN - warning message is logged
    mocked_warning.assert_called_once()
    assert mocked_warning.call_args[0][0] == (
        "Skipping state directory deletion because path is not a subdirectory of the project directory: %s"
    )


def test_deleting_instance_keeps_other_instance_state_directories_same_project(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - instance 1 and instance 2 in the same project
    instance1_url, instance1_payload = get_instance_payload(project_fixture)
    instance1_payload["recovery_state_info"]["product_instance_state_dirname"] = "is_instance1_same_project"  # type: ignore
    response = project_fixture.client.post(instance1_url, json=instance1_payload)
    _check_status(response)

    instance2_url = f"{project_fixture.properties['name']}/steps/instance-step/instances/http"
    instance2_payload = dict(instance1_payload)
    instance2_payload["name"] = instance2_url
    instance2_payload["pim_name"] = "instances/XYZ-2"
    instance2_payload["service_name"] = "http"
    instance2_payload["recovery_state_info"]["product_instance_state_dirname"] = "is_instance2_same_project"  # type: ignore
    response = project_fixture.client.post(instance2_url, json=instance2_payload)
    _check_status(response)

    instance1_state_dir = project_fixture.project_files_dir / "is_instance1_same_project"
    instance2_state_dir = project_fixture.project_files_dir / "is_instance2_same_project"
    instance1_state_dir.mkdir(parents=True, exist_ok=True)
    instance2_state_dir.mkdir(parents=True, exist_ok=True)

    # WHEN - deleting instance 1
    response = project_fixture.client.delete(instance1_url)
    _check_status(response)

    # THEN - only instance1 state dir is removed
    assert not instance1_state_dir.exists()
    assert instance2_state_dir.is_dir()


def test_deleting_instance_keeps_other_instance_state_directories_different_project(
    project_fixture: ProjectFixture,
    create_project: Callable[[str, str], Response],
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - instance 1 in one project and instance 1 in another project
    instance1_url, instance1_payload = get_instance_payload(project_fixture)
    instance1_payload["recovery_state_info"]["product_instance_state_dirname"] = "is_instance1_same_project"  # type: ignore
    response = project_fixture.client.post(instance1_url, json=instance1_payload)
    _check_status(response)

    other_project = create_project("project-other", "").json()
    other_instance1_url = f"{other_project['name']}/steps/instance-step/instances/x-y"
    other_instance1_payload = dict(instance1_payload)
    other_instance1_payload["name"] = other_instance1_url
    other_instance1_payload["pim_name"] = "instances/XYZ-3"
    # Keep the same state dir name as instance1 to verify project-level isolation.
    other_instance1_payload["recovery_state_info"]["product_instance_state_dirname"] = "is_instance1_same_project"  # type: ignore
    response = project_fixture.client.post(other_instance1_url, json=other_instance1_payload)
    _check_status(response)

    instance1_state_dir = project_fixture.project_files_dir / "is_instance1_same_project"
    other_project_id = other_project["name"].removeprefix("projects/")
    other_project_state_dir = project_fixture.project_files_path / other_project_id / "is_instance1_same_project"
    instance1_state_dir.mkdir(parents=True, exist_ok=True)
    other_project_state_dir.mkdir(parents=True, exist_ok=True)

    # WHEN - deleting instance 1 in the first project
    response = project_fixture.client.delete(instance1_url)

    # THEN - only instance1 state dir in that project is removed
    _check_status(response)
    assert not instance1_state_dir.exists()
    assert other_project_state_dir.is_dir()


def test_getting_instance_after_update_results_in_updated_value(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - create instance for a given step
    instance_url, instance_payload = get_instance_payload(project_fixture)

    project_fixture.client.post(instance_url, json=instance_payload)

    # WHEN - updating the instance
    new_pim_name = "instances/ABC"
    assert new_pim_name != instance_payload["pim_name"]
    new_instance_payload = dict(instance_payload)
    new_instance_payload["pim_name"] = new_pim_name
    response = project_fixture.client.patch(instance_url, json={"pim_name": new_pim_name})

    # THEN - the response returns the given pim_name
    _check_response(response, new_instance_payload)

    # WHEN - getting the same instance
    response = project_fixture.client.get(instance_url)

    # THEN - the response returns the given pim_name
    _check_response(response, new_instance_payload)


@pytest.mark.parametrize("pim_name", ["XYZ", "instances/"])
def test_create_instance_with_invalid_pim_name(
    pim_name: str,
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - instance playload
    instance_url, instance_payload = get_instance_payload(project_fixture)
    instance_payload["pim_name"] = pim_name

    # WHEN - posting the payload
    response = project_fixture.client.post(instance_url, json=instance_payload)

    # THEN - the request fails
    _check_invalid_name_response(response, "pim_name")


@pytest.mark.parametrize("new_pim_name", ["XYZ", "instances/", ""])
def test_modify_instance_with_invalid_pim_name(
    new_pim_name: str,
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - create instance
    instance_url, instance_payload = get_instance_payload(project_fixture)
    response = project_fixture.client.post(instance_url, json=instance_payload)

    # WHEN - updating the instance with a invalid pim_name
    assert new_pim_name != instance_payload["pim_name"]
    new_instance_payload = dict(instance_payload)
    new_instance_payload["pim_name"] = new_pim_name
    response = project_fixture.client.patch(instance_url, json={"pim_name": new_pim_name})

    # THEN - the request fails
    _check_invalid_name_response(response, "pim_name")


@pytest.mark.parametrize("instance_name", ["test", "projects/", ""])
def test_create_instance_with_invalid_name(
    instance_name: str,
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - instance payload with invalid instance name
    instance_url, instance_payload = get_instance_payload(project_fixture)
    instance_payload["name"] = instance_name

    # WHEN - posting the payload
    response = project_fixture.client.post(instance_url, json=instance_payload)

    # THEN - the request fails
    _check_invalid_name_response(response, "name")


@pytest.mark.usefixtures("project_dir")
def test_import_project_including_instances(
    project_fixture: ProjectFixture,
    safx_path: Path,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    """Add instances to project, export the project, then import the project."""
    # Add instances to the project
    original_project_name = project_fixture.properties["name"]
    instance_url, instance_payload = get_instance_payload(project_fixture)
    response = project_fixture.client.post(instance_url, json=instance_payload)
    _check_response(response, instance_payload)

    # Export the project as safx file.
    response = project_fixture.client.get(f"/{original_project_name}:export")
    safx_path.write_bytes(response.content)

    # Import the safx file
    with safx_path.open("rb") as f:
        response = project_fixture.client.post(
            "/projects:import",
            files={"safx_file": f},
            data={"display_name": "my_project"},
        )
    assert response.status_code == status.HTTP_200_OK
    new_project_name = response.json()["name"]
    new_instance_url = instance_url.replace(original_project_name, new_project_name)

    # Verify that the instances were cleaned up correctly in the imported project.
    original_instance = project_fixture.client.get(instance_url).json()
    new_instance = project_fixture.client.get(new_instance_url).json()

    # The service name and the product version should be the same as in the original project.
    assert original_instance["service_name"] == new_instance["service_name"]
    assert original_instance["product_version"] == new_instance["product_version"]

    # The pim_name should be an empty string;
    # so that the new project does not use the pim instance of the original project.
    assert original_instance["pim_name"] != new_instance["pim_name"]
    assert new_instance["pim_name"] == ""

    # The instance name should be not the same as the one in the original project.
    assert original_instance["name"] != new_instance["name"]

    # The instance name should include the new project name.
    assert new_instance["name"].startswith(new_project_name)


def test_remove_project_removes_instance_and_instance_state_dir(
    mocker: MockerFixture,
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    # GIVEN - existing instance
    instance_url, instance_payload = get_instance_payload(project_fixture)

    response = project_fixture.client.post(instance_url, json=instance_payload)
    assert response.status_code == status.HTTP_200_OK

    state_dirname = instance_payload["recovery_state_info"]["product_instance_state_dirname"]  # type: ignore
    state_dir = project_fixture.project_files_dir / state_dirname
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "marker.txt").write_text("state")
    assert state_dir.is_dir()

    # WHEN - deleting the project
    project_url = project_fixture.properties["name"]

    shutdown_instance_mock = mocker.patch.object(Crud, "_shutdown_project_instances")

    # THEN - instance is found before removing the project
    response = project_fixture.client.get(instance_url)
    instance_name = response.json()["pim_name"]
    assert response.status_code == status.HTTP_200_OK

    response = project_fixture.client.delete(project_url)
    assert response.status_code == status.HTTP_200_OK

    # THEN - instance is shutdown
    shutdown_instance_mock.assert_called_once()
    assert shutdown_instance_mock.call_args_list[0][0][0] == [instance_name]

    # THEN - instance can't be found
    response = project_fixture.client.get(instance_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # THEN - instance state dir is removed with the project directory
    assert not project_fixture.project_files_dir.exists()
    assert not state_dir.exists()


def test_get_instance_nonexistent_step_returns_404(project_fixture: ProjectFixture):
    """Tests that GET instance on a nonexistent step returns a 404 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/nonexistent-step/instances/x-y"
    response = project_fixture.client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_get_instance_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Tests that GET instance with a nonexistent project_id returns a 404 error."""
    url = "projects/nonexistent_project_id/steps/instance-step/instances/x-y"
    response = project_fixture.client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."


def test_post_instance_nonexistent_step_returns_404(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    """Tests that POST instance with a nonexistent step returns a 404 error."""
    project_name = project_fixture.properties["name"]
    _, instance_payload = get_instance_payload(project_fixture)
    url = f"{project_name}/steps/nonexistent-step/instances/x-y"
    instance_payload["name"] = url
    response = project_fixture.client.post(url, json=instance_payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_post_instance_nonexistent_project_returns_404(
    project_fixture: ProjectFixture,
    get_instance_payload: Callable[[ProjectFixture], tuple[str, dict[str, str]]],
):
    """Tests that POST instance with a nonexistent project_id returns a 404 error."""
    _, instance_payload = get_instance_payload(project_fixture)
    url = "projects/nonexistent_project_id/steps/instance-step/instances/x-y"
    instance_payload["name"] = url
    response = project_fixture.client.post(url, json=instance_payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."


def test_patch_instance_nonexistent_step_returns_404(project_fixture: ProjectFixture):
    """Tests that PATCH instance with a nonexistent step returns a 404 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/nonexistent-step/instances/x-y"
    response = project_fixture.client.patch(url, json={"pim_name": "instances/ABC"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_patch_instance_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Tests that PATCH instance with a nonexistent project_id returns a 404 error."""
    url = "projects/nonexistent_project_id/steps/instance-step/instances/x-y"
    response = project_fixture.client.patch(url, json={"pim_name": "instances/ABC"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."


def test_delete_instance_nonexistent_step_returns_404(project_fixture: ProjectFixture):
    """Tests that DELETE instance with a nonexistent step returns a 404 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/nonexistent-step/instances/x-y"
    response = project_fixture.client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_delete_instance_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Tests that DELETE instance with a nonexistent project_id returns a 404 error."""
    url = "projects/nonexistent_project_id/steps/instance-step/instances/x-y"
    response = project_fixture.client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."
