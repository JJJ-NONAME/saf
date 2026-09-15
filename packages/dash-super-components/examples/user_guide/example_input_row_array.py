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
User guide example for the InputRowArray component.

Demonstrates basic usage (single row), advanced usage (multiple dynamic rows),
and a callback that collects all values using pattern-matching wildcards.
See the InputRowArray page in the User Guide for the full reference documentation.
"""

# [imports-start]
from ansys.solutions.dash_super_components import InputRowArray
# [imports-end]

from dash import _dash_renderer
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Input, Output, State, callback, html
import dash_mantine_components as dmc

_dash_renderer._set_react_version("18.2.0")

app = DashProxy(__name__)


# [basic-layout-start]
def layout():
    items = [
        {
            "id": "input_1",
            "type": "TextInput",
            "properties": {
                "label": "Name",
                "placeholder": "Enter a name",
            },
        },
        {
            "id": "input_2",
            "type": "NumberInput",
            "properties": {
                "label": "Value",
                "placeholder": "Enter a value",
                "min": 0,
                "max": 100,
            },
        },
        {
            "id": "input_3",
            "type": "Select",
            "properties": {
                "label": "Category",
                "placeholder": "Select a category",
                "data": ["Option A", "Option B", "Option C"],
            },
        },
    ]
    return html.Div(
        [
            InputRowArray(
                items=items,
                aio_id="basic-array",
            )
        ]
    )


# [basic-layout-end]


# [advanced-layout-start]
def advanced_layout():
    items = [
        {
            "id": "input_1",
            "type": "TextInput",
            "properties": {
                "label": "Input 1",
                "placeholder": "Enter input 1",
            },
        },
        {
            "id": "input_2",
            "type": "NumberInput",
            "properties": {
                "label": "Input 2",
                "placeholder": "Enter input 2",
                "min": 0,
                "max": 100,
                "step": 1,
            },
        },
    ]
    return html.Div(
        [
            InputRowArray(
                items=items,
                enable_multiple_rows=True,
                aio_id="multi-row-array",
                full_width=True,
            ),
        ],
        style={"width": "500px"},
    )


# [advanced-layout-end]


app.layout = dmc.MantineProvider(
    html.Div(
        [
            dmc.Title("Input Row Array — User Guide Example", order=2, mb="md"),
            dmc.Text("Basic (single row):", fw=600, mb="xs"),
            layout(),
            dmc.Divider(my="xl"),
            dmc.Text("Advanced (multiple rows):", fw=600, mb="xs"),
            advanced_layout(),
            dmc.Button("Get all inputs", id="get-all-inputs-button", mt="md"),
            html.Div(id="all-inputs-output", style={"marginTop": "12px", "color": "dimgray"}),
            dmc.Button("Get first row inputs", id="get-first-row-inputs-button", mt="md"),
            html.Div(id="first-row-output", style={"marginTop": "12px", "color": "dimgray"}),
            dmc.Button("Get input 1 values", id="get-input-1-values-button", mt="md"),
            html.Div(id="input-1-values-output", style={"marginTop": "12px", "color": "dimgray"}),
        ],
        style={"maxWidth": 900, "margin": "40px auto", "padding": "0 16px"},
    )
)


# [all-values-callback-start]
from dash_extensions.enrich import ALL


@callback(
    Output("all-inputs-output", "children"),
    Input("get-all-inputs-button", "n_clicks"),
    State(InputRowArray.ids.input("multi-row-array", ALL, ALL), "value"),
    prevent_initial_call=True,
)
def collect_values(n_clicks, values):
    """Collect values from all rows of the InputRowArray."""
    if n_clicks:
        return str(values)
    raise PreventUpdate


# [all-values-callback-end]


# [first-row-values-callback-start]
@callback(
    Output("first-row-output", "children"),
    Input("get-first-row-inputs-button", "n_clicks"),
    State(InputRowArray.ids.input("multi-row-array", ALL, 0), "value"),
    prevent_initial_call=True,
)
def collect_first_row_values(n_clicks, values):
    """Collect values from the first row of the InputRowArray."""
    if n_clicks:
        return str(values)
    raise PreventUpdate


# [first-row-values-callback-end]


# [collect-input-1-values-callback-start]
@callback(
    Output("input-1-values-output", "children"),
    Input("get-input-1-values-button", "n_clicks"),
    State(InputRowArray.ids.input("multi-row-array", "input_1", ALL), "value"),
    prevent_initial_call=True,
)
def collect_input_1_values(n_clicks, values):
    """Collect values from the input_1 field across all rows of the InputRowArray."""
    if n_clicks:
        return str(values)
    raise PreventUpdate


# [collect-input-1-values-callback-end]

if __name__ == "__main__":
    app.run(debug=True)
