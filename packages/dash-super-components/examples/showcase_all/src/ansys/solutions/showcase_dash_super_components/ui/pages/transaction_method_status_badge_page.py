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


"""Transaction method status badge page."""

from ansys.saf.glow.client import DashClient, callback
from ansys.saf.glow.solution import MethodStatus
from ansys.solutions.dash_super_components import TransactionMethodStatusBadge
from ansys.solutions.dash_super_components.utils.svg_icons import (
    IconNames,
    create_icon_span,
)
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import MATCH, Input, Output, State, Trigger, ctx, html
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
    (
        "Transaction Method Status Badge monitors the real-time execution status of a "
        "long-running transaction method."
    ),
    (
        "The badge can be configured to start and stop monitoring automatically when the "
        "transaction starts and terminates, or the monitoring can be controlled independently "
        "from the rest of the application."
    ),
]


def _run_transaction_button(button_id: dict | str, label: str, running: bool) -> dmc.Button:
    """Return a styled 'Run Transaction' button."""
    return dmc.Button(
        label,
        id=button_id,
        leftSection=create_icon_span(
            IconNames.STREAMLINE_STARTUP, size_px=16, color=CommonColors.WHITE
        ),
        radius="xs",
        loading=running,
        className=CommonCSSClassNames.MANTINE_BUTTON,
    )


def layout(step: SimpleStep) -> html.Div:
    """Layout of the transaction method status badge page."""
    main_content = html.Div(
        [
            # ── Example 1 ────────────────────────────────────────────────────────────
            html.Div(
                [
                    dmc.Text("Example 1 - Default Badge", fw=700, size="xl"),
                    dmc.Text(
                        "Uses only the required constructor arguments with all defaults. "
                        "Monitoring starts automatically when the transaction is triggered "
                        "and stops as soon as it terminates.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Grid(
                        [
                            dmc.GridCol(
                                _run_transaction_button(
                                    button_id={"type": "run-btn", "index": 1},
                                    label="Run Transaction 1",
                                    running=method_in_progress(step, "long_running_1"),
                                ),
                                span="content",
                                style={"display": "flex", "alignItems": "center"},
                            ),
                            dmc.GridCol(
                                html.Div(id="tmsb-container-1", style={"width": "200px"}),
                                span="auto",
                            ),
                        ],
                        gutter="xl",
                        align="center",
                    ),
                    DashClient.create_event_listener(
                        step,
                        stream_name="long-running-1",
                        id={"type": "ws-long-running", "index": 1},  # type: ignore[arg-type]
                    ),
                ],
                style={"maxWidth": "700px"},
            ),
            dmc.Space(h=60),
            # ── Example 2 ────────────────────────────────────────────────────────────
            html.Div(
                [
                    dmc.Text("Example 2 - Customized Badge", fw=700, size="xl"),
                    dmc.Text(
                        "Demonstrates a custom label and size and a faster polling interval of "
                        "1 s. "
                        "Like example 1, monitoring still starts and stops automatically with "
                        "the transaction.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Grid(
                        [
                            dmc.GridCol(
                                _run_transaction_button(
                                    button_id={"type": "run-btn", "index": 2},
                                    label="Run Transaction 2",
                                    running=method_in_progress(step, "long_running_2"),
                                ),
                                span="content",
                                style={"display": "flex", "alignItems": "center"},
                            ),
                            dmc.GridCol(
                                html.Div(id="tmsb-container-2", style={"width": "200px"}),
                                span="auto",
                            ),
                        ],
                        gutter="xl",
                        align="center",
                    ),
                    DashClient.create_event_listener(
                        step,
                        stream_name="long-running-2",
                        id={"type": "ws-long-running", "index": 2},  # type: ignore[arg-type]
                    ),
                ],
                style={"maxWidth": "700px"},
            ),
            dmc.Space(h=60),
            # ── Example 3 ────────────────────────────────────────────────────────────
            html.Div(
                [
                    dmc.Text("Example 3 - Live Updates Toggle", fw=700, size="xl"),
                    dmc.Text(
                        "Monitoring is decoupled from the transaction trigger. "
                        "Use the 'Live Updates' switch to start or stop watching the method "
                        "status at any time, independently of whether the transaction is running.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Grid(
                        [
                            dmc.GridCol(
                                dmc.Stack(
                                    [
                                        _run_transaction_button(
                                            button_id={"type": "run-btn", "index": 3},
                                            label="Run Transaction 3",
                                            running=method_in_progress(step, "long_running_3"),
                                        ),
                                        dmc.Switch(
                                            id="live-updates-switch",
                                            label="Live Updates",
                                            checked=False,
                                            persistence=True,
                                        ),
                                    ],
                                    gap="xs",
                                    align="flex-start",
                                ),
                                span="content",
                                style={"display": "flex", "alignItems": "center"},
                            ),
                            dmc.GridCol(
                                html.Div(id="tmsb-container-3", style={"width": "200px"}),
                                span="auto",
                            ),
                        ],
                        gutter="xl",
                        align="center",
                    ),
                    DashClient.create_event_listener(
                        step,
                        stream_name="long-running-3",
                        id={"type": "ws-long-running", "index": 3},  # type: ignore[arg-type]
                    ),
                ],
                style={"maxWidth": "700px"},
            ),
        ],
    )
    return page_layout(
        page_title="Transaction Method Status Badge",
        info_card_text=INFO_CARD_TEXT,
        main_content=main_content,
    )


