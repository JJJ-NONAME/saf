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

import pytest

from ansys.saf.glow._bdm.storage_contexts import METHOD_CONTEXT
from ansys.saf.glow._config.const import DatabaseType
import tests.mocks.solutions.bdm_solution as bdm_solution
from tests.unit.routes.conftest import ProjectFixture

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = bdm_solution


class TestBdmTransactions:
    def test_bdm_store_stream(self, project_fixture: ProjectFixture):
        # GIVEN - a transaction storing a stream using bdm
        project_name = project_fixture.properties["name"]
        url = f"{project_name}/steps/bdm-step:store-stream"
        assert len(project_fixture.project_files()) == 0
        # WHEN - executing the transaction
        project_fixture.client.post(url)
        # THEN - the file has been created
        project_files = project_fixture.project_files()
        assert len(project_files) == 1
        created_filepath = project_fixture.project_files_path / project_files[0]
        assert created_filepath.exists()
        # AND - it is stored in the right place
        uuid_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        assert re.search(rf"{METHOD_CONTEXT}_\w{{8}}/{uuid_regex}", created_filepath.as_posix())
        # AND - it has the right content
        assert created_filepath.read_text() == "hello world!"

    def test_bdm_store_one_file_when_transaction_called_twice(self, project_fixture: ProjectFixture):
        # GIVEN - a transaction storing a file using bdm
        project_name = project_fixture.properties["name"]
        url = f"{project_name}/steps/bdm-step:store-result"
        assert len(project_fixture.project_files()) == 0
        # WHEN - executing the transaction twice
        project_fixture.client.post(url)
        project_fixture.client.post(url)
        # THEN - two files have been created
        project_files = project_fixture.project_files()
        assert len(project_files) == 1
        assert "result.txt" in project_files[0]

    def test_bdm_store_file_in_entity_handle(self, project_fixture: ProjectFixture):
        # GIVEN - a transaction storing a file using bdm
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        # THEN - the original entity handle is empty
        response = project_fixture.client.get(f"{step_url}")
        result = response.json()["result"]
        assert result["entity_id"] == "00000000-0000-0000-0000-000000000000"
        assert result["opaque_identifier"] == ""
        assert result["is_blob"]
        # WHEN - executing the store_result transaction
        project_fixture.client.post(f"{step_url}:store-result")
        response = project_fixture.client.get(f"{step_url}")
        result = response.json()["result"]
        # THEN - the entity handle has been set properly
        assert result["entity_id"] != "00000000-0000-0000-0000-000000000000"
        uuid_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        assert re.match(uuid_regex, result["entity_id"])
        assert re.match(
            rf"primary/{project_fixture.project_id}/bdm/{METHOD_CONTEXT}_\w{{8}}:_DELIMITERresult.txt",
            result["opaque_identifier"].replace("\\", "/"),
        )
        assert result["is_blob"]

    def test_bdm_store_entity_handle_in_sub_model(self, project_fixture: ProjectFixture):
        # GIVEN - a transaction storing a blob into sub models using bdm
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        # THEN - the original entity handle in sub and inner model are empty
        response = project_fixture.client.get(f"{step_url}")
        result = response.json()
        sub_handle = result["sub"]["sub_handle"]
        assert sub_handle["entity_id"] == "00000000-0000-0000-0000-000000000000"
        assert sub_handle["opaque_identifier"] == ""
        assert sub_handle["is_blob"]

        inner_sub_handle = result["sub"]["inner_sub"]["inner_sub_handle"]
        assert inner_sub_handle["entity_id"] == "00000000-0000-0000-0000-000000000000"
        assert inner_sub_handle["opaque_identifier"] == ""
        assert inner_sub_handle["is_blob"]
        # WHEN - executing the store_submodel transaction
        project_fixture.client.post(f"{step_url}:store-sub-model")
        response = project_fixture.client.get(f"{step_url}")
        result = response.json()
        # THEN - the entity handle have been set properly
        uuid_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        sub_handle = result["sub"]["sub_handle"]
        assert re.match(uuid_regex, sub_handle["entity_id"])
        assert re.match(
            rf"primary/{project_fixture.project_id}/bdm/{METHOD_CONTEXT}_\w{{8}}:_DELIMITERsub.txt",
            sub_handle["opaque_identifier"].replace("\\", "/"),
        )
        assert sub_handle["is_blob"]

        inner_sub_handle = result["sub"]["inner_sub"]["inner_sub_handle"]
        assert re.match(uuid_regex, inner_sub_handle["entity_id"])
        assert re.match(
            rf"primary/{project_fixture.project_id}/bdm/{METHOD_CONTEXT}_\w{{8}}:_DELIMITERinner_sub.txt",
            inner_sub_handle["opaque_identifier"].replace("\\", "/"),
        )
        assert inner_sub_handle["is_blob"]

    def test_bdm_begin_store_in_entity_handle(self, project_fixture: ProjectFixture):
        # GIVEN - a transaction using bdm begin_store
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        # AND - the original entity handle is empty
        response = project_fixture.client.get(f"{step_url}")
        result = response.json()["result"]
        assert result["entity_id"] == "00000000-0000-0000-0000-000000000000"
        assert result["opaque_identifier"] == ""
        assert result["is_blob"]
        # WHEN - executing the being_store transaction
        project_fixture.client.post(f"{step_url}:begin-store-no-relative-location")
        response = project_fixture.client.get(f"{step_url}")
        result = response.json()["result"]
        # THEN - the entity handle has been set properly
        assert result["entity_id"] != "00000000-0000-0000-0000-000000000000"
        uuid_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        assert re.match(uuid_regex, result["entity_id"])
        assert re.match(
            rf"primary/{project_fixture.project_id}/bdm/{METHOD_CONTEXT}_\w{{8}}:_DELIMITER{uuid_regex}",
            result["opaque_identifier"].replace("\\", "/"),
        )
        assert result["is_blob"]

    def test_bdm_store_directory_in_entity_handle(self, project_fixture: ProjectFixture):
        # GIVEN - a transaction using directory entity handle
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        # AND - the original entity handle is empty
        response = project_fixture.client.get(f"{step_url}")
        result = response.json()["directory"]
        assert result["entity_id"] == "00000000-0000-0000-0000-000000000000"
        assert result["opaque_identifier"] == ""
        assert result["is_blob"]
        # WHEN - executing the transaction
        project_fixture.client.post(f"{step_url}:store-directory-in-entity-handle")
        response = project_fixture.client.get(f"{step_url}")
        result = response.json()["directory"]
        # THEN - the entity handle has been set properly
        assert result["entity_id"] != "00000000-0000-0000-0000-000000000000"
        uuid_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        assert re.match(uuid_regex, result["entity_id"])
        assert re.match(
            rf"primary/{project_fixture.project_id}/bdm/{METHOD_CONTEXT}_\w{{8}}:_DELIMITERtop",
            result["opaque_identifier"].replace("\\", "/"),
        )
        assert not result["is_blob"]

    def test_bdm_store_directory_create_files(self, project_fixture: ProjectFixture):
        # GIVEN - a transaction using directory entity handle
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        # AND - there is no project files
        project_files = project_fixture.project_files()
        assert len(project_files) == 0
        # WHEN - executing the transaction storing directory
        project_fixture.client.post(f"{step_url}:store-directory-in-entity-handle")
        project_files = project_fixture.project_files()
        # THEN - directories and files have been created
        assert len(project_files) == 1
        assert len(list(project_fixture.project_files_path.rglob("*"))) == 7
        created_filepath = project_fixture.project_files_path / project_files[0]
        assert created_filepath.exists()
        # AND - it is stored in the right place
        assert re.search(rf"{METHOD_CONTEXT}_\w{{8}}/top/subtop/leaf.txt", created_filepath.as_posix())
        # AND - it has the right content
        assert created_filepath.read_text() == "hello world!"

    def test_bdm_get_cached_result(self, project_fixture: ProjectFixture):
        # GIVEN - an entity handle previously stored
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        project_fixture.client.post(f"{step_url}:store-result")
        # WHEN - executing a transaction using get_cached(result)
        response = project_fixture.client.post(f"{step_url}:get-cached-result")
        # THEN - the result of get_cached is the path of the result file stored in project files
        result_file = project_fixture.project_files_path / project_fixture.project_files()[0]
        assert Path(response.json()) == result_file

    def test_bdm_get_text_result(self, project_fixture: ProjectFixture):
        # GIVEN - an entity handle previously stored
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        project_fixture.client.post(f"{step_url}:store-result")
        # WHEN - executing a transaction using get_cached(result)
        response = project_fixture.client.post(f"{step_url}:get-text-result")
        # THEN - the result of get_cached is the path of the result file stored in project files
        result_file = project_fixture.project_files_path / project_fixture.project_files()[0]
        assert response.json() == result_file.read_text()

    def test_bdm_get_copy_result(self, project_fixture: ProjectFixture, tmp_path: Path):
        # GIVEN - an entity handle previously stored
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        project_fixture.client.post(f"{step_url}:store-result")
        result_file = tmp_path / "result.txt"
        assert not result_file.exists()
        # WHEN - executing a transaction using get_copy(result)
        project_fixture.client.post(f"{step_url}:get-copy-result", json={"destination": str(tmp_path.as_posix())})
        # THEN - the file has been copied to the destination
        assert result_file.exists()
        assert result_file.read_text() == "hello world!"

    def test_bdm_get_stream_result(self, project_fixture: ProjectFixture):
        # GIVEN - an entity handle previously stored
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        project_fixture.client.post(f"{step_url}:store-result")
        # WHEN - executing a transaction using get_stream(result)
        response = project_fixture.client.post(f"{step_url}:get-stream-result")
        # THEN - the content of the entity handle is received
        assert response.json() == "hello world!"

    def test_bdm_get_directory_children(self, project_fixture: ProjectFixture):
        # GIVEN - a directory entity handle previously stored
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        project_fixture.client.post(f"{step_url}:store-directory-in-entity-handle")
        # WHEN - executing a transaction using get_children(directory)
        response = project_fixture.client.post(f"{step_url}:get-directory-children")
        # THEN - the result of get_children is the directory created earlier
        entity_handles = list(response.json())
        assert len(entity_handles) == 2
        assert {entity_handle["original_name"] for entity_handle in list(response.json())} == {"empty", "subtop"}

    def test_bdm_get_directory_child(self, project_fixture: ProjectFixture):
        # GIVEN - a directory entity handle previously stored
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        project_fixture.client.post(f"{step_url}:store-directory-in-entity-handle")
        # WHEN - executing a transaction using get_child(directory, "empty")
        response = project_fixture.client.post(f"{step_url}:get-directory-child")
        # THEN - the result of get_children is the directory created earlier
        assert response.json()["original_name"] == "empty"

    def test_bdm_delete_result(self, project_fixture: ProjectFixture):
        # GIVEN - an entity handle stored
        project_name = project_fixture.properties["name"]
        step_url = f"{project_name}/steps/bdm-step"
        project_fixture.client.post(f"{step_url}:store-result")
        # AND - file associated with the entity handle is already created
        project_files = project_fixture.project_files()
        assert len(project_files) == 1
        created_filepath = project_fixture.project_files_path / project_files[0]
        assert created_filepath.exists()
        # WHEN - replacing the entity handle by NO_ENTITY
        project_fixture.client.post(f"{step_url}:delete-result")
        response = project_fixture.client.get(f"{step_url}")
        # THEN - the new entity handle is NO_ENTITY
        assert response.json()["result"]["entity_id"] == "00000000-0000-0000-0000-000000000000"
        # AND - the file should be deleted by the garbage collection
        project_files = project_fixture.project_files()
        assert len(project_files) == 0
        assert not created_filepath.exists()
