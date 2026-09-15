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


"""Frontend of the folder selector page."""

from pathlib import Path
from typing import Any

from ansys.saf.glow.client import callback
from ansys.solutions.dash_super_components import InputForm
from ansys.solutions.dash_super_components.folder_selector import FolderSelector, FolderSelectorMode
from dash_extensions.enrich import Input, Output, State, Trigger, html
import dash_mantine_components as dmc

from ansys.solutions.showcase_dash_super_components.solution.definition import (
    SuperComponentsExamplesSolution,
)
from ansys.solutions.showcase_dash_super_components.ui.components.page_template import (
    layout as page_layout,
)
from ansys.solutions.showcase_dash_super_components.ui.utilities.common_colors import CommonColors

INFO_CARD_TEXT = [
    (
        "Folder Selector is a component for browsing and selecting a directory. It supports "
        "two operating modes (native OS dialog via tkinter, or browser-based modal via bootstrap), "
        "customizable button appearance, and flexible value persistence."
    ),
]

_FS_MAX_WIDTH = "500px"
BOOTSTRAP_MAX_TREE_DEPTH = 10
BOOTSTRAP_MAX_CHILDREN_PER_NODE = 20

SOLUTION_BASE_PATH = Path(__file__).parent.parent.parent.parent.parent.parent.parent


def layout() -> html.Div:
    """Layout of the folder selector page."""
    mode_options_form = InputForm(
        [
            {
                "fields": [
                    {
                        "type": "Switch",
                        "id": "toggle_mode",
                        "checked": True,
                        "label": "Bootstrap mode (vs Tkinter)",
                        "size": "xs",
                        "radius": "xl",
                        "styles": {"label": {"fontSize": "12px"}},
                    },
                    {
                        "type": "Switch",
                        "id": "toggle_display_field",
                        "checked": True,
                        "label": "Show built-in path display",
                        "size": "xs",
                        "radius": "xl",
                        "styles": {"label": {"fontSize": "12px"}},
                    },
                    {
                        "type": "Switch",
                        "id": "toggle_default_path",
                        "checked": False,
                        "label": "Set default path",
                        "size": "xs",
                        "radius": "xl",
                        "styles": {"label": {"fontSize": "12px"}},
                    },
                    {
                        "type": "NumberInput",
                        "id": "max_display_lines",
                        "label": "Max display lines",
                        "description": "Lines before the path is truncated with an ellipsis.",
                        "size": "xs",
                        "radius": "xl",
                        "styles": {"label": {"fontSize": "12px"}},
                        "value": 2,
                        "min": 1,
                        "max": 5,
                    },
                ],
            },
        ],
        aio_id="mode-option-controls",
        columns=["fields"],
        with_card=False,
    )

    main_content = html.Div(
        [
            html.Div(
                [
                    dmc.Text("Example 1 - Basic Folder Selector", fw=700, size="xl"),
                    dmc.Text(
                        "Minimal usage with default settings. The component is placed directly "
                        "in the layout without a callback. The selected path is read in a "
                        "callback and shown in a styled badge below.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Space(h=10),
                    html.Div(
                        FolderSelector(aio_id="basic-fs"),
                        style={"maxWidth": _FS_MAX_WIDTH},
                    ),
                    dmc.Space(h=20),
                    html.Div(id="basic-fs-selected-display"),
                ],
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text("Example 2 - Mode and Options", fw=700, size="xl"),
                    dmc.Text(
                        "Demonstrates the two operating modes (Bootstrap and Tkinter) and the "
                        "options dictionary (display_field, default_path, max_display_lines). "
                        "Toggle the switches or adjust the number of display lines "
                        "to change behavior — the component is recreated each time.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Space(h=10),
                    html.Div(
                        [
                            mode_options_form,
                            dmc.Space(h=20),
                            html.Div(
                                id="mode-options-fs-container", style={"maxWidth": _FS_MAX_WIDTH}
                            ),
                        ],
                    ),
                ],
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text("Example 3 - Custom Styling", fw=700, size="xl"),
                    dmc.Text(
                        "Customizes the component container via style, the browse button via "
                        "browse_button_props, and the clear button via clear_button_props. No "
                        "callback is needed — the component is placed directly in the layout.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Space(h=10),
                    html.Div(
                        FolderSelector(
                            aio_id="styled-fs",
                            style={
                                "border": f"1px solid {CommonColors.MEDIUM_GREY}",
                                "borderRadius": "8px",
                                "padding": "12px",
                                "backgroundColor": (
                                    f"light-dark({CommonColors.VERY_LIGHT_GREY}, "
                                    f"{CommonColors.VERY_DARK_GREY})"
                                ),
                            },
                            browse_button_props={
                                "children": "Choose Project Folder",
                                "color": (
                                    f"light-dark({CommonColors.BLACK}, {CommonColors.DARK_GREY})"
                                ),
                                "variant": "filled",
                            },
                            clear_button_props={
                                "color": f"light-dark({CommonColors.BLACK}, {CommonColors.WHITE})",
                                "variant": "outline",
                                "size": "sm",
                            },
                        ),
                        style={"maxWidth": _FS_MAX_WIDTH},
                    ),
                ],
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text("Example 4 - Persistence", fw=700, size="xl"),
                    dmc.Text(
                        "Two selectors demonstrating how to persist the selected folder value "
                        "across component recreations and page reloads. "
                        "Click the button to simulate "
                        "recreation and observe how the selectors behave. Also switch to "
                        "another page and back or load a different project to see how the "
                        "backend persistence strategy behaves.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="xs",
                    ),
                    dmc.List(
                        [
                            dmc.ListItem(
                                dmc.Text(
                                    [
                                        dmc.Text("No persistence", fw=600, span=True),
                                        ": resets the selection every time the folder selector "
                                        "is recreated or the page is reloaded.",
                                    ],
                                    size="sm",
                                    c=CommonColors.MANTINE_DIMMED,
                                )
                            ),
                            dmc.ListItem(
                                dmc.Text(
                                    [
                                        dmc.Text("Backend", fw=600, span=True),
                                        ": keeps the selected folder consistently when the folder "
                                        "selector is recreated, the page is reloaded, and even "
                                        "when a different project is loaded within the same "
                                        "solution UI.",
                                    ],
                                    size="sm",
                                    c=CommonColors.MANTINE_DIMMED,
                                )
                            ),
                        ],
                        size="sm",
                        mb="sm",
                        type="ordered",
                    ),
                    dmc.Space(h=10),
                    dmc.Button("Reload Components", id="persistence-reload-btn"),
                    dmc.Space(h=16),
                    dmc.Stack(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        "(1) No persistence — resets on recreation and reload:",
                                        style={"fontWeight": "bold", "marginBottom": "8px"},
                                    ),
                                    html.Div(
                                        id="persistence-fs-container-1",
                                        style={"maxWidth": _FS_MAX_WIDTH},
                                    ),
                                ],
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        "(2) Backend — restored from server per project:",
                                        style={"fontWeight": "bold", "marginBottom": "8px"},
                                    ),
                                    html.Div(
                                        id="persistence-fs-container-2",
                                        style={"maxWidth": _FS_MAX_WIDTH},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dmc.Space(h=10),
                    html.Div(id="persistence-selected-display"),
                ],
            ),
        ],
        style={"maxWidth": "900px"},
    )
    return page_layout(
        page_title="Folder Selector",
        info_card_text=INFO_CARD_TEXT,
        main_content=main_content,
    )