@callback(
    Output("tmsb-container-1", "children"),
    Output("tmsb-container-2", "children"),
    Output("tmsb-container-3", "children"),
    Input("url", "pathname"),
)
def initialize_badges(
    project: SuperComponentsExamplesSolution,
) -> tuple[
    TransactionMethodStatusBadge, TransactionMethodStatusBadge, TransactionMethodStatusBadge
]:
    """Initialize the transaction method status badges."""
    return (
        TransactionMethodStatusBadge(
            project.url,
            "simple_step",
            "long_running_1",
            aio_id="tmsb-1",
        ),
        TransactionMethodStatusBadge(
            project.url,
            "simple_step",
            "long_running_2",
            aio_id="tmsb-2",
            label_props={
                "children": "Status (polling every 1 s)",
                "style": {"fontSize": "14px", "fontWeight": 500},
            },
            badge_props={
                "size": "md",
            },
            interval_props={"interval": 1000},
        ),
        TransactionMethodStatusBadge(
            project.url,
            "simple_step",
            "long_running_3",
            aio_id="tmsb-3",
            label_props={
                "children": "Status (live updates)",
            },
            auto_mode=False,
        ),
    )


@callback(
    Output(TransactionMethodStatusBadge.ids.activate_monitoring("tmsb-1"), "data"),
    Input({"type": "run-btn", "index": 1}, "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def run_transaction_1(
    n_clicks: int,
    project: SuperComponentsExamplesSolution,
) -> bool:
    """Trigger long_running_1 and activate badge 1 monitoring."""
    if not ctx.triggered_id or not n_clicks:
        raise PreventUpdate
    step = project.steps.simple_step
    step.long_running_1()
    return True


@callback(
    Output(TransactionMethodStatusBadge.ids.activate_monitoring("tmsb-2"), "data"),
    Input({"type": "run-btn", "index": 2}, "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def run_transaction_2(
    n_clicks: int,
    project: SuperComponentsExamplesSolution,
) -> bool:
    """Trigger long_running_2 and activate badge 2 monitoring."""
    if not ctx.triggered_id or not n_clicks:
        raise PreventUpdate
    step = project.steps.simple_step
    step.long_running_2()
    return True


@callback(
    Input({"type": "run-btn", "index": 3}, "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def run_transaction_3(
    n_clicks: int,
    project: SuperComponentsExamplesSolution,
) -> None:
    """Trigger long_running_3 without activating badge 3 monitoring."""
    if not ctx.triggered_id or not n_clicks:
        raise PreventUpdate
    step = project.steps.simple_step
    step.long_running_3()


@callback(
    Output(TransactionMethodStatusBadge.ids.activate_monitoring("tmsb-3"), "data"),
    Input("live-updates-switch", "checked"),
)
def toggle_live_updates(checked: bool) -> bool:
    """Activate or deactivate badge 3 monitoring based on the live updates switch."""
    return checked


@callback(
    Output({"type": "run-btn", "index": MATCH}, "loading", allow_duplicate=True),
    Input({"type": "run-btn", "index": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def disable_button_on_click(n_clicks: int) -> bool:
    """Immediately disable the clicked button."""
    if not ctx.triggered_id or not n_clicks:
        raise PreventUpdate
    return True


@callback(
    Output({"type": "run-btn", "index": MATCH}, "loading", allow_duplicate=True),
    Trigger({"type": "ws-long-running", "index": MATCH}, "message"),
    prevent_initial_call=True,
)
def enable_button_on_termination() -> bool:
    """Immediately enable the button when the corresponding transaction completes."""
    return False


def method_in_progress(step: SimpleStep, method_name: str) -> bool:
    """Check if the method is currently running."""
    return step.get_long_running_method_state(method_name).status == MethodStatus.Running
