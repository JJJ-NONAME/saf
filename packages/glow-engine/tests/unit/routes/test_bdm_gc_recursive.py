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
import pytest_mock

from ansys.saf.glow._config.const import DatabaseType
from ansys.saf.glow._crud.crud import Crud
import tests.mocks.solutions.bdm_recursive_solution as bdm_solution
from tests.unit.routes.conftest import ProjectFixture

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = bdm_solution


class TestGarbageCollection:
    def test_bdm_gc_store_entity_handle_in_recursive_model_keep_files(self, project_fixture: ProjectFixture):
        # GIVEN - a transaction storing a recursive thing using bdm
        project_name = project_fixture.properties["name"]
        url = f"{project_name}/steps/bdm-step:upload-recursive-thing"
        assert len(project_fixture.project_files()) == 0
        # AND - executing the method storing entity handles in recursive model
        project_fixture.client.post(url).raise_for_status()
        # THEN - the files have not been removed
        project_files = project_fixture.project_files()
        assert len(project_files) == 2


class TestBdmGarbageCollectorLocks:
    def test_transaction_with_entity_handles_in_step_spec_upload_or_download(
        self,
        project_fixture: ProjectFixture,
        mocker: pytest_mock.MockerFixture,
    ):
        project_name = project_fixture.properties["name"]

        add_bdm_lock = mocker.spy(Crud, "add_bdm_lock")
        remove_bdm_lock = mocker.spy(Crud, "remove_bdm_lock")

        # WHEN - executing the transaction uploading entity handles
        project_fixture.client.post(
            f"{project_name}/steps/bdm-step:upload-recursive-thing",
        ).raise_for_status()
        # THEN - the bdm locks have been used (2 locks, one for the transaction and one for the upload)
        assert add_bdm_lock.call_count == 2
        assert remove_bdm_lock.call_count == 2

        add_bdm_lock.reset_mock()
        remove_bdm_lock.reset_mock()

        # WHEN - executing the transaction downloading entity handles
        project_fixture.client.post(
            f"{project_name}/steps/bdm-step:download-child-from-recursive-thing",
        ).raise_for_status()
        # THEN - the bdm locks have been used (no upload, so only one lock for the transaction)
        assert add_bdm_lock.call_count == 1
        assert remove_bdm_lock.call_count == 1
