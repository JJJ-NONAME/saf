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

#

from fastapi import status
from fastapi.testclient import TestClient
import pytest

from ansys.saf.glow._config.const import DatabaseType
import tests.mocks.solutions.has_methods as has_methods
from tests.mocks.solutions.has_methods import MethodStep
from tests.unit.routes.conftest import ProjectFixture

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = has_methods


def test_invoking_nonexistent_method_result_in_404(project_fixture: ProjectFixture):
    """Tests that non-existent method returns a 404 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/method-step:missing"
    response = project_fixture.client.post(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_invoking_method_without_transaction_decorator_result_in_404(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/method-step:hidden"
    response = project_fixture.client.post(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_method_has_docstring_in_openapi(client: TestClient):
    """Tests that the custom method has proper description taken from the docstring."""
    response = client.get("openapi.json")
    doc = MethodStep.increment.__doc__
    assert doc is not None
    assert doc in response.json()["paths"]["/projects/{project_id}/steps/method-step:increment"]["post"]["description"]


def test_async_method_initially_has_never_started_status(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/method-step:slow"
    _check_async_no_exception_state(project_fixture.client, url, ["run-required"])


def _check_async_no_exception_state(client: TestClient, url: str, expected_statuses: list[str]) -> str:
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert "status" in json
    assert "exception_message" not in json or json["exception_message"] is None
    assert "exception_trace" not in json or json["exception_trace"] is None
    status_returned = json["status"]
    assert status_returned in expected_statuses
    return status_returned


def test_invoking_method_with_payload_should_result_in_a_422_error(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/method-step:increment"
    payload = {"foo": "foobar"}
    response = project_fixture.client.post(url, json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "Extra inputs are not permitted" in response.json()["detail"][0]["msg"]


def test_invoking_nonexistent_step_result_in_404(project_fixture: ProjectFixture):
    """Tests that POST method on a nonexistent step returns a 404 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/nonexistent-step:increment"
    response = project_fixture.client.post(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_invoking_method_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Tests that POST method with a nonexistent project_id returns a 404 error."""
    url = "projects/nonexistent_project_id/steps/method-step:increment"
    response = project_fixture.client.post(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."


def test_get_method_state_nonexistent_step_returns_404(project_fixture: ProjectFixture):
    """Tests that GET method state on a nonexistent step returns a 404 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/nonexistent-step:slow"
    response = project_fixture.client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_get_method_state_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Tests that GET method state with a nonexistent project_id returns a 404 error."""
    url = "projects/nonexistent_project_id/steps/method-step:slow"
    response = project_fixture.client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."


def test_patch_method_state_nonexistent_step_returns_404(project_fixture: ProjectFixture):
    """Tests that PATCH method state on a nonexistent step returns a 404 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/nonexistent-step:slow"
    payload = {"status": "run-required"}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_patch_method_state_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Tests that PATCH method state with a nonexistent project_id returns a 404 error."""
    url = "projects/nonexistent_project_id/steps/method-step:slow"
    payload = {"status": "run-required"}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."
