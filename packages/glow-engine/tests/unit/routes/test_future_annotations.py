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

from fastapi import status
from fastapi.testclient import TestClient
import pytest

from ansys.saf.glow._config.const import DatabaseType
import tests.mocks.solutions.future_annotations_solution as future_annotations_solution

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = future_annotations_solution


def test_openapi_schema_generation_with_future_annotations(client: TestClient):
    response = client.get("openapi.json")

    assert response.status_code == status.HTTP_200_OK
    schema = response.json()
    assert "/projects/{project_id}/steps/future-annotations-step" in schema["paths"]
    assert "FutureAnnotationsPayload" in schema["components"]["schemas"]


def test_docs_with_future_annotations_solution(client: TestClient):
    response = client.get("/docs")

    assert response.status_code == status.HTTP_200_OK
