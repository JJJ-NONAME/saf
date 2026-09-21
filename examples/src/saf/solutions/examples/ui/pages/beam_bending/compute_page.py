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

"""Frontend of the first step."""

import logging
from typing import Tuple

from ansys.saf.glow.client import DashClient, callback
from ansys.saf.glow.solution import MethodStatus
from ansys.solutions.dash_super_components import InputForm
import dash
from dash_extensions.enrich import Input, Output, State, ctx, dcc, html, no_update
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from saf.solutions.examples.solution.definition import ExamplesSolution

logger = logging.getLogger(__name__)

dash.register_page(
    __name__,
    name="Beam Bending Compute",
    path_template="/projects/<project_id>/beam-bending-compute",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout(project: ExamplesSolution) -> html.Div:
    """Layout of the compute page."""
    # Left side of the page -------------------------------------------------------------------------------------------

    step = project.steps.beam_bending_step
    geometrical_parameters_form = InputForm(
        [
            {
                "id": "length-a-row",
                "label": "a",
                "fields": [
                    {
                        "type": "NumberInput",
                        "value": step.length_a,
                        "min": 0,
                        "id": "length-a",
                        "required": True,
                    }
                ],
                "unit": "mm",
            },
            {
                "id": "length-b-row",
                "label": "b",
                "fields": [
                    {
                        "type": "NumberInput",
                        "value": step.length_b,
                        "min": 0,
                        "id": "length-b",
                        "required": True,
                    }
                ],
                "unit": "mm",
            },
            {
                "id": "diameter-row",
                "label": "d",
                "fields": [
                    {
                        "type": "NumberInput",
                        "value": step.diameter,
                        "min": 0,
                        "id": "diameter",
                        "required": True,
                    }
                ],
                "unit": "mm",
            },
        ],
        aio_id="geometrical-parameters-form",
        title="Geometrical parameters",
        columns=["label", "fields", "unit"],
    )

    materials_properties_form = InputForm(
        [
            {
                "id": "elasticity-modulus-row",
                "label": "Elasticity Modulus",
                "fields": [
                    {
                        "type": "NumberInput",
                        "value": step.elasticity_modulus,
                        "min": 0,
                        "id": "elasticity-modulus",
                        "required": True,
                    }
                ],
                "unit": "MPa",
            },
            {
                "id": "poisson-ratio-row",
                "label": "Poisson's Ratio",
                "fields": [
                    {
                        "type": "NumberInput",
                        "value": step.poisson_ratio,
                        "min": 0,
                        "id": "poisson-ratio",
                        "required": True,
                    }
                ],
                "unit": None,
            },
        ],
        aio_id="material-properties-form",
        title="Material properties",
        columns=["label", "fields", "unit"],
    )

    loading_parameters_form = InputForm(
        [
            {
                "id": "load-row",
                "label": "Concentrated Force",
                "fields": [
                    {
                        "type": "NumberInput",
                        "value": step.load,
                        "min": 0,
                        "id": "load",
                        "required": True,
                    }
                ],
                "unit": "N",
            },
        ],
        aio_id="loading-parameters-form",
        title="Loading parameters",
        columns=["label", "fields", "unit"],
    )

    numerical_parameters_form = InputForm(
        [
            {
                "id": "nbr-of-pts-row",
                "label": "Number of points to compute deflection (theoretical solution)",
                "fields": [
                    {
                        "type": "NumberInput",
                        "value": step.nbr_of_pts,
                        "min": 0,
                        "id": "nbr-of-pts",
                        "required": True,
                    }
                ],
                "unit": None,
            },
            {
                "id": "mapdl-nbr-of-elements-row",
                "label": "Number of elements (MAPDL solution)",
                "fields": [
                    {
                        "type": "NumberInput",
                        "value": step.mapdl_nbr_of_elements,
                        "min": 0,
                        "id": "mapdl-nbr-of-elements",
                        "required": True,
                    }
                ],
                "unit": None,
            },
        ],
        aio_id="numerical-parameters-form",
        title="Numerical parameters",
        columns=["label", "fields", "unit"],
    )

    # Right side of the page ------------------------------------------------------------------------------------------

    image_card = html.Div(
        dmc.Card(
            [
                dmc.Image(
                    src="/assets/images/beam_model.png",
                    style={
                        "width": "100%",
                        "border": "1px solid var(--mantine-color-default-border)",
                        "border-radius": "10px",
                        "padding": "10px",
                    },
                ),
                dmc.CardSection(
                    "Problem parametrization",
                    style={"text-align": "center"},
                ),
            ],
            style={
                "width": "40rem",
            },
        ),
        style={
            "width": "100%",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
        },
    )

    graph = html.Div(
        dcc.Graph(
            id="deflection-graph",
            figure={
                "data": [
                    {
                        "type": "scatter",
                        "name": "initial state",
                        "x": [0, step.length_a + step.length_b],
                        "y": [0, 0],
                        "marker": {"color": "rgba(0,0,0,1)"},
                        "line": {"width": 6},
                    },
                    {
                        "type": "scatter",
                        "name": "deformed state (theoretical)",
                        "x": (
                            step.theoretical_deflection[0]
                            if step.theoretical_deflection and len(step.theoretical_deflection) > 0
                            else []
                        ),
                        "y": (
                            step.theoretical_deflection[1]
                            if step.theoretical_deflection and len(step.theoretical_deflection) > 0
                            else []
                        ),
                        "marker": {"color": "rgba(255,183,27,1)"},
                        "line": {"width": 6},
                    },
                    {
                        "type": "scatter",
                        "name": "deformed state (MAPDL)",
                        "x": (
                            step.mapdl_deflection[0] if step.mapdl_deflection and len(step.mapdl_deflection) > 0 else []
                        ),
                        "y": (
                            step.mapdl_deflection[1] if step.mapdl_deflection and len(step.mapdl_deflection) > 0 else []
                        ),
                        "marker": {"color": "rgba(80,22,74,1)"},
                        "line": {"width": 6},
                    },
                ],
                "layout": {
                    "title": "Deflection",
                    "legend": {"orientation": "h", "x": 0.3, "y": 1.1},
                    "xaxis": {"title": "x (mm)", "range": [0, None]},
                    "yaxis": {"title": "y (mm)"},
                    "width": 750,
                    "margin": {"l": 40, "r": 0, "t": 0, "b": 0},
                    "annotations": [
                        {
                            "ax": step.length_a,
                            "axref": "x",
                            "ay": 20,
                            "ayref": "y",
                            "x": step.length_a,
                            "arrowcolor": "red",
                            "xref": "x",
                            "y": 0,
                            "yref": "y",
                            "arrowwidth": 2.5,
                            "arrowside": "end",
                            "arrowsize": 1,
                            "arrowhead": 4,
                        }
                    ],
                    "paper_bgcolor": "rgba(0,0,0,0)",
                    "plot_bgcolor": "rgba(0,0,0,0)",
                },
            },
        ),
        style={
            "width": "100%",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
        },
    )

    return html.Div(
        [
            html.H1(
                "Compute beam deflection", className="display-3", style={"font-size": "40px", "font-weight": "bold"}
            ),
            dmc.Grid(
                [
                    dmc.GridCol(
                        dmc.Stack(
                            [
                                geometrical_parameters_form,
                                materials_properties_form,
                                loading_parameters_form,
                                numerical_parameters_form,
                                html.Br(),
                                html.Br(),
                            ],
                            align="stretch",
                            gap="md",
                        ),
                        span=6,
                    ),
                    dmc.GridCol(
                        [
                            dmc.Button(
                                "Compute",
                                id="compute-deflection",
                                color="blue",
                                size="md",
                                radius="sm",
                                leftSection=DashIconify(icon="fluent:math-formula-16-filled"),
                                style={
                                    "font-size": "17px",
                                    "background-color": "#2790F1",
                                },
                            ),
                            graph,
                            image_card,
                            html.Br(),
                            html.Br(),
                        ],
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "20px",
                        },
                        span=6,
                    ),
                ],
                gutter="xs",
            ),
            dcc.Loading(
                type="circle",
                fullscreen=True,
                color="#ffb71b",
                style={
                    "background-color": "rgba(55, 58, 54, 0.1)",
                },
                children=html.Div(id="wait-for-completion"),
            ),
            dcc.Store(id="trigger-compute-after-button-click", data=0, storage_type="memory"),
            DashClient.create_event_listener(
                step,
                id="compute-theoretical-beam-deflection-listener",
                stream_name="compute-theoretical-beam-deflection",
            ),
            DashClient.create_event_listener(
                step, id="mapdl-preprocessing-listener", stream_name="mapdl-preprocessing"
            ),
            DashClient.create_event_listener(step, id="mapdl-solve-listener", stream_name="mapdl-solve"),
            DashClient.create_event_listener(
                step, id="mapdl-postprocessing-listener", stream_name="mapdl-postprocessing"
            ),
        ],
        style={"paddingLeft": "20px"},
    )


