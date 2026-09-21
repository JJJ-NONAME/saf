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

from typing import Any
from urllib.parse import quote

from fastapi import status
from fastapi.testclient import TestClient
import pytest

from ansys.saf.glow._config.const import DatabaseType
import tests.mocks.solutions.minimal_solution as minimal_solution
from tests.mocks.solutions.minimal_solution import MinimalStep
from tests.unit.routes.conftest import ProjectFixture

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = minimal_solution


def test_health_ok(client: TestClient):
    """Tests that the health endpoint returns 'OK'."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK


def test_get_step_all_steps_have_endpoints(project_fixture: ProjectFixture):
    """Tests that all steps have proper endpoints that return 'OK'."""
    project_name = project_fixture.properties["name"]
    urls = [f"{project_name}/steps/minimal-step", f"{project_name}/steps/other-step"]
    for url in urls:
        response = project_fixture.client.get(url)
        assert response.status_code == status.HTTP_200_OK


def test_get_step_unexistent_step_404(project_fixture: ProjectFixture):
    """Tests that a nonexistent step raises a 404 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/unexistent-step"
    response = project_fixture.client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_get_step_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Tests that GET step with a nonexistent project_id returns a 404 error."""
    url = "projects/nonexistent_project_id/steps/minimal-step"
    response = project_fixture.client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."


def test_get_step_returns_step_resource(project_fixture: ProjectFixture):
    """Tests that step endpoints return the corresponding step resources."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    response = project_fixture.client.get(url)
    step = response.json()
    assert len(step) == 20
    assert step["x"] == 99
    assert step["name"] == "a string"


def test_get_step_fields_query_returns_partial_step_resource(project_fixture: ProjectFixture):
    """Tests that step endpoints return the corresponding step resources."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    response = project_fixture.client.get(url, params={"fields": "x,name,squared_value"})
    step = response.json()
    assert len(step) == 3
    assert step["x"] == 99
    assert step["name"] == "a string"
    assert step["squared_value"] == 4


def test_get_step_wrong_fields_query_returns_empty_step_resource(project_fixture: ProjectFixture):
    """Tests that step endpoints return the corresponding step resources."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    response = project_fixture.client.get(url)
    response = project_fixture.client.get(url, params={"fields": "wrong_field"})
    step = response.json()
    assert len(step) == 0


def test_patch_step_return_modified_step(project_fixture: ProjectFixture):
    """Tests that modified data are returned properly."""
    project_name = project_fixture.properties["name"]
    old_project_date_modified = project_fixture.properties["date_modified"]
    url = f"{project_name}/steps/minimal-step"
    payload = {"x": 23}
    response = project_fixture.client.patch(url, json=payload)
    step = response.json()
    assert step["x"] == 23
    assert step["name"] == "a string"
    url = f"{project_name}"
    response = project_fixture.client.get(url)
    assert response.json()["date_modified"] != old_project_date_modified


def test_get_step_following_patch_step_has_same_response(project_fixture: ProjectFixture):
    """ "Tests that the response from PATCH is the same as subsequent GET on step."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    get_response = project_fixture.client.get(url)
    payload = {"x": 23}
    patch_response = project_fixture.client.patch(url, json=payload)
    assert get_response.json() != patch_response.json()
    get_response = project_fixture.client.get(url)
    assert patch_response.json() == get_response.json()


def my_step_has_docstring_in_openapi(client: TestClient):
    """Tests that the step has proper description taken from the docstring."""
    response = client.get("openapi.json")
    doc = MinimalStep.__doc__
    assert doc is not None
    assert doc in response.json()["paths"]["/projects/{project_id}/steps/minimal-step"]["get"]["description"]


def test_patch_step_invalid_value_raise_422(project_fixture: ProjectFixture):
    """Tests that a payload containing a field with an incorrect type raises a 422 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    payload = {"value": "NaN"}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert (
        "Input should be a valid integer, unable to parse string as an integer" in response.json()["detail"][0]["msg"]
    )


def test_patch_step_castable_value_is_ok(project_fixture: ProjectFixture):
    """Tests that a payload containing a field with a compatible type is accepted."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    payload = {"x": 12}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_200_OK


def test_patch_step_invalid_key_raise_422(project_fixture: ProjectFixture):
    """Tests that fields not included in the step definition are ignored."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    payload = {"not_a_step_field": "not_a_step_field"}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "Extra inputs are not permitted" in response.json()["detail"][0]["msg"]


def test_patch_step_invalid_field_from_validator_raised_422(project_fixture: ProjectFixture):
    """Tests that a payload containing a field not respecting the validator raises a 422 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    payload = {"name": "nospace"}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "Value error, nospace must contain a space" in response.json()["detail"][0]["msg"]


def test_patch_step_invalid_field_from_root_validator_raised_422(project_fixture: ProjectFixture):
    """Tests that a payload containing a field not respecting the validator raises a 422 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    payload = {"squared_value": 3}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "Value error, squared_value must be equal to value x value." in response.json()["detail"][0]["msg"]


