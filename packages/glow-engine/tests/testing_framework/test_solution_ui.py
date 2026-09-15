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
from fastapi.testclient import TestClient
import pytest

from tests.mocks.solution_end_to_end.ui import first_page, websockets_page

pytestmark = [pytest.mark.usefixtures("init_dashclient", "set_solution_env_vars")]


def test_sync_callback(project_name: str):
    assert first_page.calculate_project_injected(1, 1, 2, project_name).startswith("Result:3.0/PID:")

    with pytest.raises(IndexError, match="tuple index out of range"):
        first_page.calculate_project_injected(n_clicks=1, first_arg=1, second_arg=2, pathname=project_name)


def test_sync_callback_long_running(project_name: str):
    assert first_page.calculate_project_injected_long_running(1, 1, 2, project_name).startswith("Result:3.0/PID:")


def test_background_callback(project_name: str):
    assert first_page.calculate_in_background_with_project_injected(1, 1, 2, project_name).startswith("Result:3.0/PID:")


def test_background_callback_long_running(project_name: str):
    assert first_page.calculate_in_background_with_project_injected_long_running(1, 1, 2, project_name).startswith(
        "Result:3.0/PID:",
    )


def test_event_triggered_from_callback(dash_http_client: TestClient, project_name: str):
    ws_url = f"/events/{project_name}/steps/transaction-verification-step/streams"
    my_stream_url = f"{ws_url}/my-stream"
    termination_ws_url = f"{ws_url}/trigger-events"
    with (
        dash_http_client.websocket_connect(my_stream_url) as ws,
        dash_http_client.websocket_connect(
            termination_ws_url,
        ) as termination_ws,
    ):
        # GIVEN: callback that invokes a transaction that triggers several events and a termination event
        websockets_page.trigger_transaction_events(1, project_name)
        event = ws.receive_json()
        assert event["message"] == "testing!"
        event = ws.receive_json()
        assert event["message"] == 15
        termination_event = termination_ws.receive_json()
        assert termination_event["status"] == "completed"
        # THEN: Emulate dash-extensions event listener behavior, which passes {"data": event} to the callback
        assert websockets_page.message({"data": event}) == "Received message: {'message': 15.0}"


def test_event_triggered_from_callback_without_listening_to_events(project_name: str):
    # GIVEN: callback that invokes transaction that triggers an event
    # THEN: the callback returns the result even if there's nobody listening to the events
    # (messages and termination event)
    assert websockets_page.trigger_transaction_events(1, project_name) == 15
