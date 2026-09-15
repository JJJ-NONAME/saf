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

# ©2026, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Frontend of the game of life page."""

import json
import logging

from ansys.saf.glow.client import DashClient, callback
from ansys.saf.glow.solution import MethodStatus
import dash
from dash import Patch
from dash_extensions.enrich import Input, Output, State, dcc, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objects as go

from saf.solutions.examples.solution.definition import ExamplesSolution
from saf.solutions.examples.solution.game_of_life import PatternLibrary

logger = logging.getLogger(__name__)

dash.register_page(
    __name__,
    name="Conway's Game of Life",
    path_template="/projects/<project_id>/game-of-life",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout(project: ExamplesSolution) -> html.Div:
    """Layout of the game of life page."""
    step = project.steps.game_of_life_step
    return html.Div(
        [
            html.H1(
                "Conway's Game of Life",
                className="display-3",
                style={"font-size": "40px", "font-weight": "bold"},
            ),
            html.Hr(className="my-2"),
            dmc.Space(h=20),
            dmc.Blockquote(
                [
                    "This is an implementation of ",
                    dmc.Anchor(
                        "Conway's Game of Life",
                        href="https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life",
                        target="_blank",
                        underline="always",
                    ),
                    ". It demonstrates how to build a simple SAF application "
                    "from backend transactions to frontend visualization.",
                ],
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            dmc.Space(h=20),
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Divider(
                                label="Initialization",
                                styles={"label": {"fontSize": "18px"}},
                            ),
                            dmc.Select(
                                label="Select Pattern",
                                id="pattern-select",
                                value="blinker",
                                searchable=True,
                                clearable=False,
                                data=[
                                    {
                                        "value": pattern,
                                        "label": pattern.replace("_", " ").title(),
                                    }
                                    for pattern in PatternLibrary().get_pattern_list() + ["random"]
                                ],
                            ),
                            dmc.Space(h=20),
                            dmc.NumberInput(
                                label="Max Iterations",
                                id="max-iterations",
                                value=10,
                                min=1,
                                type="number",
                                style={"width": "100%"},
                            ),
                            dmc.Space(h=20),
                            html.Div("Grid Size"),
                            dmc.Slider(
                                id="grid-size",
                                value=20,
                                min=5,
                                max=100,
                                step=1,
                            ),
                            dmc.Space(h=20),
                            dmc.Button(
                                "Start Simulation",
                                leftSection=html.Img(src=dash.get_asset_url("icons/mdi--play.svg")),
                                id="start-simulation",
                                variant="filled",
                                size="sm",
                                style={"width": "100%"},
                            ),
                            dmc.Space(h=40),
                            dmc.Divider(
                                label="Simulation Status",
                                styles={"label": {"fontSize": "18px"}},
                            ),
                            dmc.Group(
                                [
                                    html.Div("Iteration:"),
                                    dmc.Badge("0", id="iteration-counter", size="lg"),
                                    dmc.Progress(
                                        value=0,
                                        id="progress-bar",
                                        size="xl",
                                        radius="xl",
                                        style={"width": "100%"},
                                    ),
                                ],
                            ),
                        ],
                        span=3,
                    ),
                    dmc.GridCol(
                        dcc.Graph(
                            id="heatmap",
                            figure=go.Figure(
                                data=go.Heatmap(
                                    zmin=0,
                                    zmax=1,
                                    colorscale=[[0, "black"], [1, "white"]],
                                    xgap=1,
                                    ygap=1,
                                    showscale=False,
                                ),
                                layout=go.Layout(
                                    xaxis=dict(
                                        visible=False,
                                        scaleanchor="y",
                                    ),
                                    yaxis=dict(visible=False, autorange="reversed"),
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="#222",
                                    autosize=True,
                                    margin=dict(l=0, r=0, t=0, b=0),
                                ),
                            ),
                            style={
                                "width": "800px",
                                "height": "600px",
                                "display": "block",
                                "marginLeft": "auto",
                                "marginRight": "auto",
                            },
                            config={"displayModeBar": False},
                        ),
                        span=9,
                        style={
                            "display": "flex",
                            "justifyContent": "center",
                            "alignItems": "center",
                        },
                    ),
                ],
                justify="center",
                style={
                    "margin": "0 auto",
                    "maxWidth": "1200px",
                    "width": "100%",
                    "paddingRight": "60px",
                    "paddingLeft": "20px",
                },
            ),
            DashClient.create_event_listener(step, stream_name="my-stream", id="update-heatmap"),
            DashClient.create_event_listener(step, stream_name="simulate", id="termination"),
            html.Div(id="notifications-container"),
        ]
    )