def test_patch_step_invalid_item_from_list_raised_422(project_fixture: ProjectFixture):
    """Tests that a payload containing an item not respecting the validator from a collection raises a 422 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    payload = {"even_numbers": [2, 3]}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "Assertion failed, 3 is not an even number" in response.json()["detail"][0]["msg"]


def test_patch_step_unexistent_step_404(project_fixture: ProjectFixture):
    """Tests that PATCH a nonexistent step raises a 404 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/unexistent-step"
    payload = {"x": 23}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_patch_step_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Tests that PATCH step with a nonexistent project_id returns a 404 error."""
    url = "projects/nonexistent_project_id/steps/minimal-step"
    payload = {"x": 23}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."


# ignore serializer warnings, see: https://github.com/pydantic/pydantic/issues/6467
@pytest.mark.filterwarnings("ignore: Pydantic serializer warnings")
@pytest.mark.parametrize(
    ("payload"),
    [
        # Add a user
        {"users": {"users": [{"user_id": 1, "name": "Zea Woods"}, {"user_id": 99, "name": "Peter White"}]}},
        # Modify a user entirely
        {"users": {"users": [{"user_id": 2, "name": "Peter White"}]}},
        # Modify a user partially
        {"users": {"users": [{"user_id": 1, "name": "Peter White"}]}},
        # Remove all users
        {"users": {"users": []}},
    ],
)
def test_custom_type_can_be_modified(payload: dict[str, Any], project_fixture: ProjectFixture):
    """Tests that a custom type can be modified."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    response = project_fixture.client.get(url)
    assert response.json()["users"] == {"users": [{"user_id": 1, "name": "Zea Woods"}]}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_200_OK
    response = project_fixture.client.get(url)
    assert response.json()["users"] == payload["users"]


def test_custom_type_wrong_data_raises_422(project_fixture: ProjectFixture):
    """Tests that updating a custom type with a wrong field raises 422."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    payload = {"users": {"users": [{"user_id": 1, "name": "Zea Woods"}, {"wrong_field": "wrong_data"}]}}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "Field required" in response.json()["detail"][0]["msg"]


@pytest.mark.parametrize(
    ("field_name", "initial_value", "new_value"),
    [
        ("my_enum", "a", "b"),
        ("my_tuple", ["a", "b"], ["c", "d"]),  # json way to represent a tuple
        ("my_list_of_tuple", [["a", "b"], ["c", "d"]], [["d", "e"]]),  # json way to represent a tuple
        ("dict_int_int", {}, {"0": 0}),  # json way to represent an integer key
    ],
)
def test_patch_step_not_working_with_strict(
    field_name: str,
    initial_value: str,
    new_value: str,
    project_fixture: ProjectFixture,
):
    """Test that step fields not working with strict mode are properly working."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step"
    response = project_fixture.client.get(url, params={"fields": field_name})
    assert response.json()[field_name] == initial_value
    payload = {field_name: new_value}
    response = project_fixture.client.patch(url, json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[field_name] == new_value


def test_get_step_without_fields(project_fixture: ProjectFixture):
    """Tests that steps without fields are supported."""
    project_name = project_fixture.properties["name"]
    response = project_fixture.client.get(project_name)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["display_name"] == "project"
    response = project_fixture.client.get(f"{project_name}/steps/fieldless-step")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"state": {}}
    response = project_fixture.client.post(f"{project_name}/steps/fieldless-step:square", json={"number": 2})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == 4


@pytest.mark.parametrize(
    ("datapath", "expected_value"),
    [
        ("x", 99),
        ("even_numbers", [2, 4]),
        ("even_numbers/0", 2),
        ("users", {"users": [{"name": "Zea Woods", "user_id": 1}]}),
        ("users/users/0/name", "Zea Woods"),
        ("my_tuple/0", "a"),
        ("my_list_of_tuple/1/1", "d"),
        ("dict_user/admin/user_id", 0),
        ("space_dict/" + quote("key with space"), "value"),
        ("dot_dict/key.with.dots", "value"),
        ("slash_dict/" + quote(r"key\/s"), "value"),
        ("accent_dict/" + quote("éèàêë"), "value"),
        ("special_char_dict/" + quote("()+[]{}%*<>?-_"), "value"),
    ],
)
def test_get_data(project_fixture: ProjectFixture, datapath: str, expected_value: Any):
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step/data/{datapath}"
    response = project_fixture.client.get(url)
    assert response.json() == expected_value


def test_get_data_empty_string_return_all_step_fields(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step/data/"
    response = project_fixture.client.get(url).json()
    assert MinimalStep().model_dump().keys() == response.keys()
    assert MinimalStep.model_validate(response)


@pytest.mark.parametrize(
    ("datapath"),
    [
        "x/0",
        "even_numbers/a",
        "wrong",
        "users/users/10",
        "users/wrong",
        "users/0",
        "my_tuple/5",
        "_private",
        "dict_user//emptykey",
    ],
)
def test_get_data_raise_not_found_wrong_field(project_fixture: ProjectFixture, datapath: str):
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/minimal-step/data/{datapath}"
    response = project_fixture.client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "The object referenced by the datapath cannot be found" in response.json()["detail"]


def test_get_data_nonexistent_step_returns_404(project_fixture: ProjectFixture):
    """Tests that GET step data with a nonexistent step returns a 404 error."""
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/unexistent-step/data/x"
    response = project_fixture.client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_get_data_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Tests that GET step data with a nonexistent project_id returns a 404 error."""
    url = "projects/nonexistent_project_id/steps/minimal-step/data/x"
    response = project_fixture.client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."
