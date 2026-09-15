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


"""Frontend of the tree page."""

import contextlib
import json
from typing import Any

from ansys.saf.glow.client import callback
from ansys.solutions.dash_super_components import Tree
from ansys.solutions.dash_super_components.utils.svg_icons import IconNames, create_base64_svg_src
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ALL, Input, Output, State, html
import dash_mantine_components as dmc

from ansys.solutions.showcase_dash_super_components.solution.definition import (
    SuperComponentsExamplesSolution,
)
from ansys.solutions.showcase_dash_super_components.ui.components.page_template import (
    layout as page_layout,
)
from ansys.solutions.showcase_dash_super_components.ui.utilities.common_colors import CommonColors

INFO_CARD_TEXT = [
    ("Tree is a component that displays hierarchical data in a collapsible tree structure. "),
    (
        "💡 Note: The page navigation bar on the left side of this application is itself "
        "a Tree component — the same component demonstrated here!"
    ),
]

# ---------------------------------------------------------------------------
# Tree 1 – Minimal: only required item properties (id + text)
# ---------------------------------------------------------------------------
_MINIMAL_ITEMS: list[dict[str, Any]] = [
    {"id": "min_a", "text": "Alpha"},
    {
        "id": "min_b",
        "text": "Beta",
        "children": [
            {"id": "min_b1", "text": "Beta-1"},
            {"id": "min_b2", "text": "Beta-2"},
        ],
    },
    {"id": "min_c", "text": "Gamma"},
]

# ---------------------------------------------------------------------------
# Tree 2 – Full-featured with online Iconify icons
# ---------------------------------------------------------------------------
_FULL_ITEMS: list[dict[str, Any]] = [
    {
        "id": "setup_step",
        "text": "Setup",
        "icon": "material-symbols:home",
        "expanded": True,
        "disabled": False,
        "description": "Project setup",
        "children": [
            {
                "id": "data_sources_step",
                "text": "Data Sources",
                "icon": "material-symbols:database",
                "expanded": True,
                "disabled": False,
                "description": "Configure data sources",
                "children": [
                    {
                        "id": "primary_database_step",
                        "text": "Primary Database",
                        "icon": "material-symbols:database",
                        "expanded": False,
                        "disabled": False,
                        "description": "Primary data connection",
                    },
                    {
                        "id": "secondary_database_step",
                        "text": "Secondary Database",
                        "icon": "material-symbols:database",
                        "expanded": False,
                        "disabled": True,
                        "description": "Secondary data connection (disabled)",
                    },
                ],
            },
            {
                "id": "parameters_step",
                "text": "Parameters",
                "icon": "material-symbols:list",
                "expanded": False,
                "disabled": False,
                "description": "Simulation parameters",
            },
        ],
    },
    {
        "id": "execution_step",
        "text": "Execution",
        "icon": "mdi:rocket",
        "expanded": False,
        "disabled": False,
        "description": "Run simulation",
        "children": [
            {
                "id": "pre_processing_step",
                "text": "Pre-processing",
                "icon": "teenyicons:doc-solid",
                "expanded": False,
                "disabled": False,
                "description": "Prepare inputs",
            },
            {
                "id": "solver_step",
                "text": "Solver",
                "icon": "mdi:rocket",
                "expanded": False,
                "disabled": False,
                "description": "Run the solver",
            },
            {
                "id": "post_processing_step",
                "text": "Post-processing",
                "icon": "teenyicons:doc-solid",
                "expanded": False,
                "disabled": False,
                "description": "Process results",
            },
        ],
    },
    {
        "id": "review_step",
        "text": "Review",
        "icon": "material-symbols:warning",
        "expanded": False,
        "disabled": False,
        "description": "Review results",
    },
    {
        "id": "help_step",
        "text": "Help",
        "icon": "material-symbols:help",
        "expanded": False,
        "disabled": False,
        "description": "Documentation and support",
    },
]

