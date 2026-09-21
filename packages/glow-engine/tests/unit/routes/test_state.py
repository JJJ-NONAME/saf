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

from ansys.saf.glow._config.const import DatabaseType
import tests.mocks.solutions.state_dependency as state_dependency
from tests.unit.routes.conftest import ProjectFixture

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = state_dependency


def test_initial_states(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    response = project_fixture.client.get(f"{project_name}/steps/a-step")
    a_step = response.json()
    response = project_fixture.client.get(f"{project_name}/steps/b-step")
    b_step = response.json()
    response = project_fixture.client.get(f"{project_name}/steps/c-step")
    c_step = response.json()
    expected_a_state = {"a1": "UPTODATE", "a2": "UPTODATE", "a3": "OUTOFDATE", "a_file": "OUTOFDATE"}
    expected_b_state = {"b1": "UPTODATE", "b2": "UPTODATE", "b3": "OUTOFDATE", "b4": "OUTOFDATE"}
    expected_c_state = {"c1": "OUTOFDATE", "c2": "UPTODATE", "c_file_group": "UPTODATE"}
    assert a_step["state"] == expected_a_state
    assert b_step["state"] == expected_b_state
    assert c_step["state"] == expected_c_state


def test_update_all_fields_makes_them_uptodate(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    updated_fields = {"a1": 90, "a2": 2, "a3": "hi"}
    response = project_fixture.client.patch(f"{project_name}/steps/a-step", json=updated_fields)
    a_step = response.json()
    response = project_fixture.client.get(f"{project_name}/steps/b-step")
    b_step = response.json()
    response = project_fixture.client.get(f"{project_name}/steps/c-step")
    c_step = response.json()
    expected_a_state = {"a1": "UPTODATE", "a2": "UPTODATE", "a3": "UPTODATE", "a_file": "OUTOFDATE"}
    expected_b_state = {"b1": "UPTODATE", "b2": "UPTODATE", "b3": "OUTOFDATE", "b4": "OUTOFDATE"}
    expected_c_state = {"c1": "OUTOFDATE", "c2": "UPTODATE", "c_file_group": "UPTODATE"}
    assert a_step["state"] == expected_a_state
    assert b_step["state"] == expected_b_state
    assert c_step["state"] == expected_c_state


def test_update_downstream_field_makes_it_uptodate(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    updated_fields = {"b4": "uptodate"}
    response = project_fixture.client.patch(f"{project_name}/steps/b-step", json=updated_fields)
    b_step = response.json()
    expected_b_state = {"b1": "UPTODATE", "b2": "UPTODATE", "b3": "OUTOFDATE", "b4": "UPTODATE"}
    assert b_step["state"] == expected_b_state


def test_update_upstream_field_invalidates_downstream(project_fixture: ProjectFixture):
    project_name = project_fixture.properties["name"]
    # make downstream c1 valid
    updated_fields = {"c1": "uptodate"}
    response = project_fixture.client.patch(f"{project_name}/steps/c-step", json=updated_fields)
    c_step = response.json()
    assert c_step["state"]["c1"] == "UPTODATE"
    # change a3 value to invalidate c1
    response = project_fixture.client.patch(f"{project_name}/steps/a-step", json={"a3": "updated_value"})
    a_step = response.json()
    response = project_fixture.client.get(f"{project_name}/steps/b-step")
    b_step = response.json()
    response = project_fixture.client.get(f"{project_name}/steps/c-step")
    c_step = response.json()
    expected_a_state = {"a1": "UPTODATE", "a2": "UPTODATE", "a3": "UPTODATE", "a_file": "OUTOFDATE"}
    expected_b_state = {"b1": "UPTODATE", "b2": "UPTODATE", "b3": "OUTOFDATE", "b4": "OUTOFDATE"}
    expected_c_state = {"c1": "OUTOFDATE", "c2": "UPTODATE", "c_file_group": "UPTODATE"}
    assert a_step["state"] == expected_a_state
    assert b_step["state"] == expected_b_state
    assert c_step["state"] == expected_c_state
