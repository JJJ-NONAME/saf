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

"""Frontend of the Dash components page."""

import dash
from dash_extensions.enrich import dcc, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

dash.register_page(
    __name__,
    name="Dash Components",
    path_template="/projects/<project_id>/dash-components",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout() -> html.Div:
    """Layout of the Dash components example page."""
    text_input = dcc.Input(
        id="input-example",
        value="",
        placeholder="Enter a value...",
        type="text",
    )
    html.Br(),

    checklist = dcc.Checklist(
        id="checklist-example",
        options=["Gather data", "Develop model", "Perform analysis"],
        value=["Gather data", "Develop model"],
    )
    html.Br(),

    radio_items = dcc.RadioItems(
        id="radio-items-example", options=["Option 1", "Option 2", "Option 3"], value="Option 2"
    )
    html.Br(),

    button = dmc.Button(
        "Submit", id="button-example", style={"color": "var(--mantine-color-body)", "background-color": "#2790F1"}
    )
    html.Br(),

    dropdown = dmc.Select(
        id="dropdown-example",
        data=["a", "b", "c"],
        value="a",
        w="50%",
        searchable=True,
        clearable=True,
        placeholder="Select an option",
        size="md",
    )
    html.Br(),

    accordion = dmc.Accordion(
        value=[""],
        multiple=True,
        children=[
            dmc.AccordionItem(
                [
                    dmc.AccordionControl(
                        "Accordion example",
                        style={
                            "backgroundColor": "#0A76DB",
                            "color": "var(--mantine-color-body)",
                        },
                    ),
                    dmc.AccordionPanel(
                        "Accordion content",
                        style={
                            "backgroundColor": "var(--mantine-color-body)",
                            "color": "var(--mantine-color-text)",
                        },
                    ),
                ],
                value="accordion-example",
                style={
                    "border": "1px solid var(--mantine-color-default-border)",
                    "borderRadius": "8px",
                    "overflow": "hidden",
                },
            ),
        ],
    )

    return html.Div(
        [
            html.H1("Dash components", className="display-3", style={"font-size": "40px", "font-weight": "bold"}),
            html.Hr(className="my-2"),
            html.Br(),
            dmc.Blockquote(
                "Use open-source components from the Dash Core Components, Dash HTML Components, and\
                Dash Mantine Components libraries to build a solution UI page layout.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            html.Br(),
            html.Br(),
            dmc.Text("Input", style={"font-size": "17px", "fontWeight": "bold"}),
            text_input,
            html.Br(),
            html.Br(),
            html.Br(),
            dmc.Text("Checklist", style={"font-size": "17px", "fontWeight": "bold"}),
            checklist,
            html.Br(),
            html.Br(),
            dmc.Text("RadioItems", style={"font-size": "17px", "fontWeight": "bold"}),
            radio_items,
            html.Br(),
            html.Br(),
            dmc.Text("Button", style={"font-size": "17px", "fontWeight": "bold"}),
            button,
            html.Br(),
            html.Br(),
            html.Br(),
            dmc.Text("Dropdown", style={"font-size": "17px", "fontWeight": "bold"}),
            dropdown,
            html.Br(),
            html.Br(),
            dmc.Text("Accordion", style={"font-size": "17px", "fontWeight": "bold"}),
            accordion,
            html.Br(),
            html.Br(),
        ]
    )
