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
User guide example for the InputForm component.

Demonstrates basic usage (text + number fields), advanced usage (full-featured
form with label/unit/help/description columns, a hidden slider, and a checkbox
to reveal it), and callbacks for retrieving field values and toggling visibility.
See the InputForm page in the User Guide for the full reference documentation.
"""

# [imports-start]
from ansys.solutions.dash_super_components import InputForm
# [imports-end]

from dash import _dash_renderer
from dash_extensions.enrich import DashProxy, Input, Output, State, callback, html
import dash_mantine_components as dmc

_dash_renderer._set_react_version("18.2.0")

app = DashProxy(__name__)


# [basic-layout-start]
def layout():
    input_form = InputForm(
        [
            {
                "label": "Name",
                "fields": [
                    {
                        "type": "TextInput",
                        "id": "name-input",
                        "placeholder": "Enter a name",
                    }
                ],
            },
            {
                "label": "Value",
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "value-input",
                        "min": 0,
                        "max": 100,
                        "value": 50,
                    }
                ],
            },
        ],
        aio_id="basic-form",
        title="Basic Form",
    )
    return html.Div(input_form, style={"width": "900px"})


# [basic-layout-end]


# [advanced-layout-start]
def advanced_layout():
    input_form = InputForm(
        [
            {
                "id": "number-row-1",  # sets row_index to "number-row-1"
                "label": "Number Input",
                "fields": [
                    {
                        "type": "NumberInput",
                        "value": 2,
                        "min": 0,
                        "max": 10,
                        "id": "number-input-1",
                        "required": True,
                    }
                ],
                "help": [html.Div("Help content")],
                "unit": "Kgm^{2}s^{-3}A^{-1}",
                "description": "This is a number input field with a unit and a description.",
            },
            {
                "id": "number-row-2",  # sets row_index to "number-row-2"
                "label": "Number Input",
                "fields": [
                    {
                        "type": "NumberInput",
                        "value": 50,
                        "min": 0,
                        "max": 100,
                        "id": "number-input-2",
                        "required": True,
                    }
                ],
                "unit": "m",
                "description": "This is another number input field with a unit and a description.",
            },
            {
                "id": "select-row",
                "label": "Select",
                "fields": [
                    {
                        "type": "Select",
                        "value": "2",
                        "data": ["2", "3", "4"],
                        "id": "select-1",
                        "required": True,
                    }
                ],
                "help": [html.Div("Dash Mantine Components | Select")],
                "description": "This is a select field with a description.",
            },
            {
                "id": "checkbox-row",
                "label": "Enable slider",
                "fields": [
                    {
                        "type": "Checkbox",
                        "id": "checkbox-1",
                        "checked": False,
                        "size": "md",
                    }
                ],
                "description": "Check to reveal the slider below.",
            },
            {
                "id": "slider-row",
                "label": "Slider",
                "fields": [
                    {
                        "type": "Slider",
                        "id": "slider-1",
                        "min": 0,
                        "max": 100,
                        "value": 50,
                        "hidden": True,  # hidden until the checkbox above is checked
                    }
                ],
                "description": "This slider is hidden until enabled.",
            },
        ],
        aio_id="full-form",
        title="Full-Featured Form",
        title_props={"style": {"fontSize": "24px", "color": "blue"}},
        card_props={"shadow": "none", "withBorder": False},
        columns=["label", "fields", "unit", "help", "description"],
        column_widths={"label": 2, "fields": 3, "unit": 2, "help": 1, "description": 4},
        column_names=["Parameter", "Value", "Unit", "Info", "Description"],
    )
    return html.Div(
        input_form,
        style={"width": "900px"},
    )


# [advanced-layout-end]


def composed_form_layout():
    front_wheels_form = InputForm(
        [
            {
                "label": "Use default values",
                "fields": [
                    {
                        "type": "Checkbox",
                        "id": "use_defaults",
                        "checked": True,
                    },
                ],
            },
            {
                "label": "Wheel diameter",
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "diameter",
                        "value": 90,
                        "min": 0,
                        "max": 180,
                    }
                ],
                "unit": "mm",
            },
            {
                "label": "Wheel material",
                "fields": [
                    {
                        "type": "Select",
                        "value": "Rubber",
                        "data": ["Rubber", "Plastic", "Metal"],
                        "id": "wheel_material",
                    }
                ],
            },
        ],
        aio_id="front-wheels",
        title="Front Wheels",
        columns=["label", "fields", "unit"],
        column_widths={"label": 3, "fields": 3, "unit": 1},
        with_card=False,
    )

    rear_wheels_form = InputForm(
        [
            {
                "label": "Use default values",
                "fields": [
                    {
                        "type": "Checkbox",
                        "id": "use_defaults",
                        "checked": True,
                    },
                ],
            },
            {
                "label": "Wheel diameter",
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "diameter",
                        "value": 90,
                        "min": 0,
                        "max": 180,
                    }
                ],
                "unit": "mm",
            },
            {
                "label": "Wheel material",
                "fields": [
                    {
                        "type": "Select",
                        "value": "Rubber",
                        "data": ["Rubber", "Plastic", "Metal"],
                        "id": "wheel_material",
                    }
                ],
            },
        ],
        aio_id="rear-wheels",
        title="Rear Wheels",
        columns=["label", "fields", "unit"],
        column_widths={"label": 3, "fields": 3, "unit": 1},
        with_card=False,
    )

    return html.Div(
        dmc.Card(
            [
                front_wheels_form,
                html.Br(),
                rear_wheels_form,
            ],
            withBorder=True,
            shadow="sm",
            radius="md",
            style={"maxWidth": "600px"},
        ),
        style={"width": "900px"},
    )


# [control-persistence-start]
def control_persistence_layout():
    input_form = InputForm(
        [
            {
                "label": "Some input field",
                "fields": [
                    {
                        "type": "TextInput",
                        "id": "some-input-field",
                        "placeholder": "Enter some text here",
                    }
                ],
                "description": "This value is retained in the browser due to global persistence "
                "settings.",
            },
            {
                "label": "API Token",
                "fields": [
                    {
                        "type": "PasswordInput",
                        "id": "api-token",
                        "placeholder": "Paste your token here",
                        "persistence": False,  # always reset to the server-provided value
                    }
                ],
                "description": "Token is never retained in the browser.",
            },
        ],
        aio_id="persistence-control-form",
        columns=["label", "fields", "description"],
        persistence=True,  # enables persistence for the form
        persistence_type="session",  # values are stored in sessionStorage
    )
    return html.Div(input_form, style={"width": "900px"})


# [control-persistence-end]


app.layout = dmc.MantineProvider(
    html.Div(
        [
            dmc.Title("Input Form — User Guide Example", order=2, mb="md"),
            dmc.Text("Basic form:", fw=600, mb="xs"),
            layout(),
            dmc.Divider(my="xl"),
            dmc.Text("Full-featured form:", fw=600, mb="xs"),
            advanced_layout(),
            html.Div(id="output", style={"marginTop": "16px", "color": "dimgray"}),
            dmc.Button("Submit", id="submit-button", mt="md"),
            html.Div(id="output_submit", style={"marginTop": "16px", "color": "dimgray"}),
            dmc.Divider(my="xl"),
            dmc.Text("Composed form example with shared field types and IDs:", fw=600, mb="xs"),
            composed_form_layout(),
            dmc.Divider(my="xl"),
            dmc.Text("Form with global and per-field persistence control:", fw=600, mb="xs"),
            control_persistence_layout(),
        ],
        style={"maxWidth": "950px", "margin": "40px auto", "padding": "0 16px"},
    )
)


# [specific-field-callback-start]
@callback(
    Output("output", "children"),
    Input(
        InputForm.ids.field("full-form", "NumberInput", "number-input-1", "number-row-1"), "value"
    ),
    Input(
        InputForm.ids.field("full-form", "NumberInput", "number-input-2", "number-row-2"), "value"
    ),
    Input(InputForm.ids.field("full-form", "Select", "select-1", "select-row"), "value"),
    Input(InputForm.ids.field("full-form", "Checkbox", "checkbox-1", "checkbox-row"), "checked"),
    prevent_initial_call=True,
)
def collect_inputs(number_input_1, number_input_2, select_1, checkbox_1):
    """Collect individual field values."""
    return f"{number_input_1} | {number_input_2} | {select_1} | {checkbox_1}"


# [specific-field-callback-end]


# [number-inputs-callback-start]
from dash_extensions.enrich import ALL


@callback(
    Output("output_submit", "children"),
    Input("submit-button", "n_clicks"),
    State(
        InputForm.ids.field("full-form", "NumberInput", field_id=ALL, row_index=ALL),
        "value",
    ),
    prevent_initial_call=True,
)
def get_all_number_inputs(n_clicks, values):
    """Get all NumberInput values from the form."""
    return f"Number Inputs: {values}"


# [number-inputs-callback-end]


# [color-callback-start]
from dash_extensions.enrich import MATCH


@callback(
    Output(InputForm.ids.label(aio_id="full-form", row_index=MATCH), "c"),
    Output(InputForm.ids.unit(aio_id="full-form", row_index=MATCH), "c"),
    Input(
        InputForm.ids.field(
            aio_id="full-form", field_type="NumberInput", field_id="number-input-1", row_index=MATCH
        ),
        "value",
    ),
    Input(
        InputForm.ids.field(
            aio_id="full-form", field_type="NumberInput", field_id="number-input-1", row_index=MATCH
        ),
        "min",
    ),
    Input(
        InputForm.ids.field(
            aio_id="full-form", field_type="NumberInput", field_id="number-input-1", row_index=MATCH
        ),
        "max",
    ),
)
def color_row_by_value(value, min_value, max_value):
    """Color label and unit based on value relative to the valid range."""
    value_range = max_value - min_value
    if value < min_value + 0.2 * value_range or value > min_value + 0.8 * value_range:
        return "orange", "orange"
    else:
        return "var(--mantine-color-text)", "var(--mantine-color-text)"


# [color-callback-end]


# [disable-parameters-callback-start]
@callback(
    Output(
        InputForm.ids.field(
            aio_id=MATCH, field_type="NumberInput", field_id="diameter", row_index=ALL
        ),
        "disabled",
    ),
    Output(
        InputForm.ids.field(
            aio_id=MATCH, field_type="Select", field_id="wheel_material", row_index=ALL
        ),
        "disabled",
    ),
    Input(
        InputForm.ids.field(
            aio_id=MATCH, field_type="Checkbox", field_id="use_defaults", row_index=ALL
        ),
        "checked",
    ),
)
def enable_disable_wheel_parameters(use_defaults):
    """Disable or enable wheel fields when 'Use defaults' is toggled."""
    disabled = bool(use_defaults[0])
    return [disabled], [disabled]


# [disable-parameters-callback-end]


# [toggle-visibility-callback-start]
@callback(
    Output(
        InputForm.ids.field_div("full-form", "Slider", "slider-1", row_index="slider-row"),
        "style",
    ),
    Input(
        InputForm.ids.field("full-form", "Checkbox", "checkbox-1", row_index="checkbox-row"),
        "checked",
    ),
    State(
        InputForm.ids.field_div("full-form", "Slider", "slider-1", row_index="slider-row"),
        "style",
    ),
)
def toggle_parameter_visibility(checked, style_slider):
    """Toggle slider visibility based on checkbox state."""
    if checked:
        style_slider["display"] = "block"
    else:
        style_slider["display"] = "none"
    return style_slider


# [toggle-visibility-callback-end]


if __name__ == "__main__":
    app.run(debug=True)