# ---------------------------------------------------------------------------
# Tree 3 – Offline base64 icons + item-level styles
# ---------------------------------------------------------------------------
_STYLED_ITEMS: list[dict[str, Any]] = [
    {
        "id": "critical_item",
        "text": "Critical Issues",
        "icon": create_base64_svg_src(IconNames.MATERIAL_WARNING),
        "icon_color": f"light-dark({CommonColors.RED}, {CommonColors.LIGHT_RED})",
        "expanded": True,
        "description": "Requires immediate attention",
        "styles": {
            "label": {"color": f"light-dark({CommonColors.RED}, {CommonColors.LIGHT_RED})"},
        },
        "children": [
            {
                "id": "critical_child_1",
                "text": "Memory Leak",
                "icon": create_base64_svg_src(IconNames.MATERIAL_WARNING),
                "icon_color": f"light-dark({CommonColors.ORANGE}, {CommonColors.LIGHT_ORANGE})",
                "description": "High severity",
                "styles": {
                    "label": {
                        "color": f"light-dark({CommonColors.ORANGE}, {CommonColors.LIGHT_ORANGE})"
                    },
                },
            },
            {
                "id": "critical_child_2",
                "text": "Null Pointer",
                "icon": create_base64_svg_src(IconNames.MATERIAL_WARNING),
                "icon_color": f"light-dark({CommonColors.ORANGE}, {CommonColors.LIGHT_ORANGE})",
                "description": "High severity",
                "styles": {
                    "label": {
                        "color": f"light-dark({CommonColors.ORANGE}, {CommonColors.LIGHT_ORANGE})"
                    },
                },
            },
        ],
    },
    {
        "id": "warning_item",
        "text": "Warnings",
        "icon": create_base64_svg_src(IconNames.MATERIAL_HELP),
        "icon_color": f"light-dark({CommonColors.YELLOW}, {CommonColors.VERY_LIGHT_YELLOW})",
        "expanded": False,
        "description": "Non-critical notices",
        "styles": {
            "label": {
                "color": f"light-dark({CommonColors.YELLOW}, {CommonColors.VERY_LIGHT_YELLOW})"
            },
        },
        "children": [
            {
                "id": "warning_child_1",
                "text": "Deprecated API",
                "icon": create_base64_svg_src(IconNames.TEENYICONS_DOC_SOLID),
                "description": "Will be removed in next version",
                "styles": {},
            },
        ],
    },
    {
        "id": "ok_item",
        "text": "Passing Checks",
        "icon": create_base64_svg_src(IconNames.MATERIAL_HOME),
        "icon_color": f"light-dark({CommonColors.GREEN}, {CommonColors.VERY_LIGHT_GREEN})",
        "expanded": False,
        "description": "All good",
        "styles": {
            "label": {
                "color": f"light-dark({CommonColors.GREEN}, {CommonColors.VERY_LIGHT_GREEN})"
            },
        },
    },
    {
        "id": "disabled_item",
        "text": "Skipped (disabled)",
        "icon": create_base64_svg_src(IconNames.MATERIAL_WARNING),
        "disabled": True,
        "description": "This check was skipped",
    },
]

# ---------------------------------------------------------------------------
# Tree 4 – Explicit icon_type overrides + no-icon items
# ---------------------------------------------------------------------------
_ICON_TYPE_OVERRIDE_ITEMS: list[dict[str, Any]] = [
    {
        "id": "forced_local_base64",
        "text": "Forced local mode",
        "icon": create_base64_svg_src(IconNames.MATERIAL_WARNING),
        "icon_type": "local",
        "description": "Rendered via CSS mask + currentColor",
    },
    {
        "id": "forced_iconify_name",
        "text": "Forced iconify mode",
        "icon": "material-symbols:warning",
        "icon_type": "iconify",
        "description": "Rendered via DashIconify",
    },
    {
        "id": "no_icon_item",
        "text": "No icon rendered",
        "description": "No icon and no default_icon",
    },
]

# ---------------------------------------------------------------------------
# Tree 5 – Workflow with disable/enable via callbacks
# ---------------------------------------------------------------------------
# Ordered list of step IDs — used by callbacks to compute ranges.
_WORKFLOW_STEP_ORDER: list[str] = [
    "wf_import",
    "wf_preprocess",
    "wf_config",
    "wf_solve",
    "wf_postprocess",
]

