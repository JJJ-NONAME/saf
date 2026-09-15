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

"""Frontend of the third page."""

import base64
import logging
from typing import Any

from dash import dcc  # pyright: ignore[reportMissingTypeStubs]
from dash_extensions.enrich import Input, Output, State, html  # pyright: ignore[reportMissingTypeStubs]

from ansys.saf.glow.client import DashClient, callback
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution
from tests.mocks.solution_end_to_end.solution.transaction_verification_step import (
    TransactionVerificationStep,
)

logger = logging.getLogger(__name__)


def layout(step: TransactionVerificationStep):
    """Layout of the third step UI."""
    return html.Div(
        [
            html.H1("We are in Third Page"),
            html.Div(
                [
                    html.Button("Trigger Event", id="trigger_event_on_page_3", n_clicks=0),
                    html.Div(id="event_message", children="Not triggered yet."),
                    html.Div(DashClient.create_event_listener(step, stream_name="my-third-stream", id="my_third_ws")),  # type: ignore
                ],
            ),
            html.Div(
                [
                    dcc.Upload(
                        id="aedt_project_file_uploader",
                        children=html.Button("Upload AEDT File"),
                        accept=".aedt",
                        multiple=False,
                    ),
                    html.Div(id="file_upload_completed", children="File not uploaded yet."),
                ],
            ),
        ],
    )


@callback(
    Input("trigger_event_on_page_3", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def trigger_transaction_event(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        step = project.steps.transaction_verification_step
        step.another_trigger_event()


@callback(
    Output("event_message", "children"),
    Input("my_third_ws", "message"),
    prevent_initial_call=True,
)
def message(message: dict[str, Any]):
    if message:
        return f"Received message: {message['data']}"
    else:
        return "No message received yet."


@callback(
    Output("file_upload_completed", "children"),
    [
        Input("aedt_project_file_uploader", "contents"),
        State("aedt_project_file_uploader", "filename"),
        State("url", "pathname"),
    ],
    prevent_initial_call=True,
)
def handle_file(contents: str, filename: str, project: EndToEndSolution):
    if contents and filename:
        content_string = contents.removeprefix("data:application/octet-stream;base64,")
        file_bytes = base64.b64decode(content_string)
        step = project.steps.transaction_verification_step
        # Store file via the storage scope at the transaction method (api-side)
        step.store_data_content_into_file_entity(file_content=file_bytes, file_name="api_" + filename)

        # Store file via the storage scope at project client
        storage_scope = project.storage_scope
        scoped_filepath = storage_scope.get_storage_root() / ("ui_" + filename)
        scoped_filepath.write_bytes(file_bytes)
        step.e2e_file_entity_ui = storage_scope.store(scoped_filepath)

        return "File uploaded."
    else:
        return "File not uploaded yet."
