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

"""Frontend of the first page."""

import contextlib
import logging
from typing import Any

from dash_extensions.enrich import Input, Output, State, html  # pyright: ignore[reportMissingTypeStubs]

from ansys.saf.glow._core.method_status import MethodState
from ansys.saf.glow.client import DashClient, callback
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution
from tests.mocks.solution_end_to_end.solution.transaction_verification_step import (
    CustomTypeABC,
    TransactionVerificationStep,
)

logger = logging.getLogger(__name__)


def layout(step: TransactionVerificationStep):
    """Layout of a step that uses websockets."""
    return html.Div(
        [
            html.H1("We are in WebSockets Page"),
            html.Div(
                [
                    html.Button("Trigger Event", id="trigger_event", n_clicks=0),
                    html.Button("Trigger Events", id="trigger_events", n_clicks=0),
                    html.Div(id="event_message", children="Not triggered yet."),
                    html.Div(id="event_state", children=""),
                    html.Div(DashClient.create_event_listener(step, stream_name="my-stream", id="my_ws")),  # type: ignore
                ],
            ),
            html.Div(
                [
                    html.Button("Trigger Event Second", id="trigger_event_second", n_clicks=0),
                    html.Div(id="event_message_second", children="Not triggered yet."),
                    html.Div(DashClient.create_event_listener(step, stream_name="my-stream-second", id="my_ws_second")),  # type: ignore
                ],
            ),
            html.Div(
                [
                    html.Button("Trigger Multiple Events", id="trigger_multiple_events", n_clicks=0),
                    html.Div(id="multiple_events_message", children="Not triggered yet."),
                    html.Div(
                        DashClient.create_event_listener(  # type: ignore
                            step,
                            stream_name="multiple-events-stream",
                            id="ws_container_multiple_events",
                        ),
                    ),
                ],
            ),
            html.Div(
                [
                    html.Button("Trigger Custom Data Event", id="trigger_custom_data_event", n_clicks=0),
                    html.Div(id="event_message_custom_data", children="Not triggered yet."),
                    html.Div(
                        DashClient.create_event_listener(  # type: ignore
                            step,
                            stream_name="my-custom-data-stream",
                            id="my_ws_custom_data",
                        ),
                    ),
                ],
            ),
            html.Div(
                [
                    html.Div(
                        children=[
                            html.Button(
                                "Do Not Trigger Termination Event",
                                id="dont_trigger_termination_event",
                                n_clicks=0,
                            ),
                            html.Button("Trigger Termination Event", id="trigger_termination_event", n_clicks=0),
                            html.Button(
                                "Trigger Long-Runnig Termination Event",
                                id="trigger_lr_termination_event",
                                n_clicks=0,
                            ),
                            html.Button(
                                "Trigger Failed Termination Event",
                                id="trigger_failed_termination_event",
                                n_clicks=0,
                            ),
                        ],
                    ),
                    html.Div(id="termination_event_message", children="No termination event received."),
                    html.Div(
                        DashClient.create_event_listener(  # type: ignore
                            step,
                            stream_name="trigger-termination-event",
                            id="transaction_event_ws",
                        ),
                    ),
                    html.Div(
                        DashClient.create_event_listener(  # type: ignore
                            step,
                            stream_name="dont-trigger-termination-event",
                            id="no_transaction_event_ws",
                        ),
                    ),
                    html.Div(
                        DashClient.create_event_listener(  # type: ignore
                            step,
                            stream_name="trigger-termination-event-long-running",
                            id="lr_transaction_event_ws",
                        ),
                    ),
                    html.Div(
                        DashClient.create_event_listener(  # type: ignore
                            step,
                            stream_name="trigger-failed-termination-event",
                            id="fail_transaction_event_ws",
                        ),
                    ),
                ],
            ),
        ],
    )


