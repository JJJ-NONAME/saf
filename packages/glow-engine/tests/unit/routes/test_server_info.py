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

import importlib.metadata

from fastapi import status
from fastapi.testclient import TestClient
import pytest

from ansys.saf.glow._config.const import DatabaseType
from ansys.saf.glow._config.settings import Settings
from tests.mocks.solutions import minimal_solution, modify_file_add_entity_handle

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = minimal_solution


def test_root_route_exposes_server_info(client: TestClient, settings: Settings) -> None:
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["solution"]["name"] == "MinimalSolution"
    assert body["solution"]["display_name"] == "Minimal Solution"
    assert body["solution"]["schema_version"] == 1
    assert body["glow_version"] == importlib.metadata.version("ansys-saf-glow-engine")
    assert (
        body["external_api_url"]
        == settings.computed_external_api_url
        == f"http://{settings.glow_api_host}:{settings.glow_api_port}"
    )


@pytest.mark.parametrize("client_func", [modify_file_add_entity_handle], indirect=True)
def test_root_route_with_solution_greater_version_than_one(client_func: TestClient, settings: Settings) -> None:
    response = client_func.get("/")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["solution"]["name"] == "OriginalSolution"
    assert body["solution"]["display_name"] == "Original for File Migration"
    assert body["solution"]["schema_version"] == 2
    assert body["glow_version"] == importlib.metadata.version("ansys-saf-glow-engine")
    assert body["external_api_url"] == settings.computed_external_api_url


@pytest.mark.parametrize("settings", [{"glow_external_api_url": "https://external.api.url"}], indirect=True)
def test_root_route_with_configured_external_api_url(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["solution"]["name"] == "MinimalSolution"
    assert body["solution"]["display_name"] == "Minimal Solution"
    assert body["solution"]["schema_version"] == 1
    assert body["glow_version"] == importlib.metadata.version("ansys-saf-glow-engine")
    assert body["external_api_url"] == "https://external.api.url"
