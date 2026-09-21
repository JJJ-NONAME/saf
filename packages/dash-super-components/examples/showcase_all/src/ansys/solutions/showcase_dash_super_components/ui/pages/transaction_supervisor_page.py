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


"""Frontend of the transaction supervisor page."""

from ansys.saf.glow.client import callback
from ansys.solutions.dash_super_components import TransactionSupervisor
from ansys.solutions.dash_super_components.utils.svg_icons import (
    IconNames,
    create_icon_span,
)
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, Trigger, ctx, dcc, html
import dash_mantine_components as dmc

from ansys.solutions.showcase_dash_super_components.solution.definition import (
    SuperComponentsExamplesSolution,
)
from ansys.solutions.showcase_dash_super_components.solution.simple_step import SimpleStep
from ansys.solutions.showcase_dash_super_components.ui.components.page_template import (
    layout as page_layout,
)
from ansys.solutions.showcase_dash_super_components.ui.utilities.common_classes import (
    CommonCSSClassNames,
)
from ansys.solutions.showcase_dash_super_components.ui.utilities.common_colors import CommonColors

INFO_CARD_TEXT = [
    "Transaction Supervisor component is used to monitor the status of a transaction method.",
]

_OUTPUT_INITIAL = "Not available"


def layout(step: SimpleStep) -> html.Div:
    """Layout of the transaction supervisor page."""
    main_content = html.Div(
        [
            dcc.Store(id="computation_result"),
            html.Div(
                children=[
                    dmc.Grid(
                        [
                            dmc.GridCol(
                                [
                                    dmc.NumberInput(
                                        id="input_1",
                                        label="Input value 1",
                                        value=step.input_1,
                                    ),
                                    dmc.NumberInput(
                                        id="input_2",
                                        label="Input value 2",
                                        value=step.input_2,
                                    ),
                                ],
                                span="content",
                            ),
                            dmc.GridCol(
                                html.Div(
                                    [
                                        dmc.Text(
                                            "Sum Result",
                                            fw=700,
                                            size="sm",
                                            c=CommonColors.MANTINE_DIMMED,
                                        ),
                                        dmc.Text(
                                            id="output_value",
                                            size="xl",
                                            fw=700,
                                            mt=4,
                                        ),
                                    ],
                                    style={
                                        "borderLeft": "3px solid "
                                        + CommonColors.MANTINE_PRIMARY_COLOR,
                                        "paddingLeft": "12px",
                                        "width": "200px",
                                    },
                                ),
                                span="content",
                                style={
                                    "display": "flex",
                                    "alignItems": "flex-end",
                                    "paddingBottom": "4px",
                                },
                            ),
                        ],
                        gutter="xl",
                        align="center",
                    ),
                    dmc.Space(h=40),
                    html.Div(
                        [
                            dmc.Button(
                                "Compute sum with success",
                                id="compute_with_success",
                                leftSection=create_icon_span(
                                    IconNames.STREAMLINE_STARTUP,
                                    size_px=16,
                                    color=CommonColors.WHITE,
                                ),
                                color=CommonColors.GREEN,
                                disabled=False,
                                className=CommonCSSClassNames.MANTINE_BUTTON,
                            ),
                            dmc.Button(
                                "Compute sum with error",
                                id="compute_with_error",
                                leftSection=create_icon_span(
                                    IconNames.STREAMLINE_STARTUP,
                                    size_px=16,
                                    color=CommonColors.WHITE,
                                ),
                                color=CommonColors.RED,
                                disabled=False,
                                className=CommonCSSClassNames.MANTINE_BUTTON,
                            ),
                        ],
                        style={"display": "flex", "gap": "20px"},
                    ),
                ],
                style={"display": "flex", "flexDirection": "column", "alignItems": "center"},
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text("Example 1 - Default Transaction Supervisor", fw=700, size="xl"),
                    dmc.Text(
                        "Uses only the required constructor arguments. The supervisor renders "
                        "with its default layout, polling the transaction method status and "
                        "displaying the result once the computation completes.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Space(h=10),
                    html.Div(id="default_ts_container"),
                ],
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text("Example 2 - Customized Transaction Supervisor", fw=700, size="xl"),
                    dmc.Text(
                        "Demonstrates custom styling and layout options: a fixed width of "
                        "600 px, larger font sizes, vertical orientation, and a custom title.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Space(h=10),
                    html.Div(id="custom_ts_container"),
                ],
            ),
        ],
        style={"maxWidth": "700px"},
    )
    return page_layout(
        page_title="Transaction Supervisor",
        info_card_text=INFO_CARD_TEXT,
        main_content=main_content,
    )


@callback(
    Output("default_ts_container", "children"),
    Output("custom_ts_container", "children"),
    Input("url", "pathname"),
)
def initialize_transaction_supervisors(
    project: SuperComponentsExamplesSolution,
) -> tuple[TransactionSupervisor, TransactionSupervisor]:
    """Initialize the transaction supervisors."""
    default_supervisor = TransactionSupervisor(
        aio_id="default_ts",
        url=project.url,
        step_name="simple_step",
        method_name="compute_sum",
    )
    custom_supervisor = TransactionSupervisor(
        aio_id="custom_ts",
        url=project.url,
        step_name="simple_step",
        method_name="compute_sum",
        title="Custom Transaction Supervisor",
        show=True,
        width=600,
        font_size="16px",
        title_font_size="20px",
        orientation="vertical",
    )
    return default_supervisor, custom_supervisor


@callback(
    Output("output_value", "children", allow_duplicate=True),
    Trigger("compute_with_success", "n_clicks"),
    Trigger("compute_with_error", "n_clicks"),
    State("input_1", "value"),
    State("input_2", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def run_compute_sum_method(
    input_1: float,
    input_2: float,
    project: SuperComponentsExamplesSolution,
) -> str:
    """Start a synchronous method and store the result."""
    if not ctx.triggered_id:
        raise PreventUpdate

    step = project.steps.simple_step
    step.input_1 = input_1
    step.input_2 = input_2
    if ctx.triggered_id == "compute_with_error":
        step.force_failure = True
    else:
        step.force_failure = False

    step.compute_sum()
    return str(step.output_1)


@callback(
    Output("output_value", "children", allow_duplicate=True),
    Input("url", "pathname"),
    Trigger(TransactionSupervisor.ids.transaction_status_badge("default_ts"), "children"),
    prevent_initial_call=True,
)
def update_output_display(project: SuperComponentsExamplesSolution) -> str:
    """Update the sum result display based on the transaction status."""
    result = project.steps.simple_step.output_1
    return str(result) if result else _OUTPUT_INITIAL


@callback(
    Output(
        TransactionSupervisor.ids.activate_monitoring("default_ts"),
        "data",
    ),
    Output(
        TransactionSupervisor.ids.activate_monitoring("custom_ts"),
        "data",
    ),
    Trigger("compute_with_success", "n_clicks"),
    Trigger("compute_with_error", "n_clicks"),
    prevent_initial_call=True,
)
def activate_monitoring() -> tuple[bool, bool]:
    """Activate monitoring with the transaction supervisors."""
    return True, True