@callback(
    Output("heatmap", "figure", allow_duplicate=True),
    Input("pattern-select", "value"),
    Input("grid-size", "value"),
    State("url", "pathname"),
)
def update_initial_pattern(pattern_select: str, grid_size: int, project: ExamplesSolution) -> Patch:
    """Update the initial pattern."""
    step = project.steps.game_of_life_step
    step.selected_pattern = pattern_select
    step.grid_size = grid_size
    step.display_initial_state()
    patched_figure = Patch()
    patched_figure["data"][0]["z"] = np.array(step.initial_grid_state)
    return patched_figure


@callback(
    Output("notifications-container", "children"),
    Output("start-simulation", "loading"),
    Output("start-simulation", "disabled"),
    Output("max-iterations", "disabled"),
    Output("grid-size", "disabled"),
    Output("pattern-select", "disabled"),
    Output("iteration-counter", "children", allow_duplicate=True),
    Output("progress-bar", "value", allow_duplicate=True),
    Input("start-simulation", "n_clicks"),
    State("pattern-select", "value"),
    State("max-iterations", "value"),
    State("grid-size", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def start_simulation(
    start_simulation: int,
    pattern: str,
    max_iterations: int,
    grid_size: int,
    project: ExamplesSolution,
) -> tuple[dmc.Notification, bool, bool, bool, bool, bool, str, int]:
    """Trigger the simulation."""
    step = project.steps.game_of_life_step
    step.selected_pattern = pattern
    step.max_iterations = max_iterations
    step.grid_size = grid_size
    try:
        step.simulate()
    except Exception as e:
        return (
            dmc.Notification(
                title="Error",
                message=str(e),
                color="red",
                id={"type": "notification", "index": "simulation-error"},
                autoClose=False,
                action="show",
            ),
            False,
            False,
            False,
            False,
            False,
            "0/{}".format(max_iterations),
            0,
        )

    return (
        dmc.Notification(
            title="Simulation Started",
            message=f"Simulation started with pattern: {pattern}",
            color="lime",
            id={"type": "notification", "index": "simulation-started"},
            autoClose=True,
            action="show",
        ),
        True,
        True,
        True,
        True,
        True,
        "0/{}".format(max_iterations),
        0,
    )


@callback(
    Output("heatmap", "figure"),
    Output("iteration-counter", "children"),
    Output("progress-bar", "value"),
    Input("update-heatmap", "message"),
    State("max-iterations", "value"),
    prevent_initial_call=True,
)
def update_graph(message: dict, max_iterations: int) -> tuple[Patch, str, int]:
    """Update the grid."""
    data = json.loads(message.get("data"))
    patched_figure = Patch()
    patched_figure["data"][0]["z"] = np.array(data.get("grid"))
    iteration = data.get("iteration", 0)
    return (
        patched_figure,
        f"{iteration}/{max_iterations}",
        iteration / max_iterations * 100,
    )


@callback(
    Output("notifications-container", "children"),
    Output("start-simulation", "loading"),
    Output("start-simulation", "disabled"),
    Output("max-iterations", "disabled"),
    Output("grid-size", "disabled"),
    Output("pattern-select", "disabled"),
    Input("termination", "message"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def enable_new_simulation(
    message: dict, project: ExamplesSolution
) -> tuple[dmc.Notification, bool, bool, bool, bool, bool]:
    """Enable starting a new simulation after termination."""
    step = project.steps.game_of_life_step
    status = step.get_method_state("simulate").status
    if status == MethodStatus.Completed:
        notification = dmc.Notification(
            title="Simulation Completed",
            message="The simulation has completed successfully.",
            color="lime",
            id={"type": "notification", "index": "simulation-completed"},
            autoClose=True,
            action="show",
        )
    elif status == MethodStatus.Failed:
        notification = dmc.Notification(
            title="Simulation Failed",
            message="The simulation has failed or was terminated.",
            color="red",
            id={"type": "notification", "index": "simulation-failed"},
            autoClose=True,
            action="show",
        )
    return notification, False, False, False, False, False