@callback(
    Output("basic-fs-selected-display", "children"),
    Input(FolderSelector.ids.selected_folder("basic-fs"), "data"),
    prevent_initial_call=True,
)
def update_basic_selected_folder(selected_folder: str | None) -> dmc.Badge | str:
    """Display the selected path in a styled badge."""
    if not selected_folder:
        return ""
    return dmc.Badge(
        f"Selected: {selected_folder}",
        variant="light",
        size="lg",
        style={"maxWidth": "100%", "overflow": "hidden", "textOverflow": "ellipsis"},
    )


@callback(
    Output("mode-options-fs-container", "children"),
    Trigger("url", "pathname"),
)
def initialize_mode_options_fs() -> html.Div:
    """Create the mode/options folder selector on initial page load."""
    return html.Div(
        FolderSelector(
            aio_id="mode-options-fs",
            mode=FolderSelectorMode.BOOTSTRAP,
            options={
                "display_field": {"enabled": True, "max_display_lines": 2},
                "browse_from": str(SOLUTION_BASE_PATH),
                "max_tree_depth": BOOTSTRAP_MAX_TREE_DEPTH,
                "max_children_per_node": BOOTSTRAP_MAX_CHILDREN_PER_NODE,
            },
        ),
        style={"maxWidth": _FS_MAX_WIDTH},
    )