_WORKFLOW_ITEMS: list[dict[str, Any]] = [
    {
        "id": "wf_import",
        "text": "1. Data Import",
        "icon": create_base64_svg_src(IconNames.MATERIAL_DATABASE),
        "disabled": False,
        "description": "Load input data",
    },
    {
        "id": "wf_preprocess",
        "text": "2. Pre-processing",
        "icon": create_base64_svg_src(IconNames.TEENYICONS_DOC_SOLID),
        "disabled": False,
        "description": "Prepare data for the solver",
    },
    {
        "id": "wf_config",
        "text": "3. Solver Config",
        "icon": create_base64_svg_src(IconNames.MATERIAL_LIST),
        "disabled": False,
        "description": "Configure solver settings",
    },
    {
        "id": "wf_solve",
        "text": "4. Run Solver",
        "icon": create_base64_svg_src(IconNames.MDI_ROCKET),
        "disabled": False,
        "description": "Execute the simulation",
    },
    {
        "id": "wf_postprocess",
        "text": "5. Post-processing",
        "icon": create_base64_svg_src(IconNames.TEENYICONS_DOC_SOLID),
        "disabled": False,
        "description": "Analyze results",
    },
]


def _detail_card(selected_item_id: str, selected_index_id: str) -> dmc.Card:
    """Return a styled detail card for displaying the selected tree item."""
    return dmc.Card(
        withBorder=True,
        radius="md",
        style={
            "width": "320px",
            "backgroundColor": f"light-dark({CommonColors.VERY_LIGHT_GREY}, "
            f"{CommonColors.DARK_GREY})",
        },
        children=[
            dmc.Text("Selected Item", fw=600, mb="xs"),
            dmc.Text(
                "Index: No item selected",
                id=selected_index_id,
                size="sm",
                c=f"light-dark({CommonColors.MEDIUM_GREY}, {CommonColors.LIGHT_GREY})",
                mb="xs",
            ),
            dmc.Code(
                id=selected_item_id,
                children="No item selected.",
                block=True,
                color=f"light-dark({CommonColors.VERY_LIGHT_GREY}, {CommonColors.DARK_GREY})",
            ),
        ],
    )


def _tree_section(
    title: str,
    description: str,
    tree_component: Tree,
    selected_item_id: str,
    selected_index_id: str,
    section_footer: Any | None = None,
) -> html.Div:
    """Return a titled section containing a tree and its detail card side-by-side."""
    return html.Div(
        children=[
            dmc.Text(title, fw=700, size="xl"),
            dmc.Text(description, size="sm", c=CommonColors.MANTINE_DIMMED, mb="sm"),
            dmc.Grid(
                gutter="xl",
                align="flex-start",
                children=[
                    dmc.GridCol(
                        span="content",
                        children=[
                            html.Div(
                                style={"width": "280px"},
                                children=[tree_component],
                            ),
                        ],
                    ),
                    dmc.GridCol(
                        span="content",
                        children=[_detail_card(selected_item_id, selected_index_id)],
                    ),
                ],
            ),
            (
                html.Div(
                    style={"width": "280px"},
                    children=[section_footer],
                )
                if section_footer is not None
                else html.Div()
            ),
        ],
    )


def _disable_enable_scenario(
    title: str,
    description: str,
    disable_btn_id: str,
    disable_btn_label: str,
    enable_btn_id: str,
    enable_btn_label: str,
) -> html.Div:
    """Build one disable/enable scenario block (title, description, two buttons)."""
    return html.Div(
        children=[
            dmc.Text(title, fw=500, size="sm", mb=4),
            dmc.Text(description, size="xs", c=CommonColors.MANTINE_DIMMED, mb=6),
            dmc.Group(
                gap="xs",
                children=[
                    dmc.Button(
                        disable_btn_label,
                        id=disable_btn_id,
                        color=CommonColors.RED,
                        variant="filled",
                        size="xs",
                    ),
                    dmc.Button(
                        enable_btn_label,
                        id=enable_btn_id,
                        color=CommonColors.GREEN,
                        variant="filled",
                        size="xs",
                    ),
                ],
            ),
        ],
    )


