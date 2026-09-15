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


"""Frontend of the input row array page."""

from typing import Any

from ansys.saf.glow.client import callback
from ansys.solutions.dash_super_components import InputRowArray
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ALL, Input, Output, State, html
import dash_mantine_components as dmc

from ansys.solutions.showcase_dash_super_components.ui.components.page_template import (
    layout as page_layout,
)
from ansys.solutions.showcase_dash_super_components.ui.utilities.common_colors import CommonColors

INFO_CARD_TEXT = [
    (
        "Input Row Array is a component that helps you to create a dynamic array "
        "of input rows. "
        "You can add or remove rows and get the values of the inputs."
    ),
]


def layout() -> html.Div:
    """Layout of the input row array page."""
    basic_items = [
        {
            "id": "name",
            "type": "TextInput",
            "properties": {
                "label": "Name",
            },
        },
        {
            "id": "count",
            "type": "NumberInput",
            "properties": {
                "label": "Count",
                "min": 0,
                "max": 100,
            },
        },
        {
            "id": "category",
            "type": "Select",
            "properties": {
                "label": "Category",
                "data": ["Option A", "Option B", "Option C"],
            },
        },
    ]

    advanced_items = [
        {
            "id": "description",
            "type": "TextInput",
            "properties": {
                "label": "Description",
                "placeholder": "Enter a short description",
                "description": "Brief summary of the entry",
            },
        },
        {
            "id": "lower_bound",
            "type": "NumberInput",
            "properties": {
                "label": "Lower Bound",
                "placeholder": "0.0",
                "description": "Minimum expected value",
                "min": -100,
                "max": 100,
                "step": 0.5,
                "decimalScale": 1,
                "suffix": " m",
            },
        },
        {
            "id": "upper_bound",
            "type": "NumberInput",
            "properties": {
                "label": "Upper Bound",
                "placeholder": "10.0",
                "description": "Maximum expected value",
                "min": -100,
                "max": 100,
                "step": 0.5,
                "decimalScale": 1,
                "suffix": " m",
            },
        },
        {
            "id": "method",
            "type": "Select",
            "properties": {
                "label": "Method",
                "placeholder": "Select a method",
                "description": "Selection method for interpolation",
                "data": ["Linear", "Cubic", "Nearest"],
                "searchable": True,
                "clearable": True,
            },
        },
    ]

    multi_row_items = [
        {
            "id": "input_1",
            "type": "TextInput",
            "properties": {
                "label": "Name",
                "placeholder": "Enter a name",
            },
        },
        {
            "id": "input_3",
            "type": "NumberInput",
            "properties": {
                "label": "Value",
                "placeholder": "Enter a value",
                "min": 0,
                "max": 100,
                "step": 1,
                "decimalScale": 1,
            },
        },
    ]
    main_content = html.Div(
        [
            html.Div(
                [
                    dmc.Text("Example 1 - Minimal Single Row", fw=700, size="xl"),
                    dmc.Text(
                        "Basic usage with a single fixed row containing one item of each "
                        "supported type (TextInput, NumberInput, Select) and only the required "
                        "properties configured.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    html.Div(
                        InputRowArray(
                            items=basic_items,
                            aio_id="single_array",
                        ),
                        style={"width": "640px"},
                    ),
                    dmc.Space(h=10),
                    dmc.Button(
                        "Print all inputs",
                        id="print_all_inputs_single",
                    ),
                    html.Div(id="print_all_inputs_single_output"),
                ],
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text("Example 2 - Single Row with Custom Properties", fw=700, size="xl"),
                    dmc.Text(
                        "Single fixed row with more detailed item configuration: a text field "
                        "with a placeholder and description hint, two numeric inputs with unit "
                        "suffix, step size, and decimal scale, and a searchable/clearable select.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    html.Div(
                        InputRowArray(
                            items=advanced_items,
                            aio_id="advanced_single_array",
                        ),
                    ),
                    dmc.Space(h=10),
                    dmc.Button(
                        "Print all inputs",
                        id="print_all_inputs_advanced_single",
                    ),
                    html.Div(id="print_all_inputs_advanced_single_output"),
                ],
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text("Example 3 - Dynamic Multiple Rows", fw=700, size="xl"),
                    dmc.Text(
                        "Advanced usage enabling multiple rows. Users can add and remove rows "
                        "dynamically. Each row uses the same column definitions. The buttons "
                        "below demonstrate how to read individual inputs or entire rows. "
                        "This Input Row Array is configured to take the full width of its "
                        "container, while the previous examples are inline-block and only take the "
                        "width needed to display their content.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    html.Div(
                        InputRowArray(
                            items=multi_row_items,
                            enable_multiple_rows=True,
                            aio_id="multiple_array",
                            full_width=True,
                        ),
                        style={"width": "480px"},
                    ),
                    dmc.Space(h=10),
                    dmc.Button(
                        "Print all rows for input 1",
                        id="print_all_rows_input_1",
                    ),
                    dmc.Space(h=5),
                    dmc.Button(
                        "Print all inputs for first row",
                        id="print_all_inputs_first_row",
                    ),
                    html.Div(id="print_multiple_output"),
                ],
            ),
        ],
        style={"width": "800px"},
    )
    return page_layout(
        page_title="Input Row Array",
        info_card_text=INFO_CARD_TEXT,
        main_content=main_content,
    )


@callback(
    Output("print_all_inputs_single_output", "children"),
    Input("print_all_inputs_single", "n_clicks"),
    State(InputRowArray.ids.input("single_array", ALL), "value"),
    prevent_initial_call=True,
)
def print_all_inputs_single(n_clicks: int, parameters: list[Any]) -> str:
    """Print all inputs from the single array."""
    if n_clicks:
        return f"parameters: {parameters}"
    raise PreventUpdate


@callback(
    Output("print_all_inputs_advanced_single_output", "children"),
    Input("print_all_inputs_advanced_single", "n_clicks"),
    State(InputRowArray.ids.input("advanced_single_array", ALL), "value"),
    prevent_initial_call=True,
)
def print_all_inputs_advanced_single(n_clicks: int, parameters: list[Any]) -> str:
    """Print all inputs from the advanced single row array."""
    if n_clicks:
        return f"parameters: {parameters}"
    raise PreventUpdate


@callback(
    Output("print_multiple_output", "children"),
    Input("print_all_rows_input_1", "n_clicks"),
    State(InputRowArray.ids.input("multiple_array", "input_1", ALL), "value"),
    prevent_initial_call=True,
)
def print_all_rows_input_1(n_clicks: int, parameters: list[Any]) -> str:
    """Print the values for input_1 for all rows of the multiple array."""
    if n_clicks:
        return f"parameters for input_1: {parameters}"
    raise PreventUpdate


@callback(
    Output("print_multiple_output", "children"),
    Input("print_all_inputs_first_row", "n_clicks"),
    State(InputRowArray.ids.input("multiple_array", ALL, 0), "value"),
    prevent_initial_call=True,
)
def print_all_inputs_first_row(n_clicks: int, parameters: list[Any]) -> str:
    """Print all inputs from the first row of the multiple array."""
    if n_clicks:
        return f"parameters for first row: {parameters}"
    raise PreventUpdate
