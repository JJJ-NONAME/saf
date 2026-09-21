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

from pydantic import BaseModel
import pytest
import pytest_mock

from ansys.saf.glow._config.const import DatabaseType
from ansys.saf.glow._core.client_exceptions import BadRequestException, NotFoundException
from ansys.saf.glow._core.gql import get_update_project_steps_request_str
from ansys.saf.glow._crud.crud import Crud
from tests.check_message import check_message
from tests.mocks.solutions import bdm_solution
from tests.unit.routes.conftest import ProjectFixture
from tests.unit.routes.gql_mock_client import TestClientGqlMock

pytestmark = pytest.mark.parametrize(
    "settings",
    [
        {"glow_database_type": DatabaseType.Sqlite},
        {"glow_database_type": DatabaseType.PostgreSql},
    ],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = bdm_solution


class AnotherModel(BaseModel):
    foo: str


def test_passing_incorrect_values_for_multiple_fields_to_graphql_end_point_results_in_partial_pydantic_message(
    mocker: pytest_mock.MockerFixture,
    project_fixture: ProjectFixture,
):
    # the behavior being tested is less than ideal but is a result of validating each field in turn
    gql_client = TestClientGqlMock(project_fixture.client)
    payload: dict[str, Any] = {"other": "lalala", "result": AnotherModel(foo="BANG").model_dump()}
    mutation_query = get_update_project_steps_request_str(payload, project_fixture.project_id, "bdm_step")
    assert mutation_query
    with pytest.raises(BadRequestException) as e:
        gql_client.run_query(mutation_query, payload)
    check_message(
        [
            "1 validation error for BdmStep",
            "other",
            "Input should be a valid integer, unable to parse string as an integer "
            "[type=int_parsing, input_value='lalala', input_type=str]",
        ],
        e.value.args[0],
    )


def test_grapqhl_update_simple_field_does_not_add_bdm_lock(
    mocker: pytest_mock.MockerFixture,
    project_fixture: ProjectFixture,
):
    gql_client = TestClientGqlMock(project_fixture.client)
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/bdm-step"

    response = project_fixture.client.get(url, params={"fields": "other"})
    response.raise_for_status()
    assert response.json()["other"] == 0

    add_bdm_lock = mocker.spy(Crud, "add_bdm_lock")
    remove_bdm_lock = mocker.spy(Crud, "remove_bdm_lock")

    payload = {"other": "3"}
    mutation_query = get_update_project_steps_request_str(payload, project_fixture.project_id, "bdm_step")
    assert mutation_query
    gql_client.run_query(mutation_query, payload)
    response = project_fixture.client.get(url, params={"fields": "other"})
    response.raise_for_status()
    assert response.json()["other"] == 3

    add_bdm_lock.assert_not_called()
    remove_bdm_lock.assert_not_called()


def test_grapqhl_update_entity_handle_adds_bdm_lock(mocker: pytest_mock.MockerFixture, project_fixture: ProjectFixture):
    gql_client = TestClientGqlMock(project_fixture.client)
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/bdm-step"

    project_fixture.client.post(f"{project_name}/steps/bdm-step:store-result").raise_for_status()
    entity_handle_json = project_fixture.client.get(f"{project_name}/steps/bdm-step/data/result").json()

    add_bdm_lock = mocker.spy(Crud, "add_bdm_lock")
    remove_bdm_lock = mocker.spy(Crud, "remove_bdm_lock")

    payload = {"result": entity_handle_json}
    mutation_query = get_update_project_steps_request_str(payload, project_fixture.project_id, "bdm_step")
    assert mutation_query
    gql_client.run_query(mutation_query, payload)
    project_fixture.client.get(url, params={"fields": "result"}).raise_for_status()

    add_bdm_lock.assert_called_once()
    remove_bdm_lock.assert_called_once()


def test_grapqhl_update_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Test that attempting to update steps for a project that does not exist results in a 404."""
    gql_client = TestClientGqlMock(project_fixture.client)

    payload = {"other": 3}
    mutation_query = get_update_project_steps_request_str(payload, "nonexistent-project-id", "bdm_step")
    assert mutation_query
    with pytest.raises(NotFoundException, match="404: Project 'nonexistent-project-id' not found."):
        gql_client.run_query(mutation_query, payload)


def test_grapqhl_update_nonexistent_step_returns_404(project_fixture: ProjectFixture):
    """Test that attempting to update a step that does not exist results in a 404."""
    gql_client = TestClientGqlMock(project_fixture.client)

    payload = {"other": 3}
    mutation_query = get_update_project_steps_request_str(payload, project_fixture.project_id, "nonexistent_step")
    assert mutation_query
    with pytest.raises(NotFoundException, match="Field 'nonexistent_step' is not defined by type 'StepsJsonInput'."):
        gql_client.run_query(mutation_query, payload)


def test_grapqhl_update_nonexistent_field_returns_404(project_fixture: ProjectFixture):
    """Test that attempting to update a field that does not exist results in a 404."""
    gql_client = TestClientGqlMock(project_fixture.client)

    payload = {"nonexistent_field": 3}
    mutation_query = get_update_project_steps_request_str(payload, project_fixture.project_id, "bdm_step")
    assert mutation_query
    with pytest.raises(NotFoundException, match="Field 'nonexistent_field' is not defined by type 'BdmStepJsonInput'."):
        gql_client.run_query(mutation_query, payload)
