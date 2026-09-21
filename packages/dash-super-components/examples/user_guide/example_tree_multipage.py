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
User guide example for the Tree component in a multi-page Dash application.

Demonstrates how to use the Tree component as a multi-page navigation sidebar.
"""

# [tree-multipage-start]
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import (
    DashProxy,
    Input,
    Output,
    callback,
    callback_context,
    dcc,
    html,
)
import dash_mantine_components as dmc

from ansys.solutions.dash_super_components import Tree, add_super_components_assets
from ansys.solutions.dash_super_components.utils.svg_icons import IconNames, create_base64_svg_src


tree_items = [
    {
        "id": "step_1",
        "text": "Step 1",
        "expanded": True,
        "disabled": False,
        "description": "Level 1",
        "children": [
            {
                "id": "step_11",
                "text": "Step 1-1",
                "expanded": True,
                "disabled": False,
                "description": "Level 1-1",
                "children": [
                    {
                        "id": "step_111",
                        "text": "Step 1-1-1",
                        "expanded": True,
                        "disabled": False,
                        "description": "Level 1-1-1",
                    },
                ],
            },
        ],
    },
    {
        "id": "step_2",
        "text": "Step 2",
        "expanded": True,
        "disabled": False,
        "description": "Level 2",
    },
]

layout = dmc.MantineProvider(
    [
        html.Div(
            [
                dcc.Location(id="url", refresh=False),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            Tree(
                                items=tree_items,
                                aio_id="navigation_tree",
                                selected_item="step_1",
                                default_icon=create_base64_svg_src(IconNames.MATERIAL_TREE),
                            ),
                            span=2,
                        ),
                        dmc.GridCol(
                            html.Div(
                                id="page-content",
                                style={"paddingRight": "0.7%"},
                            ),
                            span=10,
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input(Tree.ids.selected_item("navigation_tree"), "data"),
    prevent_initial_call=True,
)
def display_page(pathname, selected_item):
    """Display page content."""
    triggered_id = callback_context.triggered_id
    if triggered_id == "url" or not selected_item:
        return Step1Page.layout()
    elif triggered_id == Tree.ids.selected_item("navigation_tree"):
        page_id = Tree.ids.get_index_from_navlink_item_id(selected_item)
        if page_id == "step_1":
            return Step1Page.layout()
        elif page_id == "step_11":
            return Step11Page.layout()
        elif page_id == "step_111":
            return Step111Page.layout()
        elif page_id == "step_2":
            return Step2Page.layout()
        else:
            raise ValueError(f"Unknown page selection: {page_id}")
    raise PreventUpdate


# [tree-multipage-end]


class Step1Page:
    @staticmethod
    def layout():
        return html.Div(
            [
                html.H1(
                    "Step 1",
                    style={
                        "fontSize": "48px",
                        "fontWeight": "bold",
                        "marginTop": "0",
                    },
                ),
                html.P("Content for Step 1."),
            ],
        )


class Step11Page:
    @staticmethod
    def layout():
        return html.Div(
            [
                html.H1(
                    "Step 1-1",
                    style={
                        "fontSize": "48px",
                        "fontWeight": "bold",
                        "marginTop": "0",
                    },
                ),
                html.P("Content for Step 1-1."),
            ],
        )


class Step111Page:
    @staticmethod
    def layout():
        return html.Div(
            [
                html.H1(
                    "Step 1-1-1",
                    style={
                        "fontSize": "48px",
                        "fontWeight": "bold",
                        "marginTop": "0",
                    },
                ),
                html.P("Content for Step 1-1-1."),
            ],
        )


class Step2Page:
    @staticmethod
    def layout():
        return html.Div(
            [
                html.H1(
                    "Step 2",
                    style={
                        "fontSize": "48px",
                        "fontWeight": "bold",
                        "marginTop": "0",
                    },
                ),
                html.P("Content for Step 2."),
            ],
        )


# %%
# Run the app
# -----------
from dash import _dash_renderer

# Required only for Dash 2.x to use Mantine-based components
_dash_renderer._set_react_version("18.2.0")

app = DashProxy(__name__)
add_super_components_assets(app)
app.layout = layout

if __name__ == "__main__":
    app.run(debug=True)
