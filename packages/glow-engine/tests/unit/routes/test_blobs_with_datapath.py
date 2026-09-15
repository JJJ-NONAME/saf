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

import pytest
from starlette import status

from ansys.saf.glow._config.const import DatabaseType
from tests.mocks.solutions import bdm_solution
from tests.unit.routes.conftest import ProjectFixture

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = bdm_solution


@pytest.mark.parametrize(
    ("datapath", "method", "expected_value"),
    [
        ("list_handles/0", "store-list-handles", "list_handles.txt"),
        ("my-entity", "store-my-entity", "hello world!"),
        ("my_entities/subdir1/level1_file.json", "manually-create-entities-dict", '{"key": "value"}'),
    ],
)
def test_can_download_file(project_fixture: ProjectFixture, datapath: str, method: str, expected_value: str):
    # GIVEN - a field containing at least one entity handle
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/bdm-step"

    project_fixture.client.post(f"{step_url}:{method}").raise_for_status()

    # WHEN - accessing the blob upload URL for an entity handle in the field
    url = f"{step_url}/blobs/{datapath}"
    response = project_fixture.client.get(url)

    # THEN - the result of the GET is the content of the original file
    response.raise_for_status()
    assert response.text == expected_value


@pytest.mark.parametrize(
    ("datapath", "method"),
    [
        ("list_handles/99", "store-list-handles"),
        ("JUNK", "store-my-entity"),
        ("my_entities/subdir1/JUNK", "manually-create-entities-dict"),
        ("my_entities/JUNK/level1_file.json", "manually-create-entities-dict"),
    ],
)
def test_datapaths_with_non_matching_keys_result_in_404_status_code(
    project_fixture: ProjectFixture,
    datapath: str,
    method: str,
):
    # GIVEN - a field containing at least one entity handle
    project_name = project_fixture.properties["name"]
    step_url = f"{project_name}/steps/bdm-step"

    project_fixture.client.post(f"{step_url}:{method}").raise_for_status()

    # WHEN - accessing the blob upload URL for an entity handle in the field
    url = f"{step_url}/blobs/{datapath}"
    response = project_fixture.client.get(url)

    # THEN - the result of the GET is the content of the original file
    assert response.status_code == 404


def test_get_blob_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Tests that GET blob with a nonexistent project_id returns a 404 error."""
    response = project_fixture.client.get("projects/nonexistent_project_id/steps/bdm-step/blobs/my-entity")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."


def test_put_blob_nonexistent_project_returns_404(project_fixture: ProjectFixture):
    """Tests that PUT blob with a nonexistent project_id returns a 404 error."""
    response = project_fixture.client.put(
        "projects/nonexistent_project_id/steps/bdm-step/blobs/my-entity",
        files={"upload_file": b"content"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project 'nonexistent_project_id' not found."


def test_get_blob_nonexistent_step_returns_404(project_fixture: ProjectFixture):
    """Tests that GET blob with a nonexistent step_id returns a 404 error."""
    project_name = project_fixture.properties["name"]
    response = project_fixture.client.get(f"{project_name}/steps/nonexistent_step_id/blobs/my-entity")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_put_blob_nonexistent_step_returns_404(project_fixture: ProjectFixture):
    """Tests that PUT blob with a nonexistent step_id returns a 404 error."""
    project_name = project_fixture.properties["name"]
    response = project_fixture.client.put(
        f"{project_name}/steps/nonexistent_step_id/blobs/my-entity",
        files={"upload_file": b"content"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"


def test_put_blob_nonexistent_field_returns_405(project_fixture: ProjectFixture):
    """Tests that PUT blob with a nonexistent field_id returns a 405 error."""
    project_name = project_fixture.properties["name"]
    response = project_fixture.client.put(
        f"{project_name}/steps/bdm-step/blobs/my-wrong-entity",
        files={"upload_file": b"content"},
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
