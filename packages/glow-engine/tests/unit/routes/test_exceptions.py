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
import time
from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
import pytest

from ansys.saf.glow._config.const import DatabaseType
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._core.method_status import MethodStatus
from ansys.saf.glow._server.exceptions import INTERNAL_ERROR_MESSAGE
import tests.mocks.solutions.exceptions as exceptions
from tests.unit.routes.conftest import ProjectFixture

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = exceptions

BDM_NO_ENTITY_ERROR_MSG = "entity does not exist"


def test_wrong_endpoint_raise_404(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/unexistent-step"
    response = project_fixture.client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


@pytest.mark.usefixtures("settings")
@pytest.mark.parametrize("settings", [{"glow_debug": "True"}], ids=["debug"], indirect=["settings"])
def test_wrong_field_request_raise_422(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/exceptions-step"
    payload = {"x": "wrong_value"}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = response.json()["detail"]
    assert len(detail) == 1
    assert detail[0]["input"] == "wrong_value"
    assert detail[0]["msg"] == "Input should be a valid integer, unable to parse string as an integer"


@pytest.mark.usefixtures("settings")
@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_extra_field_request_raise_422(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/exceptions-step"
    payload = {"not_a_step_field": "not_a_step_field"}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = response.json()["detail"]
    assert len(detail) == 1
    assert detail[0]["input"] == "not_a_step_field"
    assert detail[0]["msg"] == "Extra inputs are not permitted"


def test_wrong_body_request_raise_422(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/exceptions-step"
    payload = "not_json"
    response = project_fixture.client.patch(url, content=payload, headers={"Content-Type": "application/json"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["msg"] == "JSON decode error"


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_wrong_module_import_raise_500(
    project_fixture: ProjectFixture,
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
):
    """
    Test that if a wrong module is imported (or a right module not installed) the
    exception is handled properly by the server
    """

    def raise_module_not_found_err(*args: Any):
        import wrong_module  # noqa: F401  # pyright: ignore[reportUnusedImport, reportMissingImports]

    # In order to reproduce the scepnario where an import error happens,
    # that error must happen during a method execution. Importing wrong_module
    # within a transaction does not reproduce the same scenario, as that exception
    # is handled by the StarletteHTTPException's handler.
    monkeypatch.setattr("ansys.saf.glow._executor.method_runner.MethodRunner._run_method", raise_module_not_found_err)

    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/exceptions-step:no-exception"
    response = project_fixture.client.post(url)

    assert response.status_code == 500

    if settings.glow_debug:
        assert response.json()["detail"].startswith("No module named 'wrong_module'")
    else:
        assert response.json()["detail"] == INTERNAL_ERROR_MESSAGE

    monkeypatch.undo()


error_datasets = [
    (
        "raise-bad-request-error",
        "State of project invalid",
        400,
    ),
    (
        "raise-runtime-error",
        "Runtime Error!",
        500,
    ),
    (
        "raise-wrong-attribute-error",
        "The solution definition is invalid: invalid attribute 'wrong' in ",
        500,
    ),
]


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
@pytest.mark.parametrize(
    ("method_name", "expected_error", "status_code"),
    error_datasets,
)
def test_method_transaction_raise_proper_exception(
    settings: Settings,
    method_name: str,
    expected_error: str,
    status_code: int,
    project_fixture: ProjectFixture,
):
    """Test that exceptions raised during a transaction are properly displayed
    and traceback is hidden or not depending on the debug mode.
    """
    # Arrange
    project_name = project_fixture.properties["name"]
    (project_fixture.project_files_dir / "file.txt").write_text("hello")
    url = f"{project_name}/steps/exceptions-step:{method_name}"
    # Act
    response = project_fixture.client.post(url)
    assert response.status_code == status_code
    actual_error = response.json()["detail"]
    expected_traceback = "Traceback (most recent call last)"
    if settings.glow_debug:
        assert actual_error.startswith(expected_error)
        assert expected_traceback in actual_error
        assert "The above exception was the direct cause of the following exception" not in actual_error
    else:
        if status_code == 500:
            expected_error = INTERNAL_ERROR_MESSAGE
        assert actual_error == expected_error
        assert expected_traceback not in actual_error


def wait_failed(client: TestClient, url: str) -> dict[str, str]:
    attempt = 0
    response = client.get(url=url)
    status = response.json()["status"]
    while status != MethodStatus.Failed and attempt < 10:
        status = response.json()["status"]
        time.sleep(0.1)
        attempt += 1
    return response.json()


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
@pytest.mark.parametrize(("method_name", "expected_error", "status_code"), error_datasets)
def test_long_running_method_transaction_raise_proper_exception(
    settings: Settings,
    method_name: str,
    expected_error: str,
    status_code: int,
    project_fixture: ProjectFixture,
):
    """Test that exceptions raised during a long running transaction are properly displayed
    and traceback is hidden or not depending on the debug mode.
    """
    # Arrange
    project_name = project_fixture.properties["name"]
    (project_fixture.project_files_dir / "file.txt").write_text("hello")
    url = f"{project_name}/steps/exceptions-step:{method_name}-long"
    # Act
    response = project_fixture.client.post(url)
    assert response.status_code == status.HTTP_200_OK
    response = wait_failed(project_fixture.client, url)
    actual_error = response["exception_message"]
    actual_traceback = response["exception_stack"]
    actual_status_code = response["status_code"]
    expected_traceback = "Traceback (most recent call last)"
    assert actual_status_code == status_code
    if settings.glow_debug:
        assert actual_error.startswith(expected_error)
        assert expected_traceback in actual_traceback
        assert "The above exception was the direct cause of the following exception" not in actual_error
    else:
        if status_code == 500:
            expected_error = INTERNAL_ERROR_MESSAGE
        assert actual_traceback is None
        assert actual_error == expected_error


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_transaction_unjsonable_return_value(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:return-unjsonable"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert "Unable to serialize unknown type: <class 'ansys.saf.glow._core.step_spec.StepSpec'>" in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_transaction_wrong_return_value(project_fixture: ProjectFixture):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:wrong-return-value"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "The returned data is invalid."


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_blob_with_no_entity_exception(project_fixture: ProjectFixture):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    entity_url = f"{step_url}/blobs/result"
    # Act
    response = project_fixture.client.get(entity_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == BDM_NO_ENTITY_ERROR_MSG


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_blob_with_fake_entity_exception(project_fixture: ProjectFixture):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    entity_url = f"{step_url}/blobs/fake-entity"
    # Act
    response = project_fixture.client.get(entity_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "The object referenced by the datapath cannot be found: 'fake-entity'"


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_blob_with_directory_entity_exception(project_fixture: ProjectFixture):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:store-directory"
    response = project_fixture.client.post(method_url)
    entity_url = f"{step_url}/blobs/directory"
    # Act
    response = project_fixture.client.get(entity_url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "cannot create stream for directory"


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_cached_of_no_entity(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:raise-get-cached"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert "accessing storage using NO_ENTITY handle" in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_copy_of_no_entity(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:raise-get-copy"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert "accessing storage using NO_ENTITY handle" in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_stream_of_no_entity(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:raise-get-stream-result"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert "accessing storage using NO_ENTITY handle" in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_parent_of_no_entity(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:raise-get-parent"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert BDM_NO_ENTITY_ERROR_MSG in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_children_with_file_entity(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:store-result"
    response = project_fixture.client.post(method_url)
    method_url = f"{step_url}:raise-get-children-result"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert "" in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_child_with_file_entity(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:store-result"
    response = project_fixture.client.post(method_url)
    method_url = f"{step_url}:raise-get-child"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert "" in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_cached_with_removed_entity_file(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:store-result"
    response = project_fixture.client.post(method_url)
    method_url = f"{step_url}:get-cached-result"
    response = project_fixture.client.post(method_url)
    relative_path = Path(response.json())
    relative_path.unlink()
    method_url = f"{step_url}:raise-get-child"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert BDM_NO_ENTITY_ERROR_MSG in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_parent_with_removed_entity_file(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:store-result"
    response = project_fixture.client.post(method_url)
    method_url = f"{step_url}:get-cached-result"
    response = project_fixture.client.post(method_url)
    relative_path = Path(response.json())
    relative_path.unlink()
    method_url = f"{step_url}:raise-get-parent"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert BDM_NO_ENTITY_ERROR_MSG in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_stream_with_directory_entity(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:store-directory"
    response = project_fixture.client.post(method_url)
    method_url = f"{step_url}:raise-get-stream-directory"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert "cannot create stream for directory" in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_children_with_removed_entity_directory(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:store-directory"
    response = project_fixture.client.post(method_url)
    method_url = f"{step_url}:get-cached-directory"
    response = project_fixture.client.post(method_url)
    relative_path = Path(response.json())
    relative_path.rmdir()
    method_url = f"{step_url}:raise-get-children-directory"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert BDM_NO_ENTITY_ERROR_MSG in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_get_children_with_file_entity_long_running(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:store-result"
    project_fixture.client.post(method_url)
    method_url = f"{step_url}:raise-get-children-result-long-running"
    # Act
    response_post = project_fixture.client.post(method_url)
    assert response_post.status_code == status.HTTP_200_OK
    response_get = project_fixture.client.get(method_url)
    while response_get.json()["status"] == MethodStatus.Running:
        response_get = project_fixture.client.get(method_url)
        time.sleep(0.1)
    assert response_get.json()["status_code"] == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response_get.json()["exception_message"]
    if settings.glow_debug:
        assert "" in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg


@pytest.mark.parametrize("settings", [{"glow_debug": "True"}, {}], ids=["debug", "no_debug"], indirect=["settings"])
def test_bdm_store_a_nonexistent_path_exception(project_fixture: ProjectFixture, settings: Settings):
    # Arrange
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/exceptions-step"
    method_url = f"{step_url}:store-result"
    response = project_fixture.client.post(method_url)
    method_url = f"{step_url}:get-cached-result"
    response = project_fixture.client.post(method_url)
    relative_path = Path(response.json())
    relative_path.unlink()
    method_url = f"{step_url}:raise-store"
    # Act
    response = project_fixture.client.post(method_url)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_msg = response.json()["detail"]
    if settings.glow_debug:
        assert BDM_NO_ENTITY_ERROR_MSG in error_msg
    else:
        assert "The solution encountered an internal error and was unable to complete the request" in error_msg
