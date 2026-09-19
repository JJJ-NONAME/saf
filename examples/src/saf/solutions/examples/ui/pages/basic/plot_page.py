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

"""Frontend of the Plotly graph step."""

from ansys.saf.glow.client import callback
import dash
from dash_extensions.enrich import Input, Output, State, dcc, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from saf.solutions.examples.solution.definition import ExamplesSolution

dash.register_page(
    __name__,
    name="Plotly Graph",
    path_template="/projects/<project_id>/plotly-graph",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout(project: ExamplesSolution) -> html.Div:
    """Layout of the Plotly graph example page."""
    step = project.steps.basic_step
    return html.Div(
        [
            html.H1("Plotly graph", className="display-3", style={"font-size": "40px", "font-weight": "bold"}),
            dmc.Blockquote(
                "Use a Plotly graph to visualize parametric step-field data in a solution UI.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            html.Br(),
            html.Br(),
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            dmc.Card(
                                [
                                    dmc.CardSection(
                                        dmc.Text("Parameters", size="md", fw=700),
                                        style={
                                            "padding": "0.75rem 1rem",
                                            "backgroundColor": "#0A76DB",
                                            "color": "rgba(255, 255, 255, 1)",
                                            "borderRadius": "8px 8px 0 0",
                                        },
                                    ),
                                    dmc.CardSection(
                                        [
                                            html.Label(
                                                "Curve type",
                                                style={"font-size": "16px"},
                                            ),
                                            dmc.Select(
                                                id="curve_type_selection",
                                                data=["windmill", "flower", "vegas"],
                                                value="windmill",
                                                searchable=True,
                                                size="md",
                                            ),
                                        ],
                                        style={"padding": "1rem"},
                                    ),
                                ],
                                withBorder=True,
                                radius="md",
                                shadow="sm",
                                style={"overflow": "visible"},
                            )
                        ],
                        span=4,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Card(
                                [
                                    dmc.CardSection(
                                        dmc.Text("Plot", size="md", fw=700),
                                        style={
                                            "padding": "0.75rem 1rem",
                                            "backgroundColor": "#0A76DB",
                                            "color": "rgba(255, 255, 255, 1)",
                                            "borderRadius": "8px 8px 0 0",
                                        },
                                    ),
                                    dmc.CardSection(
                                        [
                                            html.Div(
                                                [
                                                    dcc.Graph(
                                                        id="graph",
                                                        figure={
                                                            "data": [
                                                                {
                                                                    "type": "scatter",
                                                                    "x": step.x_coords,
                                                                    "y": step.y_coords,
                                                                    "marker": {
                                                                        "color": "rgba(255,183,27,1)",
                                                                    },
                                                                    "line": {"width": 1},
                                                                    "mode": "lines",
                                                                },
                                                            ],
                                                            "layout": {
                                                                "width": 600,
                                                                "height": 600,
                                                                "xaxis": {"visible": False},
                                                                "yaxis": {"visible": False},
                                                                "paper_bgcolor": "rgba(0,0,0,0)",
                                                                "plot_bgcolor": "rgba(0,0,0,0)",
                                                                "margin": {
                                                                    "l": 0,
                                                                    "r": 0,
                                                                    "b": 0,
                                                                    "t": 0,
                                                                },
                                                            },
                                                        },
                                                    )
                                                ],
                                                style={
                                                    "width": "100%",
                                                    "display": "flex",
                                                    "align-items": "center",
                                                    "justify-content": "center",
                                                },
                                            ),
                                            dcc.Loading(
                                                type="circle",
                                                fullscreen=False,
                                                color="#ffb71b",
                                                style={
                                                    "background-color": "rgba(0, 0, 0, 0)",
                                                },
                                                children=html.Div(id="wait_completion"),
                                            ),
                                        ],
                                        style={"padding": "1rem"},
                                    ),
                                ],
                                withBorder=True,
                                radius="md",
                                shadow="sm",
                            )
                        ],
                        span=8,
                    ),
                ],
                gutter="md",
            ),
            html.Br(),
            html.Br(),
        ],
        style={"paddingLeft": "20px"},
    )


@callback(
    Output("graph", "figure"),
    Output("curve_type_selection", "disabled", allow_duplicate=True),
    Output("wait_completion", "children"),
    Input("curve_type_selection", "n_clicks"),
    Input("curve_type_selection", "value"),
    State("url", "pathname"),
    State("graph", "figure"),
    prevent_initial_call=True,
)
def draw_parametric_curve(
    n_click: int, selected_curve: str, project: ExamplesSolution, figure: dict
) -> tuple[dict, bool, bool]:
    """Plot the parametric curve."""
    step = project.steps.basic_step
    step.selected_curve = selected_curve
    step.compute_parametric_curve()
    figure["data"][0]["x"] = step.x_coords
    figure["data"][0]["y"] = step.y_coords
    return figure, False, True


@callback(
    Output("curve_type_selection", "disabled", allow_duplicate=True),
    Input("curve_type_selection", "value"),
    prevent_initial_call=True,
)
def disable_selection(selected_curve: str) -> bool:
    """Disable the curve type selection."""
    return True
