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

import anyio
from fastapi import status
from fastapi.testclient import TestClient
from httpx2 import Response
import pytest
from starlette.testclient import WebSocketDenialResponse, WebSocketTestSession

from ansys.saf.glow._config.const import DatabaseType
from tests.mocks.solutions import minimal_solution

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = minimal_solution


def assert_empty_queue(websocket: WebSocketTestSession):
    with pytest.raises(anyio.WouldBlock):
        # calling receive_json() or receive() blocks the session. Tried to wrap it with asyncio, a thread, a proc...
        # but this was the simplest after checking the internal implementation of WebSocketTestSession.
        websocket._send_rx.receive_nowait()  # pyright: ignore[reportPrivateUsage, reportUnknownMemberType]


def test_single_stream_single_client_before_event(client: TestClient, create_project: Callable[[str], Response]):
    """Single stream, single client before first event is raised, multiple events."""
    create_response = create_project("x")
    project_name = create_response.json()["name"]
    url = f"/events/{project_name}/steps/minimal-step/streams/test-stream"
    first_expected_message = {"message": "content_1"}
    second_expected_message = {"message": "content_2"}
    with client.websocket_connect(url) as websocket:
        assert_empty_queue(websocket)
        client.post(url, json=first_expected_message)
        assert websocket.receive_json() == first_expected_message
        client.post(url, json=second_expected_message)
        assert websocket.receive_json() == second_expected_message


def test_single_stream_single_client_after_multiple_events(
    client: TestClient,
    create_project: Callable[[str], Response],
):
    """Single stream, single client after multiple events are raised."""
    create_response = create_project("x")
    project_name = create_response.json()["name"]
    url = f"/events/{project_name}/steps/minimal-step/streams/test-stream"
    first_expected_message = {"message": "content_1"}
    second_expected_message = {"message": "content_2"}
    with client.websocket_connect(url) as websocket:
        client.post(url, json=first_expected_message)
        client.post(url, json=second_expected_message)
        assert websocket.receive_json() == first_expected_message
        assert websocket.receive_json() == second_expected_message
        assert_empty_queue(websocket)


def test_single_stream_single_client_after_event_empty_queue(
    client: TestClient,
    create_project: Callable[[str], Response],
):
    """Single stream, single client after the first event is raised, multiple events."""
    create_response = create_project("x")
    project_name = create_response.json()["name"]
    url = f"/events/{project_name}/steps/minimal-step/streams/test-stream"
    first_expected_message = {"message": "content_1"}
    second_expected_message = {"message": "content_2"}
    client.post(url, json=first_expected_message)
    with client.websocket_connect(url) as websocket:
        assert_empty_queue(websocket)
        client.post(url, json=second_expected_message)
        assert websocket.receive_json() == second_expected_message


@pytest.mark.skip(reason="Frequently hangs indefinitely. Probably due to starlette's WebSocketTestSession impl.")
def test_single_stream_multiple_clients(client: TestClient, create_project: Callable[[str], Response]):
    """Single stream, multiple clients at different time points, multiple events."""
    create_response = create_project("x")
    project_name = create_response.json()["name"]
    stream_url = f"events/{project_name}/steps/minimal-step/streams/test-stream"

    first_expected_message = {"message": "content_1"}
    second_expected_message = {"message": "content_2"}
    third_expected_message = {"message": "content_3"}

    with client.websocket_connect(stream_url) as first_websocket:
        client.post(stream_url, json=first_expected_message)
        assert first_websocket.receive_json() == first_expected_message
        with client.websocket_connect(stream_url) as second_websocket:
            # as long as an event is consumed, future websockets will not receive it.
            assert_empty_queue(second_websocket)

            # new event can be received by both websockets
            client.post(stream_url, json=second_expected_message)
            assert first_websocket.receive_json() == second_expected_message
            assert second_websocket.receive_json() == second_expected_message

        # After exiting the context manager, second_websocket is closed and new events still reach
        # the remaining websocket.
        client.post(stream_url, json=third_expected_message)
        assert first_websocket.receive_json() == third_expected_message


def test_multiple_streams_multiple_clients(client: TestClient, create_project: Callable[[str], Response]):
    """Multiple streams, one client per stream, multiple events."""
    create_response = create_project("x")
    project_name = create_response.json()["name"]

    first_url = f"events/{project_name}/steps/minimal-step/streams/test-stream"
    second_url = f"events/{project_name}/steps/minimal-step/streams/second-test-stream"

    first_expected_message = {"message": "content_1"}
    second_expected_message = {"message": "content_2"}
    third_expected_message = {"message": "content_3"}

    with (
        client.websocket_connect(first_url) as first_websocket,
        client.websocket_connect(
            second_url,
        ) as second_websocket,
    ):
        # events are only received by the corresponding websocket
        client.post(first_url, json=first_expected_message)
        assert_empty_queue(second_websocket)
        assert first_websocket.receive_json() == first_expected_message

        client.post(second_url, json=second_expected_message)
        assert_empty_queue(first_websocket)
        assert second_websocket.receive_json() == second_expected_message

        client.post(first_url, json=third_expected_message)
        assert_empty_queue(second_websocket)
        assert first_websocket.receive_json() == third_expected_message


def test_stream_event_nonexistent_project(client: TestClient):
    """WebSocket connection is rejected when the project does not exist."""
    url = "/events/projects/nonexistent-project/steps/minimal-step/streams/test-stream"
    with pytest.raises(WebSocketDenialResponse) as e, client.websocket_connect(url):
        ...
    assert "404 Not Found" in str(e)


def test_stream_event_nonexistent_step(client: TestClient, create_project: Callable[[str], Response]):
    """WebSocket connection is rejected when the step does not exist."""
    create_response = create_project("x")
    project_name = create_response.json()["name"]
    url = f"/events/{project_name}/steps/nonexistent-step/streams/test-stream"
    with pytest.raises(WebSocketDenialResponse) as e, client.websocket_connect(url):
        ...
    assert "404 Not Found" in str(e)


def test_store_event_nonexistent_project(client: TestClient):
    """POST to store event returns 404 when the project does not exist."""
    url = "/events/projects/nonexistent-project/steps/minimal-step/streams/test-stream"
    response = client.post(url, json={"message": "content"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Project 'nonexistent-project' not found." in response.json()["detail"]


def test_store_event_nonexistent_step(client: TestClient, create_project: Callable[[str], Response]):
    """POST to store event returns 404 when the step does not exist."""
    create_response = create_project("x")
    project_name = create_response.json()["name"]
    url = f"/events/{project_name}/steps/nonexistent-step/streams/test-stream"
    response = client.post(url, json={"message": "content"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Step 'nonexistent_step' not found." in response.json()["detail"]
