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

"""Frontend of the long transaction step."""

from ansys.saf.glow.client import callback
from ansys.saf.glow.solution import MethodStatus
import dash
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, dcc, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from saf.solutions.examples.solution.definition import ExamplesSolution

dash.register_page(
    __name__,
    name="Long Transaction",
    path_template="/projects/<project_id>/long-transaction",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout(project: ExamplesSolution) -> html.Div:
    step = project.steps.long_transaction_step
    """Layout of the long transaction example page."""
    return html.Div(
        [
            html.H1(
                "Long-transaction streaming update",
                className="display-3",
                style={"font-size": "40px", "font-weight": "bold"},
            ),
            html.Hr(className="my-2"),
            html.Br(),
            dmc.Blockquote(
                "Use SAF GLOW to show a progress bar that displays the status of a long-running transaction.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            dmc.Button(
                "Run test",
                id="run-button",
                n_clicks=0,
                style={"font-size": "16px", "color": "var(--mantine-color-body)", "background-color": "#2790F1"},
            ),
            html.Br(),
            html.Br(),
            html.Div([dmc.Progress(id="completion-progress", className="mb-3", value=0)]),
            html.Div(id="status-line", children=["No transaction is running yet."]),
            dcc.Interval(id="interval-refresh", interval=1 * 1000, n_intervals=0, disabled=True),  # in milliseconds
        ]
    )


@callback(
    Output("status-line", "children"),
    Output("run-button", "disabled"),
    Output("interval-refresh", "disabled"),
    Output("completion-progress", "value"),
    Output("completion-progress", "label"),
    Input("run-button", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def start_long_running_transaction(n_clicks: int, project: ExamplesSolution) -> tuple[str, bool, bool, int, str]:
    """Start the long-running transaction."""
    if n_clicks <= 0:
        raise PreventUpdate
    step = project.steps.long_transaction_step
    step.processing = True
    step.current_increment = -1
    step.stream_updates()
    return "running", True, False, 0, ""


@callback(
    Output("status-line", "children"),
    Output("run-button", "disabled"),
    Output("interval-refresh", "disabled"),
    Output("completion-progress", "value"),
    Output("completion-progress", "label"),
    Input("interval-refresh", "n_intervals"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def update_status(_, project: ExamplesSolution) -> tuple[str, bool, bool, int, str]:
    """Update the progress bar with the status of the long-running transaction."""
    step = project.steps.long_transaction_step
    if not step.processing:
        raise PreventUpdate
    else:
        number_of_completed_increments = step.current_increment + 1
        progress = int((number_of_completed_increments * 100) / step.number_of_increments)
        if step.get_long_running_method_state("stream_updates").status == MethodStatus.Running:
            status = "running"
        else:
            status = "done"
            step.processing = False
        return (
            f"{step.status} {status}",
            step.processing,
            not step.processing,
            number_of_completed_increments,
            f"{progress}%",
        )
