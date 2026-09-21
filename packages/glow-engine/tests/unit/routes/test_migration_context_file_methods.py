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
from typing import Any, cast

from fastapi.testclient import TestClient
import pytest

from ansys.saf.glow._config.const import DatabaseType
from ansys.saf.glow._config.settings import Settings
from tests.mocks.solutions import (
    modify_attempt_to_create_handle_for_missing_file,
    modify_attempt_to_create_two_files_in_same_place,
    modify_file_add_entity_handle,
    modify_file_add_entity_handle_for_directory,
    modify_file_add_entity_handle_in_sub_directory,
    modify_file_extract_from_entity_handle,
    modify_file_original,
    modify_file_path_from_existing_handle_is_none,
    modify_file_set_entity_handle_to_no_entity,
)
from tests.unit.routes.conftest import ProjectFixture
from tests.unit.routes.modification_test_helpers import assert_error_from_upgrade_or_import, upgrade_or_import_project

pytestmark = [
    pytest.mark.parametrize(
        "settings",
        [
            {"glow_database_type": DatabaseType.Sqlite},
            {"glow_database_type": DatabaseType.PostgreSql},
        ],
        ids=["sqlite", "postgres"],
        indirect=True,
    ),
    pytest.mark.parametrize("source", ["db", "import"]),
]
solution = modify_file_original


@pytest.fixture
def initialized_project(project_fixture: ProjectFixture) -> ProjectFixture:
    project_name = project_fixture.properties["name"]
    url = f"{project_name}/steps/first-step:initialize"
    response = project_fixture.client.post(url)
    response.raise_for_status()
    return project_fixture


def _assert_contains_no_files(entity: Path) -> None:
    assert entity.exists()
    assert not entity.is_file()

    for i in entity.iterdir():
        _assert_contains_no_files(i)


@pytest.mark.parametrize(
    "client_func",
    [
        modify_file_add_entity_handle,
        modify_file_add_entity_handle_in_sub_directory,
    ],
    indirect=True,
)
def test_add_file_entity_handle(
    source: str,
    initialized_project: ProjectFixture,
    client_func: TestClient,
    tmp_path: Path,
) -> None:
    # GIVEN: Project created with a solution that doesn't have the entity handle
    project_name = initialized_project.properties["name"]
    # WHEN: Using a modified version of the solution which has a migration to add a value to the entity handle
    # THEN: Project cannot be successfully retrieved and returns a 422 error
    response = client_func.get(f"/{project_name}")
    assert response.status_code == 422

    # WHEN: Upgrading
    project_info = upgrade_or_import_project(initialized_project.client, client_func, source, project_name, tmp_path)

    # THEN: the file content can be retrieved using the entity handle API
    response = client_func.get(f"/{project_info['name']}/steps/first-step/blobs/file-entity-handle")
    assert response.status_code == 200
    assert response.content == b"new file content"


@pytest.mark.parametrize(
    "client_func",
    [
        modify_file_add_entity_handle_for_directory,
        modify_file_path_from_existing_handle_is_none,
        modify_file_extract_from_entity_handle,
    ],
    indirect=True,
)
def test_migration_does_not_fail_when_the_project_is_initialized(
    source: str,
    initialized_project: ProjectFixture,
    client_func: TestClient,
    tmp_path: Path,
) -> None:
    # GIVEN: project that is initialized
    project_name = initialized_project.properties["name"]

    # add hidden file to the project
    hidden = initialized_project.project_files_dir / ".hidden"
    hidden.mkdir(exist_ok=True)
    file = hidden / "stuff_99.txt"
    file.write_text("you should not be reading this")

    # WHEN: access the project using a later version of the schema
    response = client_func.get(f"/{project_name}")
    # THEN: the response is that the project is not processable
    assert response.status_code == 422

    # WHEN: Upgrading
    # THEN: no exception occurs
    upgrade_or_import_project(initialized_project.client, client_func, source, project_name, tmp_path)


@pytest.mark.parametrize(
    "client_func",
    [
        modify_file_set_entity_handle_to_no_entity,
    ],
    indirect=True,
)
def test_files_no_longer_referenced_after_migration_do_not_remain_in_project(
    source: str,
    initialized_project: ProjectFixture,
    client_func: TestClient,
    tmp_path: Path,
    settings: Settings,
) -> None:
    # GIVEN: project that is initialized
    project_name = initialized_project.properties["name"]

    # WHEN: access the project using a later version of the schema
    response = client_func.get(f"/{project_name}")

    # THEN: the response is that the project is not processable
    assert response.status_code == 422

    # WHEN: Upgrading
    project = upgrade_or_import_project(initialized_project.client, client_func, source, project_name, tmp_path)
    project_name = cast("str", project["name"])
    project_id = project_name.split("/")[-1]

    # THEN: nothing remains in the bdm directory because the files are no longer referenced
    project_files_directory = settings.computed_project_files_directory / project_id
    assert project_files_directory.is_dir()
    bdm_dir = project_files_directory / "bdm"
    _assert_contains_no_files(bdm_dir)


@pytest.mark.parametrize(
    "client_func_and_extra",
    [
        (
            modify_attempt_to_create_two_files_in_same_place,
            "An entity already exists at the requested target path: new_file.txt.",
        ),
        (modify_attempt_to_create_handle_for_missing_file, "new_file.txt does not exist"),
    ],
    indirect=True,
)
def test_error_conditions_result_with_expected_error_codes_and_response_text(
    source: str,
    project_fixture: ProjectFixture,
    client_func_and_extra: tuple[TestClient, Any],
    tmp_path: Path,
) -> None:
    # GIVEN: Project created with a solution that doesn't have the entity handle
    project_name = project_fixture.properties["name"]
    client_func, expected_error_text = client_func_and_extra
    response = client_func.get(f"/{project_name}")
    assert response.status_code == 422

    # WHEN: Upgrading using a solution that saves files twice to the same location
    # THEN error raised
    assert_error_from_upgrade_or_import(
        project_fixture.client,
        client_func,
        source,
        project_name,
        tmp_path,
        expected_error_text,
    )
