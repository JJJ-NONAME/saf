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

"""
User guide example for the Tree component.

Demonstrates basic usage, callback integration, and per-item styling.
See the Tree page in the User Guide for the full reference documentation.
"""

# [imports-start]
from ansys.solutions.dash_super_components import Tree, add_super_components_assets
from ansys.solutions.dash_super_components.utils.svg_icons import IconNames, create_base64_svg_src
# [imports-end]

from dash import _dash_renderer
from dash_extensions.enrich import DashProxy, Input, Output, callback, html
import dash_mantine_components as dmc

_dash_renderer._set_react_version("18.2.0")

app = DashProxy(__name__)
add_super_components_assets(app)

# [basic-items-start]
tree_items = [
    {
        "id": "step_1",
        "text": "Step 1",
        "icon": create_base64_svg_src(IconNames.MATERIAL_TREE),
        "expanded": True,
        "description": "First step",
        "children": [
            {
                "id": "step_11",
                "text": "Step 1-1",
                "icon": create_base64_svg_src(IconNames.MATERIAL_TREE),
                "description": "Sub-step",
            },
        ],
    },
    {
        "id": "step_2",
        "text": "Step 2",
        "icon": create_base64_svg_src(IconNames.MATERIAL_TREE),
        "description": "Second step",
    },
]
# [basic-items-end]


# [basic-layout-start]
layout = html.Div(
    [
        html.Div(id="selected-item"),
        Tree(
            items=tree_items,
            aio_id="navigation_tree",
            selected_item="step_1",
        ),
    ]
)
# [basic-layout-end]


# [styling-items-start]
tree_items_styled = [
    {"id": "step_1", "text": "Step 1 (custom color)", "styles": {"label": {"color": "#ff0000"}}},
    {
        "id": "step_2",
        "text": "Step 2 (custom background)",
        "styles": {"root": {"backgroundColor": "#f0f0f0"}},
    },
    {
        "id": "step_3",
        "text": "Step 3 (default color)",
        # no styles key: label color falls back to var(--mantine-color-text)
    },
]
# [styling-items-end]


# [styling-layout-start]
layout_tree_styled = html.Div(Tree(items=tree_items_styled, aio_id="styled_tree"))
# [styling-layout-end]


# [icon-type-items-start]
tree_items_icon_type = [
    {
        "id": "icon_type_no_type_specified",
        "text": "No icon type specified",
        "icon": create_base64_svg_src(IconNames.MATERIAL_WARNING),
        "description": "Icon type is automatically determined based on the icon value",
    },
    {
        "id": "icon_type_local",
        "text": "Forced local mode",
        "icon": create_base64_svg_src(IconNames.MATERIAL_WARNING),
        "icon_type": "local",
        "description": "Explicitly rendered as CSS-mask icon span",
    },
    {
        "id": "icon_type_iconify",
        "text": "Forced iconify mode",
        "icon": "material-symbols:warning",
        "icon_type": "iconify",
        "description": "Explicitly rendered via DashIconify",
    },
    {
        "id": "icon_type_auto",
        "text": "Auto icon type explicitly set",
        "icon": "material-symbols:warning",
        "icon_type": "auto",
        "description": "Icon type is automatically determined based on the icon value",
    },
]
# [icon-type-items-end]


layout_tree_icon_type = html.Div(Tree(items=tree_items_icon_type, aio_id="icon_type_tree"))


# [icons-dark-mode-options-start]
tree_items_dark_mode_options = [
    # Automatic adaptation: one icon for both themes with base64-encoded SVG
    {
        "id": "home",
        "text": "Local icon",
        "icon": create_base64_svg_src(IconNames.MATERIAL_HOME),
    },
    # Automatic adaptation: one icon for both themes with Iconify icon name
    {
        "id": "warning",
        "text": "Iconify icon",
        "icon": "material-symbols:warning",
    },
    # Iconify icon with explicit icon color.
    {
        "id": "success",
        "text": "Iconify icon with explicit icon_color",
        "icon": "material-symbols:check-circle",
        "icon_color": "var(--mantine-color-green-6)",
    },
    # Local icon with icon_color override for light and dark mode.
    {
        "id": "logo",
        "text": "Local icon with explicit icon_colors for light and dark mode",
        "icon": create_base64_svg_src(IconNames.MATERIAL_TREE),
        "icon_color": "light-dark(var(--mantine-color-blue-8), var(--mantine-color-blue-2))",
    },
]
# [icons-dark-mode-options-end]


# [layout-dark-mode-options-start]
layout_tree_dark_mode_options = html.Div(
    Tree(
        items=tree_items_dark_mode_options,
        aio_id="tree_dark_mode_options",
    )
)
# [layout-dark-mode-options-end]


app.layout = dmc.MantineProvider(
    html.Div(
        [
            dmc.Title("Tree — User Guide Example", order=2, mb="md"),
            dmc.Text("Click a node to see its ID displayed below.", c="dimmed", mb="lg"),
            layout,
            dmc.Divider(my="xl"),
            dmc.Text("Styled items (no interaction wired):", fw=600, mb="xs"),
            layout_tree_styled,
            dmc.Divider(my="xl"),
            dmc.Text("Explicit icon_type overrides:", fw=600, mb="xs"),
            layout_tree_icon_type,
            dmc.Divider(my="xl"),
            dmc.Text("Toggle dark mode:", fw=600, mb="xs"),
            dmc.ColorSchemeToggle(
                id="color-scheme-toggle",
                lightIcon=html.Img(src=create_base64_svg_src(IconNames.RADIX_SUN), width=36),
                darkIcon=html.Img(
                    src=create_base64_svg_src(IconNames.RADIX_MOON, color="#FFFFFF"), width=36
                ),
                color="yellow",
                size="lg",
                m="xl",
            ),
            dmc.Space(h=16),
            dmc.Text("Dark mode options (default automatic adaptation):", fw=600, mb="xs"),
            layout_tree_dark_mode_options,
        ],
        style={"maxWidth": 600, "margin": "40px auto", "padding": "0 16px"},
    )
)


# [basic-callback-start]
@callback(
    Output("selected-item", "children"),
    Input(Tree.ids.selected_item("navigation_tree"), "data"),
    prevent_initial_call=True,
)
def display_selected(value):
    """Display the selected item."""
    return f"Selected: {value['index']}"


# [basic-callback-end]


if __name__ == "__main__":
    app.run(debug=True)