def _workflow_controls_card() -> dmc.Card:
    """Build the disable/enable controls card for Example 5."""
    return dmc.Card(
        withBorder=True,
        radius="md",
        style={"width": "320px"},
        children=[
            dmc.Text("Disable / Enable Controls", fw=600, mb="md"),
            dmc.Stack(
                gap="md",
                children=[
                    _disable_enable_scenario(
                        title="A - Single node",
                        description="Disable or re-enable Step 5.",
                        disable_btn_id="wf_disable_step5_btn",
                        disable_btn_label="Disable Step 5",
                        enable_btn_id="wf_enable_step5_btn",
                        enable_btn_label="Enable Step 5",
                    ),
                    dmc.Divider(),
                    _disable_enable_scenario(
                        title="B - Downstream range",
                        description="Disable or re-enable Steps 3-5.",
                        disable_btn_id="wf_lock_from_step3_btn",
                        disable_btn_label="Disable Steps 3-5",
                        enable_btn_id="wf_unlock_from_step3_btn",
                        enable_btn_label="Enable Steps 3-5",
                    ),
                    dmc.Divider(),
                    _disable_enable_scenario(
                        title="C - Entire tree",
                        description="Disable all nodes during a job.",
                        disable_btn_id="wf_lock_all_btn",
                        disable_btn_label="Disable All",
                        enable_btn_id="wf_unlock_all_btn",
                        enable_btn_label="Enable All",
                    ),
                ],
            ),
        ],
    )