@callback(
    Output("mode-options-fs-container", "children"),
    Input(
        InputForm.ids.field("mode-option-controls", "Switch", "toggle_mode", 0),
        "checked",
    ),
    Input(
        InputForm.ids.field("mode-option-controls", "Switch", "toggle_display_field", 0),
        "checked",
    ),
    Input(
        InputForm.ids.field("mode-option-controls", "Switch", "toggle_default_path", 0),
        "checked",
    ),
    Input(
        InputForm.ids.field("mode-option-controls", "NumberInput", "max_display_lines", 0),
        "value",
    ),
    prevent_initial_call=True,
)
def update_mode_options_fs(
    bootstrap_mode: bool,
    show_display_field: bool,
    set_default_path: bool,
    max_display_lines: int,
) -> html.Div:
    """Recreate the folder selector when a mode/options switch or number input changes."""
    mode = FolderSelectorMode.BOOTSTRAP if bootstrap_mode else FolderSelectorMode.TKINTER
    options: dict[str, Any] = {
        "display_field": {
            "enabled": show_display_field,
            "max_display_lines": max_display_lines if max_display_lines else 2,
        },
    }
    if set_default_path:
        options["default_path"] = str(SOLUTION_BASE_PATH)
    if mode == FolderSelectorMode.BOOTSTRAP:
        options["browse_from"] = str(SOLUTION_BASE_PATH)
        options["max_tree_depth"] = BOOTSTRAP_MAX_TREE_DEPTH
        options["max_children_per_node"] = BOOTSTRAP_MAX_CHILDREN_PER_NODE
    return html.Div(
        FolderSelector(
            aio_id="mode-options-fs",
            mode=mode,
            options=options,
        ),
        style={"maxWidth": _FS_MAX_WIDTH},
    )


@callback(
    Output("persistence-fs-container-1", "children"),
    Output("persistence-fs-container-2", "children"),
    Input("url", "pathname"),
)
def initialize_persistence_selectors(
    project: SuperComponentsExamplesSolution,
) -> tuple[FolderSelector, FolderSelector]:
    """Create the two persistence selectors on page load."""
    backend_value = project.steps.simple_step.selected_folder
    return (
        FolderSelector(aio_id="persistence-fs-1"),  # no persistence
        FolderSelector(aio_id="persistence-fs-2", value=backend_value),  # backend
    )


@callback(
    Output("persistence-fs-container-1", "children"),
    Output("persistence-fs-container-2", "children"),
    Trigger("persistence-reload-btn", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def reload_persistence_selectors(
    project: SuperComponentsExamplesSolution,
) -> tuple[FolderSelector, FolderSelector]:
    """Recreate the selectors; each retains its value per its persistence strategy."""
    backend_value = project.steps.simple_step.selected_folder
    return (
        FolderSelector(aio_id="persistence-fs-1"),  # no persistence
        FolderSelector(aio_id="persistence-fs-2", value=backend_value),  # backend
    )


@callback(
    Output("persistence-selected-display", "children"),
    Input(FolderSelector.ids.selected_folder("persistence-fs-1"), "data"),
    Input(FolderSelector.ids.selected_folder("persistence-fs-2"), "data"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def update_persistence_display_and_backend(
    folder_1: str | None,
    folder_2: str | None,
    project: SuperComponentsExamplesSolution,
) -> dmc.Paper:
    """Show all selected paths and persist the second one to the backend."""
    project.steps.simple_step.selected_folder = folder_2

    def _path_badge(label: str, path: str | None) -> html.Div:
        value = path if path else "—"
        return html.Div(
            [
                dmc.Text(
                    label,
                    size="xs",
                    fw=600,
                    c=CommonColors.MANTINE_DIMMED,
                    style={"minWidth": "180px"},
                ),
                dmc.Badge(
                    value,
                    variant="light",
                    size="md",
                    style={"overflow": "hidden", "textOverflow": "ellipsis", "maxWidth": "600px"},
                ),
            ],
            style={"display": "flex", "alignItems": "center", "gap": "8px"},
        )

    return dmc.Paper(
        [
            dmc.Text("Currently selected folders:", size="sm", fw=700, mb="xs"),
            _path_badge("(1) No persistence", folder_1),
            _path_badge("(2) Backend", folder_2),
        ],
        withBorder=True,
        shadow="xs",
        radius="md",
        p="md",
        style={"maxWidth": "900px", "display": "flex", "flexDirection": "column", "gap": "8px"},
    )
