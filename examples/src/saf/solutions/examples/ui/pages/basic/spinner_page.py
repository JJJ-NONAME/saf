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

"""Frontend of the Spinner step."""

from ansys.saf.glow.client import callback
import dash
from dash_extensions.enrich import Input, Output, State, dcc, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from saf.solutions.examples.solution.definition import ExamplesSolution

dash.register_page(
    __name__,
    name="Spinner",
    path_template="/projects/<project_id>/spinner",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout() -> html.Div:
    """Layout of the Spinner example page."""
    return html.Div(
        [
            html.H1("Spinner", className="display-3", style={"font-size": "40px", "font-weight": "bold"}),
            html.Hr(className="my-2"),
            html.Br(),
            dmc.Blockquote(
                "Add a Dash spinner to the solution UI to display loading states\
                while the solution is processing data.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            html.Br(),
            html.Br(),
            dmc.Button(
                "Start",
                id="spinner-start-button",
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
            dcc.Loading(
                id="loading",
                type="default",
                children=html.Div(
                    id="loading_output",
                    style={"margin-top": "50px"},
                ),
            ),
        ]
    )


@callback(
    Output("loading_output", "children"),
    Input("spinner-start-button", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def start_transaction(n_clicks: int, project: ExamplesSolution) -> html.Div:
    """Start the transaction."""
    step = project.steps.basic_step
    step.simple_blocking_process(wait_time=4)
    return html.Div("Transaction completed.")
