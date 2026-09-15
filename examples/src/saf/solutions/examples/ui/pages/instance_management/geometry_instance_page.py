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

# ©2025, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Frontend of the Geometry page."""

from typing import Any

from ansys.saf.glow.client import DashClient, callback
from ansys.saf.glow.solution import MethodState
import dash
from dash_extensions.enrich import Input, Output, State, html, no_update  # pyright: ignore[reportMissingTypeStubs]
from dash_iconify import DashIconify  # pyright: ignore[reportMissingTypeStubs]
import dash_mantine_components as dmc  # pyright: ignore[reportMissingTypeStubs]

from saf.solutions.examples.solution.definition import ExamplesSolution

dash.register_page(
    __name__,
    name="Geometry Instance Management",
    path_template="/projects/<project_id>/geometry-instance-management",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout(project: ExamplesSolution) -> html.Div:
    """Layout for the Geometry Instance Manager page."""
    step = project.steps.geometry_step

    controls_card = dmc.Card(
        [
            dmc.CardSection(
                dmc.Group(
                    children=[
                        dmc.Text("Controls", fw=500, style={"font-size": "17px"}),
                    ],
                    justify="space-between",
                ),
                withBorder=True,
                inheritPadding=True,
                py="xs",
            ),
            dmc.Space(h=20),
            dmc.Group(
                [
                    dmc.Tooltip(
                        dmc.ActionIcon(
                            DashIconify(
                                icon="streamline:startup-solid", width=30, style={"color": "var(--mantine-color-body)"}
                            ),
                            id="launch-geometry-button",
                            size="xl",
                            color="#2790F1",
                        ),
                        label="Launch Geometry",
                        position="top",
                    ),
                    dmc.Tooltip(
                        dmc.ActionIcon(
                            DashIconify(icon="mdi:shutdown", width=30, style={"color": "var(--mantine-color-body)"}),
                            id="shutdown-geometry-button",
                            size="xl",
                            color="#2790F1",
                            disabled=True,
                        ),
                        label="Shutdown Geometry",
                        position="top",
                    ),
                ],
                gap="md",
                justify="center",
            ),
            dmc.Space(h=20),
            dmc.Divider(variant="solid"),
            dmc.Space(h=20),
            dmc.Stack(
                [
                    dmc.Button(
                        "Extrude Slot",
                        id="extrude-slot-button",
                        variant="filled",
                        color="#2790F1",
                        leftSection=DashIconify(icon="mdi:design"),
                        disabled=True,
                        style={"width": "70%", "font-size": "15px", "color": "var(--mantine-color-body)"},
                    ),
                    dmc.Button(
                        "Get Active Design",
                        id="get-active-design-button",
                        variant="filled",
                        color="#2790F1",
                        leftSection=DashIconify(icon="carbon:result"),
                        disabled=True,
                        style={"width": "70%", "font-size": "15px", "color": "var(--mantine-color-body)"},
                    ),
                ],
                align="center",
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
    )

    logs_container = dmc.Card(
        [
            dmc.CardSection(
                dmc.Group(
                    children=[
                        dmc.Text("Logs", fw=500, style={"font-size": "17px"}),
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
                html.Pre(
                    id="geometry-console-logs",
                    style={
                        "whiteSpace": "pre-wrap",
                        "wordBreak": "break-all",
                        "fontSize": "14px",
                        "height": "100%",
                        "overflowY": "auto",
                        "margin": "0",
                    },
                ),
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
            html.H1(
                "Geometry Instance Manager",
                className="display-3",
                style={"font-size": "40px", "font-weight": "bold"},
            ),
            html.Hr(className="my-2"),
            dmc.Space(h=20),
            dmc.Blockquote(
                "This example demonstrates how to leverage the instance management API to control Geometry.\
                Click the Launch action button to\
                start the instance. A transaction method will start Geometry which can be used across all transaction\
                methods of the solution. Run Geometry operations with the Extrude Slot and\
                Get Active Design buttons. Close Geometry using the Shutdown button.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            dmc.Space(h=20),
            dmc.Alert(
                dmc.Text(
                    [
                        "⚠️ This example requires at least Geometry 2025 R2 Service Pack 4 (25R2 SP4) to run.",
                    ],
                    style={"whiteSpace": "pre-line"},
                    size="md",
                ),
                title="Warning",
                color="yellow",
            ),
            dmc.Space(h=20),
            dmc.Grid(
                [
                    dmc.GridCol(
                        controls_card,
                        span=3,
                    ),
                    dmc.GridCol(logs_container, span=9),
                ],
                grow=True,
                gutter="xs",
            ),
            DashClient.create_event_listener(  # pyright: ignore[reportUnknownMemberType]
                step, id="output-listener", stream_name="geometry-output-stream"
            ),
            DashClient.create_event_listener(  # pyright: ignore[reportUnknownMemberType]
                step, id="launch-geometry-listener", stream_name="launch-geometry"
            ),
            DashClient.create_event_listener(  # pyright: ignore[reportUnknownMemberType]
                step, id="extrude-slot-listener", stream_name="extrude-slot"
            ),
            DashClient.create_event_listener(  # pyright: ignore[reportUnknownMemberType]
                step, id="get-active-design-listener", stream_name="get-active-design"
            ),
            html.Br(),
            html.Br(),
        ]
    )


@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Output("launch-geometry-button", "disabled", allow_duplicate=True),
    Output("launch-geometry-button", "loading", allow_duplicate=True),
    Input("launch-geometry-button", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def start_geometry(n_clicks: int, project: ExamplesSolution) -> tuple[list[dict[str, Any]] | str, bool, bool]:
    """Initialize the Geometry instance."""
    notification = no_update
    disable_launch_button = no_update
    loading_launch_button = no_update
    if n_clicks:
        step = project.steps.geometry_step
        step.launch_geometry()

        notification = [
            dict(
                title="Info",
                id="start-geometry-notification",
                action="show",
                message="Starting Geometry instance... Please wait.",
                autoClose=False,
                loading=True,
                color="orange",
                withCloseButton=True,
            )
        ]
        disable_launch_button = True
        loading_launch_button = True

    return notification, disable_launch_button, loading_launch_button


@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Output("launch-geometry-button", "disabled"),
    Output("launch-geometry-button", "loading"),
    Output("shutdown-geometry-button", "disabled", allow_duplicate=True),
    Output("extrude-slot-button", "disabled", allow_duplicate=True),
    Input("launch-geometry-listener", "message"),
    prevent_initial_call=True,
)
def enable_geometry_extrude_slot(message: dict[str, Any]) -> tuple[list[dict[str, Any]] | str, bool, bool, bool, bool]:
    """Update the UI after Geometry is launched to enable extrude slot."""
    notification = no_update
    disable_launch_button = no_update
    loading_launch_button = no_update
    disable_shutdown_button = no_update
    disable_extrude_slot_button = no_update

    if message:
        method_state = MethodState.model_validate_json(message["data"])

        if method_state.status.value == "completed":
            loading_launch_button = False
            disable_shutdown_button = False
            disable_extrude_slot_button = False
            notification = [
                dict(
                    title="Success",
                    id="start-geometry-notification",
                    action="update",
                    message="Geometry instance launched successfully!",
                    color="green",
                    autoClose=5000,
                    withCloseButton=True,
                    loading=False,
                )
            ]
        elif method_state.status.value == "failed":
            disable_launch_button = False
            loading_launch_button = False
            notification = [
                dict(
                    title="Error",
                    id="start-geometry-notification",
                    action="update",
                    message="Geometry initialization failed. Please check the logs.",
                    color="red",
                    autoClose=5000,
                    withCloseButton=True,
                    loading=False,
                )
            ]

    return (
        notification,
        disable_launch_button,
        loading_launch_button,
        disable_shutdown_button,
        disable_extrude_slot_button,
    )


@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Output("extrude-slot-button", "disabled"),
    Output("extrude-slot-button", "loading", allow_duplicate=True),
    Output("shutdown-geometry-button", "disabled"),
    Input("extrude-slot-button", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def extrude_slot(n_clicks: int, project: ExamplesSolution) -> tuple[list[dict[str, Any]] | str, bool, bool, bool]:
    """Extrude a slot in the Geometry instance."""
    notification = no_update
    disable_extrude_slot_button = no_update
    loading_extrude_slot_button = no_update
    disable_shutdown_button = no_update

    if n_clicks:
        step = project.steps.geometry_step
        step.extrude_slot()

        notification = [
            dict(
                title="Info",
                id="extrude-slot-notification",
                action="show",
                message="Extruding slot... Check the logs for progress.",
                autoClose=False,
                loading=True,
                color="orange",
                withCloseButton=True,
            )
        ]
        disable_extrude_slot_button = True
        loading_extrude_slot_button = True
        disable_shutdown_button = True

    return notification, disable_extrude_slot_button, loading_extrude_slot_button, disable_shutdown_button


@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Output("extrude-slot-button", "disabled"),
    Output("extrude-slot-button", "loading"),
    Output("shutdown-geometry-button", "disabled"),
    Output("get-active-design-button", "disabled", allow_duplicate=True),
    Input("extrude-slot-listener", "message"),
    prevent_initial_call=True,
)
def display_extrude_slot_notification(
    message: dict[str, Any]
) -> tuple[list[dict[str, Any]] | str, bool, bool, bool, bool]:
    """Display extrude slot notification."""
    notification = no_update
    disable_extrude_slot_button = no_update
    loading_extrude_slot_button = no_update
    disable_shutdown_button = no_update
    disable_get_active_design_button = no_update
    if message:

        loading_extrude_slot_button = False
        disable_shutdown_button = False

        method_state = MethodState.model_validate_json(message["data"])
        if method_state.status.value == "completed":
            disable_get_active_design_button = False
            notification = [
                dict(
                    title="Success",
                    id="extrude-slot-notification",
                    action="update",
                    message="Slot extruded successfully!",
                    autoClose=5000,
                    loading=False,
                    color="green",
                    withCloseButton=True,
                )
            ]
        elif method_state.status.value == "failed":
            disable_extrude_slot_button = False
            notification = [
                dict(
                    title="Error",
                    id="extrude-slot-notification",
                    action="update",
                    message="Slot extrusion failed. Please check the logs.",
                    autoClose=5000,
                    loading=False,
                    color="red",
                    withCloseButton=True,
                )
            ]
    return (
        notification,
        disable_extrude_slot_button,
        loading_extrude_slot_button,
        disable_shutdown_button,
        disable_get_active_design_button,
    )


@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Output("get-active-design-button", "disabled"),
    Output("get-active-design-button", "loading", allow_duplicate=True),
    Output("shutdown-geometry-button", "disabled"),
    Input("get-active-design-button", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def get_active_design(n_clicks: int, project: ExamplesSolution) -> tuple[list[dict[str, Any]] | str, bool, bool, bool]:
    """Get the active design from the Geometry instance."""
    notification = no_update
    disable_get_active_design_button = no_update
    loading_get_active_design_button = no_update
    disable_shutdown_button = no_update

    if n_clicks:
        step = project.steps.geometry_step
        step.get_active_design()

        notification = [
            dict(
                title="Info",
                id="get-active-design-notification",
                action="show",
                message="Getting active design... Check the logs for progress.",
                autoClose=False,
                loading=True,
                color="orange",
                withCloseButton=True,
            )
        ]
        disable_get_active_design_button = True
        loading_get_active_design_button = True
        disable_shutdown_button = True

    return (
        notification,
        disable_get_active_design_button,
        loading_get_active_design_button,
        disable_shutdown_button,
    )


@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Output("get-active-design-button", "disabled"),
    Output("get-active-design-button", "loading"),
    Output("shutdown-geometry-button", "disabled"),
    Input("get-active-design-listener", "message"),
    prevent_initial_call=True,
)
def display_get_active_design_notification(
    message: dict[str, Any]
) -> tuple[list[dict[str, Any]] | str, bool, bool, bool]:
    """Display get active design notification."""
    notification = no_update
    disable_get_active_design_button = no_update
    loading_get_active_design_button = no_update
    disable_shutdown_button = no_update

    if message:

        loading_get_active_design_button = False
        disable_shutdown_button = False

        method_state = MethodState.model_validate_json(message["data"])

        if method_state.status.value == "completed":
            notification = [
                dict(
                    title="Success",
                    id="get-active-design-notification",
                    action="update",
                    message="Get active design completed successfully!",
                    autoClose=5000,
                    loading=False,
                    color="green",
                    withCloseButton=True,
                )
            ]
        elif method_state.status.value == "failed":
            disable_get_active_design_button = False
            notification = [
                dict(
                    title="Error",
                    id="get-active-design-notification",
                    action="update",
                    message="Get active design failed. Please check the logs.",
                    autoClose=5000,
                    loading=False,
                    color="red",
                    withCloseButton=True,
                )
            ]
    return (
        notification,
        disable_get_active_design_button,
        loading_get_active_design_button,
        disable_shutdown_button,
    )


@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Output("launch-geometry-button", "disabled"),
    Output("shutdown-geometry-button", "disabled"),
    Output("extrude-slot-button", "disabled"),
    Output("get-active-design-button", "disabled"),
    Input("shutdown-geometry-button", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def shutdown_geometry(
    n_clicks: int, project: ExamplesSolution
) -> tuple[list[dict[str, Any]] | str, bool, bool, bool, bool]:
    """Shutdown the geometry instance."""
    notification = no_update
    disable_launch_button = no_update
    disable_shutdown_button = no_update
    disable_extrude_slot_button = no_update
    disable_get_active_design_button = no_update

    if n_clicks:
        step = project.steps.geometry_step

        try:
            step.shutdown_geometry()
            notification = [
                dict(
                    title="Success",
                    id="shutdown-geometry-notification",
                    action="show",
                    message="Geometry instance shutdown successfully.",
                    autoClose=5000,
                    color="green",
                    withCloseButton=True,
                )
            ]
            disable_launch_button = False
            disable_shutdown_button = True
            disable_extrude_slot_button = True
            disable_get_active_design_button = True
        except Exception:
            notification = [
                dict(
                    title="Error",
                    id="shutdown-geometry-notification",
                    action="show",
                    message="Failed to shutdown geometry instance.",
                    autoClose=5000,
                    color="red",
                    withCloseButton=True,
                )
            ]

    return (
        notification,
        disable_launch_button,
        disable_shutdown_button,
        disable_extrude_slot_button,
        disable_get_active_design_button,
    )


@callback(
    Output("geometry-console-logs", "children", allow_duplicate=True),
    Input("output-listener", "message"),
    State("geometry-console-logs", "children"),
    prevent_initial_call=True,
)
def display_geometry_output(message: dict[str, Any], current_logs: str) -> str:
    """Display geometry output."""
    if message:
        new_content = message["data"].strip('"').replace("\\n", "\n")
        combined = (current_logs or "") + "\n" + new_content
        return combined
    return current_logs


@callback(
    Output("geometry-console-logs", "children"),
    Input("clear-logs-button", "n_clicks"),
    prevent_initial_call=True,
)
def clear_console_logs(n_clicks: int) -> str:
    """Clear the console logs."""
    return ""