@callback(
    Output("compute-deflection", "disabled", allow_duplicate=True),
    Output("compute-deflection", "loading", allow_duplicate=True),
    Output(
        InputForm.ids.field("geometrical-parameters-form", "NumberInput", "length-a", "length-a-row"),
        "disabled",
        allow_duplicate=True,
    ),
    Output(
        InputForm.ids.field("geometrical-parameters-form", "NumberInput", "length-b", "length-b-row"),
        "disabled",
        allow_duplicate=True,
    ),
    Output(
        InputForm.ids.field("geometrical-parameters-form", "NumberInput", "diameter", "diameter-row"),
        "disabled",
        allow_duplicate=True,
    ),
    Output(
        InputForm.ids.field("material-properties-form", "NumberInput", "elasticity-modulus", "elasticity-modulus-row"),
        "disabled",
        allow_duplicate=True,
    ),
    Output(
        InputForm.ids.field("material-properties-form", "NumberInput", "poisson-ratio", "poisson-ratio-row"),
        "disabled",
        allow_duplicate=True,
    ),
    Output(
        InputForm.ids.field("loading-parameters-form", "NumberInput", "load", "load-row"),
        "disabled",
        allow_duplicate=True,
    ),
    Output(
        InputForm.ids.field("numerical-parameters-form", "NumberInput", "nbr-of-pts", "nbr-of-pts-row"),
        "disabled",
        allow_duplicate=True,
    ),
    Output(
        InputForm.ids.field(
            "numerical-parameters-form", "NumberInput", "mapdl-nbr-of-elements", "mapdl-nbr-of-elements-row"
        ),
        "disabled",
        allow_duplicate=True,
    ),
    Output("trigger-compute-after-button-click", "data"),
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("compute-deflection", "n_clicks"),
    State("trigger-compute-after-button-click", "data"),
    prevent_initial_call=True,
)
def disable_inputs(
    n_clicks: int, trigger_compute: int
) -> Tuple[bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, dict]:
    """Disable the input fields and the compute button during the computation."""
    if n_clicks and ctx.triggered_id == "compute-deflection":
        notification = [
            dict(
                action="show",
                id="computation-status-notification",
                title="Starting computation",
                message="The computation will start shortly. Please wait...",
                loading=True,
                color="orange",
                autoClose=False,
            )
        ]
        return [True for _ in range(10)] + [trigger_compute + 1, notification]
    return [no_update for _ in range(12)]


