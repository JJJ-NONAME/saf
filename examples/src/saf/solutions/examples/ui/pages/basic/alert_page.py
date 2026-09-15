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

# ©2023, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Alert page."""


import time

from ansys.saf.glow.client import callback
from ansys.saf.glow.solution import MethodStatus
import dash
from dash_extensions.enrich import Input, Output, State, ctx, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from saf.solutions.examples.solution.definition import ExamplesSolution

dash.register_page(
    __name__,
    name="Alert",
    path_template="/projects/<project_id>/alert",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout() -> html.Div:
    """Layout of the alert example page."""
    return html.Div(
        [
            html.H1("Alert", className="display-3", style={"font-size": "40px", "font-weight": "bold"}),
            html.Hr(className="my-2"),
            html.Br(),
            dmc.Blockquote(
                "Use Dash alerts to display messages in a solution UI.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            html.Br(),
            html.Div(
                html.Div(
                    [
                        dmc.Button(
                            "Run method with success",
                            id="trigger_run_with_success",
                            leftSection=DashIconify(icon="streamline:startup-solid"),
                            color="lime",
                            radius="xl",
                            disabled=False,
                            className="mantine-button",
                            style={
                                "font-size": "16px",
                                "color": "var(--mantine-color-body)",
                                "margin-right": "6px",
                                "padding": "8px",
                            },
                        ),
                        dmc.Button(
                            "Run method with failure",
                            id="trigger_run_with_failure",
                            leftSection=DashIconify(icon="streamline:startup-solid"),
                            color="red",
                            radius="xl",
                            disabled=False,
                            className="mantine-button",
                            style={
                                "font-size": "16px",
                                "color": "var(--mantine-color-body)",
                                "margin-left": "6px",
                                "padding": "8px",
                            },
                        ),
                    ],
                    style={"display": "flex", "justify-content": "center"},
                ),
                style={
                    "width": "50%",
                    "display": "inline-block",
                    "justify-content": "center",
                    "align-items": "center",
                    "margin-left": "25%",
                },
            ),
            html.Br(),
            html.Br(),
            html.Div(
                dmc.Alert(
                    id="alert",
                ),
                style={
                    "textAlign": "center",
                    "margin-left": "25%",
                    "width": "50%",
                },
            ),
        ]
    )


@callback(
    Output("alert", "title"),
    Output("alert", "children"),
    Output("alert", "color"),
    Input("trigger_run_with_success", "n_clicks"),
    Input("trigger_run_with_failure", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def run_method(
    trigger_run_with_success: int, trigger_run_with_failure: int, project: ExamplesSolution
) -> tuple[str, str, str]:
    """Trigger a simple method and display an alert based on the method result."""
    step = project.steps.basic_step
    if ctx.triggered_id == "trigger_run_with_success" and trigger_run_with_success:
        force_failure = False
    if ctx.triggered_id == "trigger_run_with_failure" and trigger_run_with_failure:
        force_failure = True
    method = step.simple_long_running_process(force_failure=force_failure, wait_time=4)

    method_state = method.get_state()
    while method_state.status not in [MethodStatus.Completed, MethodStatus.Failed]:
        time.sleep(0.5)
        method_state = method.get_state()

    if method_state.status == MethodStatus.Completed:
        title = "Info"
        message = "Method completed successfully."
        color = "lime"
    elif method_state.status == MethodStatus.Failed:
        title = "Error"
        message = "Method failed."
        color = "red"
    return title, message, color
