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
from contextlib import AbstractContextManager
from datetime import UTC, datetime
import re
from typing import Any
import uuid

from fastapi import status
from fastapi.testclient import TestClient
from httpx2 import Response
from pydantic import TypeAdapter
import pytest
from pytest_mock.plugin import MockerFixture

from ansys.saf.glow._config.const import DatabaseType
from ansys.saf.glow._repository.relational import RelationalSession
from ansys.saf.glow._server.models import BdmLockModel
import tests.mocks.solutions.bdm_solution as bdm_solution
from tests.unit.routes.conftest import ProjectFixture

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = bdm_solution


class TestBdmLocksRoutes:
    def test_post_bdm_lock_return_lock(self, project_fixture: ProjectFixture):
        project = project_fixture.properties
        response = project_fixture.client.post(f"{project['name']}/bdm-locks")
        assert response.status_code == status.HTTP_200_OK
        uuid_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        bdm_lock = response.json()
        lock_id = bdm_lock["id"]
        assert re.match(uuid_regex, lock_id)
        expiration_date = TypeAdapter(datetime).validate_python(bdm_lock["expiration_date"])
        assert datetime.now(UTC) < expiration_date

    def test_post_bdm_lock_from_inside_return_lock_without_expiration(self, project_fixture: ProjectFixture):
        project = project_fixture.properties
        response = project_fixture.client.post(
            f"{project['name']}/bdm-locks",
            headers={"GLOW_INTERNAL_TOKEN": "NOT_FROM_CLIENT_TOKEN"},
        )
        assert response.status_code == status.HTTP_200_OK
        uuid_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        bdm_lock = response.json()
        lock_id = bdm_lock["id"]
        assert re.match(uuid_regex, lock_id)
        assert bdm_lock["expiration_date"] is None

    def test_post_bdm_lock_and_delete_it(self, project_fixture: ProjectFixture):
        project = project_fixture.properties
        response = project_fixture.client.post(f"{project['name']}/bdm-locks")
        assert response.status_code == status.HTTP_200_OK
        bdm_lock = response.json()
        response = project_fixture.client.delete(f"{project['name']}/bdm-locks/{bdm_lock['id']}")
        assert response.status_code == status.HTTP_200_OK

    def test_delete_bdm_lock_wrong_id_raise_404(self, project_fixture: ProjectFixture):
        project = project_fixture.properties
        lock_id = "e396932a-7e4d-4410-a907-da5fd62cccc9"
        response = project_fixture.client.delete(f"{project['name']}/bdm-locks/{lock_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == f"Bdm lock '{lock_id}' is not found."

    def test_delete_bdm_lock_wrong_type_id_raise_422(self, project_fixture: ProjectFixture):
        project = project_fixture.properties
        lock_id = "e396932a"
        response = project_fixture.client.delete(f"{project['name']}/bdm-locks/{lock_id}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert "Input should be a valid UUID" in response.json()["detail"][0]["msg"]

    def test_get_bdm_lock_return_lock(self, project_fixture: ProjectFixture):
        project = project_fixture.properties
        post_response = project_fixture.client.post(f"{project['name']}/bdm-locks")
        assert post_response.status_code == status.HTTP_200_OK
        lock_id = post_response.json()["id"]
        get_response = project_fixture.client.get(f"{project['name']}/bdm-locks/{lock_id}")
        assert post_response.json() == get_response.json()

    def test_get_bdm_wrong_transaction_raise_404(self, project_fixture: ProjectFixture):
        project = project_fixture.properties
        response = project_fixture.client.get(f"{project['name']}/bdm-locks/e396932a-7e4d-4410-a907-da5fd62cccc9")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Bdm lock 'e396932a-7e4d-4410-a907-da5fd62cccc9' is not found."

    def test_get_bdm_lock_wrong_type_id_raise_422(self, project_fixture: ProjectFixture):
        project = project_fixture.properties
        lock_id = "e396932a"
        response = project_fixture.client.get(f"{project['name']}/bdm-locks/{lock_id}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert "Input should be a valid UUID" in response.json()["detail"][0]["msg"]

    def test_get_bdm_lock_expired_return_200(
        self,
        project_fixture: ProjectFixture,
        mocker: MockerFixture,
        client: TestClient,
    ):
        lock_id = uuid.uuid4()
        project_info_mock = mocker.patch.object(RelationalSession, "get_bdm_lock")
        project_info_mock.return_value = BdmLockModel.model_construct(
            id=lock_id,
            expiration_date=datetime.now(UTC),
        )
        response = client.get(f"{project_fixture.project_name}/bdm-locks/{lock_id}")
        project_info_mock.assert_called_once_with(project_fixture.project_id, lock_id)
        assert response.status_code == status.HTTP_200_OK

    def test_get_project_with_expired_lock_returns_200(
        self,
        project_fixture: ProjectFixture,
        mock_datetime_on_relational: Callable[[], AbstractContextManager[Any]],
    ):
        project = project_fixture.properties

        with mock_datetime_on_relational():
            response = project_fixture.client.post(f"{project['name']}/bdm-locks")
            assert response.status_code == status.HTTP_200_OK
            expired_lock_id = response.json()["id"]
            expiration_date_str = response.json()["expiration_date"]

        expiration_date = datetime.fromisoformat(expiration_date_str.replace("Z", "+00:00"))
        assert expiration_date < datetime.now(UTC)

        response = project_fixture.client.get(f"{project['name']}")
        assert response.status_code == status.HTTP_200_OK

        response = project_fixture.client.get(f"{project['name']}/bdm-locks/{expired_lock_id}")
        assert response.status_code == status.HTTP_200_OK

    def test_delete_bdm_lock_removes_expired_lock_only_selected_project(
        self,
        project_fixture: ProjectFixture,
        create_project: Callable[[str], Response],
        client: TestClient,
        mock_datetime_on_relational: Callable[[], AbstractContextManager[Any]],
    ):
        project = project_fixture.properties

        response = project_fixture.client.post(f"{project['name']}/bdm-locks")
        assert response.status_code == status.HTTP_200_OK
        valid_lock_id = response.json()["id"]

        response = project_fixture.client.get(f"{project['name']}/bdm-locks/{valid_lock_id}")
        assert response.status_code == status.HTTP_200_OK

        second_project_response = create_project("second-project")
        second_project_name = second_project_response.json()["name"]
        response = client.post(f"{second_project_name}/bdm-locks")
        assert response.status_code == status.HTTP_200_OK
        second_lock_id = response.json()["id"]

        with mock_datetime_on_relational():
            response = project_fixture.client.post(f"{project['name']}/bdm-locks")
            assert response.status_code == status.HTTP_200_OK
            expired_lock_id = response.json()["id"]
            expiration_date_str = response.json()["expiration_date"]

            expiration_date = datetime.fromisoformat(expiration_date_str.replace("Z", "+00:00"))
            assert expiration_date < datetime.now(UTC)

            response = client.post(f"{second_project_name}/bdm-locks")
            assert response.status_code == status.HTTP_200_OK
            second_expired_lock_id = response.json()["id"]

        response = project_fixture.client.delete(f"{project['name']}/bdm-locks/{valid_lock_id}")
        assert response.status_code == status.HTTP_200_OK

        response = project_fixture.client.get(f"{project['name']}/bdm-locks/{valid_lock_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = project_fixture.client.get(f"{project['name']}/bdm-locks/{expired_lock_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = client.get(f"{second_project_name}/bdm-locks/{second_lock_id}")
        assert response.status_code == status.HTTP_200_OK

        response = client.get(f"{second_project_name}/bdm-locks/{second_expired_lock_id}")
        assert response.status_code == status.HTTP_200_OK

    def test_delete_project_remove_bdm_lock(self, project_fixture: ProjectFixture):
        project = project_fixture.properties
        response = project_fixture.client.post(f"{project['name']}/bdm-locks")
        bdm_lock = response.json()
        lock_id = bdm_lock["id"]
        project_fixture.client.delete(f"{project['name']}")
        response = project_fixture.client.get(f"{project['name']}/bdm-locks/{lock_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_post_bdm_lock_nonexistent_project_returns_404(self, project_fixture: ProjectFixture):
        """Tests that POST bdm-lock with a nonexistent project_id returns a 404 error."""
        response = project_fixture.client.post("projects/nonexistent_project_id/bdm-locks")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."

    def test_get_bdm_lock_nonexistent_project_returns_404(self, project_fixture: ProjectFixture):
        """Tests that GET bdm-lock with a nonexistent project_id returns a 404 error."""
        lock_id = "e396932a-7e4d-4410-a907-da5fd62cccc9"
        response = project_fixture.client.get(f"projects/nonexistent_project_id/bdm-locks/{lock_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."

    def test_delete_bdm_lock_nonexistent_project_returns_404(self, project_fixture: ProjectFixture):
        """Tests that DELETE bdm-lock with a nonexistent project_id returns a 404 error."""
        lock_id = "e396932a-7e4d-4410-a907-da5fd62cccc9"
        response = project_fixture.client.delete(f"projects/nonexistent_project_id/bdm-locks/{lock_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."