@callback(
    Output("notification-container", "sendNotifications"),
    Input("trigger-compute-after-button-click", "data"),
    State(
        InputForm.ids.field("geometrical-parameters-form", "NumberInput", "length-a", "length-a-row"),
        "value",
    ),
    State(
        InputForm.ids.field("geometrical-parameters-form", "NumberInput", "length-b", "length-b-row"),
        "value",
    ),
    State(
        InputForm.ids.field("geometrical-parameters-form", "NumberInput", "diameter", "diameter-row"),
        "value",
    ),
    State(
        InputForm.ids.field("material-properties-form", "NumberInput", "elasticity-modulus", "elasticity-modulus-row"),
        "value",
    ),
    State(
        InputForm.ids.field("material-properties-form", "NumberInput", "poisson-ratio", "poisson-ratio-row"),
        "value",
    ),
    State(InputForm.ids.field("loading-parameters-form", "NumberInput", "load", "load-row"), "value"),
    State(
        InputForm.ids.field("numerical-parameters-form", "NumberInput", "nbr-of-pts", "nbr-of-pts-row"),
        "value",
    ),
    State(
        InputForm.ids.field(
            "numerical-parameters-form", "NumberInput", "mapdl-nbr-of-elements", "mapdl-nbr-of-elements-row"
        ),
        "value",
    ),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def start_computation(
    start_computation: int,
    length_a: float,
    length_b: float,
    diameter: float,
    elasticity_modulus: float,
    poisson_ratio: float,
    load: float,
    nbr_of_pts: int,
    mapdl_nbr_of_elements: int,
    project: ExamplesSolution,
) -> tuple[bool, bool, bool, bool, bool, bool, bool, bool, bool, bool, list]:
    """Trigger the computation of the beam deflection when the "Compute" button is clicked."""
    if start_computation and ctx.triggered_id == "trigger-compute-after-button-click":
        step = project.steps.beam_bending_step
        step.length_a = length_a
        step.length_b = length_b
        step.diameter = diameter
        step.elasticity_modulus = elasticity_modulus
        step.poisson_ratio = poisson_ratio
        step.load = load
        step.nbr_of_pts = nbr_of_pts
        step.mapdl_nbr_of_elements = mapdl_nbr_of_elements

        logger.info("Computing theoretical beam deflection")
        step.compute_theoretical_beam_deflection()

        try:
            logger.info("Starting MAPDL instance")
            step.start_mapdl()
        except Exception as e:
            logger.exception("Failed to start MAPDL instance")
            return [
                dict(
                    title="Error",
                    id="mapdl-instance-error-notification",
                    action="show",
                    message="Failed to start MAPDL instance. Check server logs for details.",
                )
            ]

        logger.info("Starting MAPDL preprocessing")
        step.mapdl_preprocessing()

        return [
            dict(
                action="update",
                id="computation-status-notification",
                title="Computation started",
                message="The computation has been started. This may take a few moments.",
                loading=True,
                color="blue",
                autoClose=False,
            )
        ]

    return no_update


@callback(
    Output("notification-container", "sendNotifications"),
    Output("deflection-graph", "figure"),
    Output("compute-deflection", "disabled"),
    Output("compute-deflection", "loading"),
    Output(
        InputForm.ids.field("geometrical-parameters-form", "NumberInput", "length-a", "length-a-row"),
        "disabled",
    ),
    Output(
        InputForm.ids.field("geometrical-parameters-form", "NumberInput", "length-b", "length-b-row"),
        "disabled",
    ),
    Output(
        InputForm.ids.field("geometrical-parameters-form", "NumberInput", "diameter", "diameter-row"),
        "disabled",
    ),
    Output(
        InputForm.ids.field("material-properties-form", "NumberInput", "elasticity-modulus", "elasticity-modulus-row"),
        "disabled",
    ),
    Output(
        InputForm.ids.field("material-properties-form", "NumberInput", "poisson-ratio", "poisson-ratio-row"),
        "disabled",
    ),
    Output(InputForm.ids.field("loading-parameters-form", "NumberInput", "load", "load-row"), "disabled"),
    Output(
        InputForm.ids.field("numerical-parameters-form", "NumberInput", "nbr-of-pts", "nbr-of-pts-row"),
        "disabled",
    ),
    Output(
        InputForm.ids.field(
            "numerical-parameters-form", "NumberInput", "mapdl-nbr-of-elements", "mapdl-nbr-of-elements-row"
        ),
        "disabled",
    ),
    Input("compute-theoretical-beam-deflection-listener", "message"),
    Input("mapdl-preprocessing-listener", "message"),
    Input("mapdl-solve-listener", "message"),
    Input("mapdl-postprocessing-listener", "message"),
    State("url", "pathname"),
    State("deflection-graph", "figure"),
    prevent_initial_call=True,
)
def update_computation_status(
    theoretical_beam_deflection_termination_event_message: str,
    mapdl_preprocessing_termination_event_message: str,
    mapdl_solve_termination_event_message: str,
    mapdl_postprocessing_termination_event_message: str,
    project: ExamplesSolution,
    figure: dict,
) -> list:
    """Update the UI based on the status of the computation."""
    step = project.steps.beam_bending_step

    methods = ["compute_theoretical_beam_deflection", "mapdl_preprocessing", "mapdl_solve", "mapdl_postprocessing"]
    method_statuses = [step.get_long_running_method_state(method).status for method in methods]

    if ctx.triggered_id == "mapdl-preprocessing-listener" and mapdl_preprocessing_termination_event_message:
        if method_statuses[1] == MethodStatus.Completed:
            step.mapdl_solve()
    elif ctx.triggered_id == "mapdl-solve-listener" and mapdl_solve_termination_event_message:
        if method_statuses[2] == MethodStatus.Completed:
            step.mapdl_postprocessing()

    disable_inputs = [False for _ in range(10)]
    if any(status == MethodStatus.Failed for status in method_statuses):
        notification = [
            dict(
                action="update",
                id="computation-status-notification",
                title="Computation failed",
                message="The computation has failed. Please check the logs for more details.",
                loading=False,
                color="red",
                autoClose=2000,
            )
        ]
        return [notification] + [no_update] + disable_inputs
    elif all(status == MethodStatus.Completed for status in method_statuses):
        notification = [
            dict(
                action="update",
                id="computation-status-notification",
                title="Computation completed",
                message="The computation has been completed successfully.",
                loading=False,
                color="green",
                autoClose=2000,
            )
        ]

        figure["data"][0]["x"] = [0, step.length_a + step.length_b]
        figure["data"][1]["x"] = step.theoretical_deflection[0]
        figure["data"][1]["y"] = step.theoretical_deflection[1]
        figure["data"][2]["x"] = step.mapdl_deflection[0]
        figure["data"][2]["y"] = step.mapdl_deflection[1]
        figure["layout"]["annotations"][0]["ax"] = step.length_a
        figure["layout"]["annotations"][0]["x"] = step.length_a

        return [notification] + [figure] + disable_inputs
    else:
        return [no_update for _ in range(12)]