def _workflow_section() -> html.Div:
    """Build Example 5 - workflow tree with disable/enable controls."""
    return html.Div(
        children=[
            dmc.Text(
                "Example 5 - Workflow Tree (Disable / Enable via Callbacks)",
                fw=700,
                size="xl",
            ),
            dmc.Text(
                (
                    "Often, workflow steps start disabled and unlock as the user progresses. "
                    "The three scenarios below show how to disable a single node, "
                    "a downstream range of nodes, and the entire tree."
                ),
                size="sm",
                c=CommonColors.MANTINE_DIMMED,
                mb="sm",
            ),
            dmc.Grid(
                gutter="xl",
                align="flex-start",
                children=[
                    dmc.GridCol(
                        span="content",
                        children=[
                            html.Div(
                                style={"width": "280px"},
                                children=[
                                    Tree(
                                        aio_id="workflow_tree",
                                        items=_WORKFLOW_ITEMS,
                                        selected_item="wf_import",
                                    )
                                ],
                            ),
                        ],
                    ),
                    dmc.GridCol(
                        span="content",
                        children=[
                            dmc.Stack(
                                gap="lg",
                                children=[
                                    _detail_card(
                                        "workflow_selected_item",
                                        "workflow_selected_index",
                                    ),
                                    _workflow_controls_card(),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def main_content(step) -> html.Div:
    """Return the main content of the tree page."""
    main_content = html.Div(
        children=[
            _tree_section(
                title="Example 1 - Minimal Tree",
                description=(
                    "Only the required item properties are used: id and text. "
                    "No icons, descriptions, preselected item, or expanded state."
                ),
                tree_component=Tree(
                    aio_id="minimal_tree",
                    items=_MINIMAL_ITEMS,
                ),
                selected_item_id="minimal_selected_item",
                selected_index_id="minimal_selected_index",
            ),
            dmc.Space(h=60),
            _tree_section(
                title="Example 2 - Full-Featured Tree (Online Icons, requires internet)",
                description=(
                    "Uses online Iconify icons, "
                    "descriptions, mixed expanded/collapsed state, a disabled item "
                    "and a preselected item. "
                    "The selected item is stored on the backend and restored on page reload. "
                    "⚠️ Requires an internet connection. "
                    "Click the button below to jump to the Execution step."
                ),
                tree_component=Tree(
                    aio_id="full_tree",
                    items=_FULL_ITEMS,
                    selected_item=step.selected_tree_item or "setup_step",
                ),
                selected_item_id="full_selected_item",
                selected_index_id="full_selected_index",
                section_footer=dmc.Button(
                    "Proceed to Execution",
                    id="full_proceed_to_next_step_btn",
                    size="xs",
                    variant="filled",
                    color=CommonColors.MANTINE_PRIMARY_COLOR,
                    mt="sm",
                ),
            ),
            dmc.Space(h=60),
            _tree_section(
                title="Example 3 - Styled Tree (Offline Base64 Icons)",
                description=(
                    "Uses offline-compatible base64 icons and a custom default_icon. "
                    "Item-level styles are used to color node labels. "
                    "Icons are colored to match the label color via currentColor. "
                    "Items which do not specify an icon will use the default_icon which is "
                    "automatically theme-aware. "
                    "Works without internet access."
                ),
                tree_component=Tree(
                    aio_id="styled_tree",
                    items=_STYLED_ITEMS,
                    selected_item="critical_item",
                    default_icon=create_base64_svg_src(IconNames.MATERIAL_WARNING),
                ),
                selected_item_id="styled_selected_item",
                selected_index_id="styled_selected_index",
            ),
            dmc.Space(h=60),
            _tree_section(
                title="Example 4 - Explicit icon_type Overrides + No-Icon Items",
                description=(
                    "Demonstrates explicit icon_type usage, plus an item which gets rendered "
                    "without an icon. "
                ),
                tree_component=Tree(
                    aio_id="icon_type_tree",
                    items=_ICON_TYPE_OVERRIDE_ITEMS,
                    selected_item="forced_local_base64",
                ),
                selected_item_id="icon_type_selected_item",
                selected_index_id="icon_type_selected_index",
            ),
            dmc.Space(h=60),
            _workflow_section(),
        ],
        style={"maxWidth": "670px"},
    )

    return main_content


def layout(step) -> html.Div:
    """Layout of the tree page."""
    return page_layout(
        page_title="Tree",
        info_card_text=INFO_CARD_TEXT,
        main_content=main_content(step),
    )


def _make_outputs(selected_item: dict[str, Any]) -> tuple[str, str]:
    """Produce formatted JSON and index label from a selected item dict."""
    if not selected_item:
        return "No item selected.", "Index: No item selected"
    return (
        json.dumps(selected_item, indent=2),
        f"Index: {selected_item.get('index', 'Unknown')}",
    )


@callback(
    Input(Tree.ids.selected_item("minimal_tree"), "data"),
    Output("minimal_selected_item", "children"),
    Output("minimal_selected_index", "children"),
)
def show_minimal_selected(selected_item: dict[str, Any]) -> tuple[str, str]:
    """Show selected item for the minimal tree."""
    return _make_outputs(selected_item)


@callback(
    Input(Tree.ids.selected_item("full_tree"), "data"),
    Input("url", "pathname"),
    Output("full_selected_item", "children"),
    Output("full_selected_index", "children"),
)
def show_full_selected(
    selected_item: dict[str, Any], project: SuperComponentsExamplesSolution
) -> tuple[str, str]:
    """Show selected item for the full-featured tree."""
    selected_index = None
    with contextlib.suppress(Exception):
        selected_index = Tree.ids.get_index_from_navlink_item_id(selected_item)
    project.steps.simple_step.selected_tree_item = selected_index
    return _make_outputs(selected_item)


@callback(
    Input(Tree.ids.selected_item("styled_tree"), "data"),
    Output("styled_selected_item", "children"),
    Output("styled_selected_index", "children"),
)
def show_styled_selected(selected_item: dict[str, Any]) -> tuple[str, str]:
    """Show selected item for the styled tree."""
    return _make_outputs(selected_item)


@callback(
    Input(Tree.ids.selected_item("icon_type_tree"), "data"),
    Output("icon_type_selected_item", "children"),
    Output("icon_type_selected_index", "children"),
)
def show_icon_type_selected(selected_item: dict[str, Any]) -> tuple[str, str]:
    """Show selected item for the icon_type override tree."""
    return _make_outputs(selected_item)


@callback(
    Input(Tree.ids.selected_item("workflow_tree"), "data"),
    Output("workflow_selected_item", "children"),
    Output("workflow_selected_index", "children"),
)
def show_workflow_selected(selected_item: dict[str, Any]) -> tuple[str, str]:
    """Show selected item for the workflow tree."""
    return _make_outputs(selected_item)


# ----------------------------------------------------------------------------
# Example 2 callbacks – Jump to next step
# ----------------------------------------------------------------------------


@callback(
    Output(Tree.ids.selected_item("full_tree"), "data", allow_duplicate=True),
    Input("full_proceed_to_next_step_btn", "n_clicks"),
)
def set_selected_tree_item_through_callback(n_clicks: int | None) -> dict[str, Any] | None:
    """Set the full tree selection to the Execution step."""
    if not n_clicks:
        raise PreventUpdate
    return Tree.ids.navlink_item("full_tree", "execution_step")


# ---------------------------------------------------------------------------
# Example 5 callbacks – Scenario A: disable / enable a single node
# ---------------------------------------------------------------------------


@callback(
    Input("wf_disable_step5_btn", "n_clicks"),
    Output(
        Tree.ids.navlink_item("workflow_tree", "wf_postprocess"),
        "disabled",
        allow_duplicate=True,
    ),
)
def disable_step5(n_clicks: int | None) -> bool:
    """Disable the Post-processing step (Step 5)."""
    if n_clicks:
        return True
    raise PreventUpdate


@callback(
    Input("wf_enable_step5_btn", "n_clicks"),
    Output(
        Tree.ids.navlink_item("workflow_tree", "wf_postprocess"),
        "disabled",
        allow_duplicate=True,
    ),
)
def enable_step5(n_clicks: int | None) -> bool:
    """Re-enable the Post-processing step (Step 5)."""
    if n_clicks:
        return False
    raise PreventUpdate


# ---------------------------------------------------------------------------
# Example 5 callbacks – Scenario B: disable / enable a downstream range
# ---------------------------------------------------------------------------


def _apply_range_disabled(
    all_ids: list[dict],
    current_disabled: list[bool],
    cutoff_id: str,
    value: bool,
) -> list[bool]:
    """Return disabled list with nodes from cutoff_id onwards set to value."""
    cutoff = _WORKFLOW_STEP_ORDER.index(cutoff_id)
    affected = set(_WORKFLOW_STEP_ORDER[cutoff:])
    return [
        value if id_dict["index"] in affected else current_disabled[i]
        for i, id_dict in enumerate(all_ids)
    ]


@callback(
    Input("wf_lock_from_step3_btn", "n_clicks"),
    Output(Tree.ids.navlink_item("workflow_tree", ALL), "disabled", allow_duplicate=True),
    State(Tree.ids.navlink_item("workflow_tree", ALL), "disabled"),
    State(Tree.ids.navlink_item("workflow_tree", ALL), "id"),
)
def lock_from_step3(
    n_clicks: int | None,
    current_disabled: list[bool],
    all_ids: list[dict],
) -> list[bool]:
    """Disable all steps from Solver Config (Step 3) onwards."""
    if n_clicks:
        return _apply_range_disabled(all_ids, current_disabled, "wf_config", True)
    raise PreventUpdate


@callback(
    Input("wf_unlock_from_step3_btn", "n_clicks"),
    Output(Tree.ids.navlink_item("workflow_tree", ALL), "disabled", allow_duplicate=True),
    State(Tree.ids.navlink_item("workflow_tree", ALL), "disabled"),
    State(Tree.ids.navlink_item("workflow_tree", ALL), "id"),
)
def unlock_from_step3(
    n_clicks: int | None,
    current_disabled: list[bool],
    all_ids: list[dict],
) -> list[bool]:
    """Re-enable all steps from Solver Config (Step 3) onwards."""
    if n_clicks:
        return _apply_range_disabled(all_ids, current_disabled, "wf_config", False)
    raise PreventUpdate


# ---------------------------------------------------------------------------
# Example 5 callbacks – Scenario C: disable / enable the entire tree
# ---------------------------------------------------------------------------


@callback(
    Input("wf_lock_all_btn", "n_clicks"),
    Output(Tree.ids.navlink_item("workflow_tree", ALL), "disabled", allow_duplicate=True),
    State(Tree.ids.navlink_item("workflow_tree", ALL), "id"),
)
def lock_all(n_clicks: int | None, all_ids: list[dict]) -> list[bool]:
    """Disable every node in the workflow tree (e.g. while a job is running)."""
    if n_clicks:
        return [True] * len(all_ids)
    raise PreventUpdate


@callback(
    Input("wf_unlock_all_btn", "n_clicks"),
    Output(Tree.ids.navlink_item("workflow_tree", ALL), "disabled", allow_duplicate=True),
    State(Tree.ids.navlink_item("workflow_tree", ALL), "id"),
)
def unlock_all(n_clicks: int | None, all_ids: list[dict]) -> list[bool]:
    """Re-enable every node in the workflow tree (e.g. after a job completes)."""
    if n_clicks:
        return [False] * len(all_ids)
    raise PreventUpdate