@callback(
    Input("trigger_event", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def trigger_transaction_event(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        step = project.steps.transaction_verification_step
        step.trigger_event()


@callback(
    Input("trigger_events", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def trigger_transaction_events(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        step = project.steps.transaction_verification_step
        step.field_1 = 10
        step.field_2 = 5
        return step.trigger_events()


@callback(
    Output("event_message", "children"),
    Input("my_ws", "message"),
    prevent_initial_call=True,
)
def message(message: dict[str, Any]):
    if message:
        return f"Received message: {message['data']}"
    else:
        return "No message received yet."


@callback(
    Output("event_state", "children"),
    Input("my_ws", "state"),
    prevent_initial_call=True,
)
def state_message(state: dict[str, Any]):
    if state:
        if state["readyState"] == 1:
            return "WebSocket is open and ready to use."
        elif state["readyState"] == 3:
            return f"WebSocket is closed. Code: {state.get('code', '')}."
        return f"Received state: {state}"
    else:
        return ""


@callback(
    Input("trigger_event_second", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def trigger_transaction_event_second(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        step = project.steps.transaction_verification_step
        step.trigger_second_event()


@callback(
    Output("event_message_second", "children"),
    Input("my_ws_second", "message"),
    prevent_initial_call=True,
)
def message_second(message: dict[str, Any]):
    if message:
        return f"Received message: {message['data']}"
    else:
        return "No message received yet."


ACCUMULATED_MESSAGES: list[str] = []


@callback(
    Input("trigger_multiple_events", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def trigger_multiple_events_transaction(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        ACCUMULATED_MESSAGES.clear()
        step = project.steps.transaction_verification_step
        step.trigger_multiple_events()


@callback(
    Output("multiple_events_message", "children"),
    Input("ws_container_multiple_events", "message"),
    prevent_initial_call=True,
)
def message_multiple_events(message: dict[str, Any]):
    if message:
        ACCUMULATED_MESSAGES.append(message["data"])

    if ACCUMULATED_MESSAGES:
        return f"Received messages: {','.join(ACCUMULATED_MESSAGES)}"
    else:
        return "No message received yet."


@callback(
    Input("trigger_custom_data_event", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def trigger_transaction_event_custom_data(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        step = project.steps.transaction_verification_step
        step.stream_custom_data()


@callback(
    Output("event_message_custom_data", "children"),
    Input("my_ws_custom_data", "message"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def message_custom_data(message: dict[str, Any], project: EndToEndSolution):
    step = project.steps.transaction_verification_step
    intended_message = step.custom_object_for_events

    if intended_message == CustomTypeABC.model_validate_json(message["data"]):
        return "Custom data validated"
    else:
        return "Validation error"


@callback(
    Output("termination_event_message", "children"),
    Input("transaction_event_ws", "message"),
    prevent_initial_call=True,
)
def message_transaction_termination(message: dict[str, Any]):
    if message:
        method_state = MethodState.model_validate_json(message["data"])
        return f"Transaction finished with status '{method_state.status.value}'"
    else:
        return "No message received yet."


@callback(
    Input("trigger_termination_event", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def trigger_termination_event(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        step = project.steps.transaction_verification_step
        step.trigger_termination_event()


@callback(
    Output("termination_event_message", "children"),
    Input("no_transaction_event_ws", "message"),
    prevent_initial_call=True,
)
def message_no_transaction_termination(message: dict[str, Any]):
    if message:
        method_state = MethodState.model_validate_json(message["data"])
        return f"Transaction finished with status '{method_state.status.value}'"
    else:
        return "No message received yet."


@callback(
    Input("dont_trigger_termination_event", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def dont_trigger_termination_event(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        step = project.steps.transaction_verification_step
        step.dont_trigger_termination_event()


@callback(
    Output("termination_event_message", "children"),
    Input("lr_transaction_event_ws", "message"),
    prevent_initial_call=True,
)
def message_lr_transaction_termination(message: dict[str, Any]):
    if message:
        method_state = MethodState.model_validate_json(message["data"])
        return f"Transaction finished with status '{method_state.status.value}'"
    else:
        return "No message received yet."


@callback(
    Input("trigger_lr_termination_event", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def trigger_lr_termination_event(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        step = project.steps.transaction_verification_step
        step.trigger_termination_event_long_running().wait()


@callback(
    Output("termination_event_message", "children"),
    Input("fail_transaction_event_ws", "message"),
    prevent_initial_call=True,
)
def message_fail_transaction_termination(message: dict[str, Any]):
    if message:
        method_state = MethodState.model_validate_json(message["data"])
        return f"Transaction finished with status '{method_state.status.value}'"
    else:
        return "No message received yet."


@callback(
    Input("trigger_failed_termination_event", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def trigger_failed_termination_event(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        step = project.steps.transaction_verification_step
        with contextlib.suppress(Exception):
            step.trigger_failed_termination_event()
