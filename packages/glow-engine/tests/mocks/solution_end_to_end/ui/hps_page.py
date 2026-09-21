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

"""Frontend of the HPS page."""

import logging

from dash_extensions.enrich import Input, Output, State, html  # pyright: ignore[reportMissingTypeStubs]

from ansys.saf.glow.client import callback
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution
from tests.mocks.solution_end_to_end.solution.hps_simple_project_step import HpsSimpleProjectStep

logger = logging.getLogger(__name__)


def layout(step: HpsSimpleProjectStep):
    """Layout of the HPS step UI."""
    return html.Div(
        [
            html.H1("We are in HPS Page"),
            html.Div(
                [
                    html.Button("Check simple HPS project state", id="hps_status_check", n_clicks=0),
                    html.Div(id="hps_status", children="Not triggered yet."),
                ],
            ),
            html.Div(
                [
                    html.Button("Authenticate project from client", id="trigger_dashclient_auth", n_clicks=0),
                    html.Div(id="auth_launched", children="Not triggered yet."),
                ],
            ),
            html.Div(
                [
                    html.Button(
                        "Authenticate project from client with custom params",
                        id="trigger_dashclient_auth_custom_params",
                        n_clicks=0,
                    ),
                    html.Div(id="custom_params_auth_launched", children="Not triggered yet."),
                ],
            ),
        ],
    )


@callback(
    Input("hps_status_check", "n_clicks"),
    State("url", "pathname"),
    Output("hps_status", "children"),
    prevent_initial_call=True,
)
def check_state(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        return project.steps.hps_simple_project_step.query_hps_status()


@callback(
    Input("trigger_dashclient_auth", "n_clicks"),
    State("url", "pathname"),
    Output("auth_launched", "children"),
    prevent_initial_call=True,
)
def launch_hps_auth_in_client(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        try:
            project.authenticate_hps()
            return "All good."
        except Exception:
            return "Something went wrong."


@callback(
    Input("trigger_dashclient_auth_custom_params", "n_clicks"),
    State("url", "pathname"),
    Output("custom_params_auth_launched", "children"),
    prevent_initial_call=True,
)
def launch_hps_auth_with_custom_params_in_client(n_clicks: int, project: EndToEndSolution):
    if n_clicks > 0:
        try:
            project.authenticate_hps(
                hps_server_url="https://127.0.0.1:8443/hps",
                client_id="rep-jms-web",
            )
            return "All good."
        except Exception:
            return "Something went wrong."
