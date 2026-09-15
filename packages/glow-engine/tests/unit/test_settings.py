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

from fastapi.testclient import TestClient
import pytest
import pytest_mock

from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._server.server import create_app
from tests.mocks.solutions import minimal_solution


def test_settings_are_reloaded_every_request(monkeypatch: pytest.MonkeyPatch, mocker: pytest_mock.MockerFixture):
    # Create app without mocking get_settings dependency
    monkeypatch.setenv("GLOW_SOLUTION_DEFINITION", minimal_solution.__name__)
    app = create_app(Settings.model_validate({}))

    # Launch app and check that every request triggers an instantiation of Settings
    with TestClient(app) as client:
        settings_mock = mocker.spy(Settings, "__init__")
        client.get("/projects").raise_for_status()
        assert settings_mock.call_count == 1

        response = client.post("/projects", json={"display_name": "test"})
        response.raise_for_status()
        project = response.json()
        assert settings_mock.call_count == 2

        client.get(f"{project['name']}/steps/minimal-step").raise_for_status()
        assert settings_mock.call_count == 3
