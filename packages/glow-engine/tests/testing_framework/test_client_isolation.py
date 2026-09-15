# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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

# ruff: noqa: PT019

from collections.abc import Callable
from unittest.mock import patch

from fastapi.testclient import TestClient
import pytest

from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._server.dependencies import get_http_client, get_settings
from ansys.saf.glow.client import Client
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution
from tests.mocks.solution_end_to_end.ui import first_page

pytestmark = pytest.mark.usefixtures("set_solution_env_vars")


class TestClientIsolation:
    """Test suite to ensure different TestClient instances are properly isolated"""

    def test_separate_client_instances_created(
        self,
        _solution_api_client: TestClient,
        dash_http_client: TestClient,
        _dash_callback_client_factory: Callable[[], TestClient],
    ):
        """Verify that all clients are different instances"""
        callback_client = _dash_callback_client_factory()

        clients = [
            _solution_api_client,
            dash_http_client,
            callback_client,
        ]

        # Ensure all clients are different instances
        for i, client_a in enumerate(clients):
            for j, client_b in enumerate(clients):
                if i != j:
                    assert client_a is not client_b

    def test_glow_client_and_client_project_use_solution_api_client(
        self,
        _glow_client: Client[EndToEndSolution],
        _solution_api_client: TestClient,
        client_project: EndToEndSolution,
    ):
        """Verify _glow_client and client_project use _solution_api_client internally"""
        assert _glow_client.http_client is _solution_api_client
        assert client_project._http_client is _solution_api_client  # type: ignore

    def test_transactions_use_method_client(
        self,
        _solution_api_client: TestClient,
        client_project: EndToEndSolution,
        _created_method_clients: list[TestClient],
    ):
        """Verify transactions use a method client"""
        http_client_within_transaction = client_project.steps.transaction_verification_step.return_http_client()
        assert http_client_within_transaction != _solution_api_client
        assert http_client_within_transaction in [str(client) for client in _created_method_clients]

    def test_dash_callbacks_use_dash_callback_client(
        self,
        init_dashclient: None,
        project_name: str,
        _solution_api_client: TestClient,
        _created_dash_callback_clients: list[TestClient],
    ):
        """Verify Dash callbacks use a new dash_callback_client"""
        old_clients = list(_created_dash_callback_clients)
        http_client_within_callback = first_page.return_project_http_client(0, project_name)
        assert http_client_within_callback != str(_solution_api_client)
        new_clients = [str(client) for client in _created_dash_callback_clients if client not in old_clients]
        assert http_client_within_callback in new_clients

    def test_callback_clients_are_separate_instances(
        self,
        init_dashclient: None,
        _dash_callback_client_factory: Callable[[], TestClient],
    ):
        """Verify each callback gets a fresh client instance"""
        client1 = _dash_callback_client_factory()
        client2 = _dash_callback_client_factory()

        assert client1 is not client2
        assert client1.app is not client2.app

    def test_client_closing_isolation(
        self,
        _solution_api_client: TestClient,
        _dash_callback_client_factory: Callable[[], TestClient],
    ):
        """Test that closing one client doesn't affect others"""
        callback_client = _dash_callback_client_factory()

        # Mock the close method to track calls
        with patch.object(TestClient, "close") as mock_close:
            # Close the callback client
            callback_client.close()

            # Verify only the callback client's close was called
            mock_close.assert_called_once()

            # Verify _solution_api_client is still functional
            response = _solution_api_client.get("/health")
            assert response.status_code == 200

    def test_header_modification_isolation(
        self,
        _solution_api_client: TestClient,
        _method_client_factory: Callable[[], TestClient],
        _dash_callback_client_factory: Callable[[], TestClient],
        dash_http_client: TestClient,
    ):
        """Test that header modifications don't leak between clients"""
        method_client = _method_client_factory()
        dash_callback_client = _dash_callback_client_factory()

        # Verify initial state
        assert method_client.headers.get("my-header") is None
        assert _solution_api_client.headers.get("my-header") is None
        assert dash_http_client.headers.get("my-header") is None
        assert dash_callback_client.headers.get("my-header") is None

        # Modify one client's headers
        _solution_api_client.headers["my-header"] = "test-value"

        # Verify other clients are unaffected
        assert method_client.headers.get("my-header") is None
        assert dash_http_client.headers.get("my-header") is None
        assert _solution_api_client.headers.get("my-header") == "test-value"
        assert dash_callback_client.headers.get("my-header") is None

    def test_dependency_override_isolation(
        self,
        _solution_api_client: TestClient,
        dash_http_client: TestClient,
        _dash_callback_client_factory: Callable[[], TestClient],
        _solution_settings: Settings,
    ):
        """Test that dependency overrides are properly set per client"""

        callback_client = _dash_callback_client_factory()

        # Retrieve method clients from each TestClient's dependency overrides
        solution_method_client = _solution_api_client.app.dependency_overrides[get_http_client]()  # type: ignore
        dashclient_method_client = dash_http_client.app.dependency_overrides[get_http_client]()  # type: ignore
        callback_method_client = callback_client.app.dependency_overrides[get_http_client]()  # type: ignore

        # Ensure all method clients are different instances
        assert solution_method_client is not dashclient_method_client
        assert solution_method_client is not callback_method_client
        assert dashclient_method_client is not callback_method_client

        # Settings should be the same across all clients
        for client in [solution_method_client, dashclient_method_client, callback_method_client]:  # type: ignore
            assert client.app.dependency_overrides[get_settings]() == _solution_settings  # type: ignore

    def test_method_client_factory_isolation(
        self,
        _method_client_factory: Callable[[], TestClient],
    ):
        client1 = _method_client_factory()
        client2 = _method_client_factory()
        assert client1 is not client2
        client1.headers["foo"] = "bar"
        assert client2.headers.get("foo") is None
