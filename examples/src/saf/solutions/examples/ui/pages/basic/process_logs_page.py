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

"""Front end of the Process logs step."""

from ansys.saf.glow.client import callback
from ansys.saf.glow.solution import MethodStatus
import dash
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, ctx, dcc, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from saf.solutions.examples.solution.definition import ExamplesSolution

dash.register_page(
    __name__,
    name="Process Logs",
    path_template="/projects/<project_id>/process-logs",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout(project: ExamplesSolution) -> html.Div:
    """Layout of the Process logs example page."""
    logs_container = dmc.Card(
        [
            dmc.CardSection(
                dmc.Group(
                    children=[
                        dmc.Text("Logs", fw=500),
                        dmc.Tooltip(
                            dmc.ActionIcon(
                                DashIconify(icon="mdi:delete-sweep", width=24),
                                id="clear-logs-button",
                                color="gray",
                                variant="transparent",
                            ),
                            label="Clear Logs",
                            position="left",
                        ),
                    ],
                    justify="space-between",
                ),
                withBorder=True,
                inheritPadding=True,
                py="xs",
            ),
            dmc.Space(h=20),
            html.Div(
                id="log_container",
                children=get_logs(project),
                style={
                    "height": "600px",
                    "width": "100%",
                    "overflowY": "scroll",
                },
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
    )

    return html.Div(
        [
            html.H1("Process logs", className="display-3", style={"font-size": "40px", "font-weight": "bold"}),
            html.Hr(className="my-2"),
            dmc.Space(h=20),
            dmc.Blockquote(
                "Read the log files for a process and display their content in a solution UI.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            dmc.Space(h=20),
            dmc.Button(
                "Start",
                id="start_button",
                variant="filled",
                radius="xl",
                style={
                    "font-size": "16px",
                    "width": "20%",
                    "color": "var(--mantine-color-body)",
                    "background-color": "#2790F1",
                },
                leftSection=DashIconify(icon="streamline:startup-solid"),
            ),
            dmc.Space(h=20),
            dmc.Grid(
                [dmc.GridCol(logs_container, span=9)],
                grow=True,
                gutter="xs",
            ),
            dcc.Interval(
                id="interval",
                interval=1000,
                n_intervals=0,
                disabled=not process_in_progress(project),
            ),
            html.Br(),
            html.Br(),
        ]
    )


@callback(
    Output("interval", "disabled"),
    Output("start_button", "disabled"),
    Output("start_button", "loading"),
    Input("start_button", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def start_transaction(n_clicks: int, project: ExamplesSolution) -> tuple[bool, bool, bool]:
    """Start the transaction."""
    if ctx.triggered_id == "start_button" and n_clicks:  # pyright: ignore[reportUnknownMemberType]
        step = project.steps.basic_step
        step.write_to_file(wait_time=10.0)
        return False, True, True
    raise PreventUpdate


@callback(
    Output("log_container", "children"),
    Output("interval", "disabled"),
    Output("start_button", "disabled"),
    Output("start_button", "loading"),
    Input("interval", "n_intervals"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def update_logs(n_intervals: int, project: ExamplesSolution) -> tuple[html.Div | None, bool, bool, bool]:
    """Update the logs."""
    if ctx.triggered_id == "interval" and n_intervals:  # pyright: ignore[reportUnknownMemberType]
        if process_in_progress(project):
            disable_monitoring = False
            disable_start_button = True
            loading_start_button = True
        else:
            disable_monitoring = True
            disable_start_button = False
            loading_start_button = False
        return get_logs(project), disable_monitoring, disable_start_button, loading_start_button
    raise PreventUpdate


@callback(
    Output("log_container", "children"),
    Input("clear-logs-button", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def clear_logs(n_clicks: int, project: ExamplesSolution) -> html.Div:
    """Clear the log container."""
    step = project.steps.basic_step
    step.clear_logs()
    return html.Div("No logs are available yet.")


def process_in_progress(project: ExamplesSolution) -> bool:
    """Return True if the process is in progress."""
    step = project.steps.basic_step
    return True if step.get_long_running_method_state("write_to_file").status == MethodStatus.Running else False


def get_logs(project: ExamplesSolution) -> html.Div | None:
    """Return the children containing the lsdyna logs."""
    try:
        step = project.steps.basic_step
        log_file = project.storage_scope.get_cached(step.log_file)
    except Exception:
        return html.Div("No logs are available yet.")
    try:
        content = log_file.read_text()
    except Exception as e:
        return html.Div("Error reading log file: " + str(e))
    return html.Div(
        [
            html.Pre(
                content,
                style={"whiteSpace": "pre-wrap", "wordBreak": "break-all", "fontSize": "10px"},
            ),
        ]
    )
