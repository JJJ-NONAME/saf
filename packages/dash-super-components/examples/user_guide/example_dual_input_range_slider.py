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
User guide example for the DualInputRangeSlider component.

Demonstrates basic usage (integer range) and advanced usage (custom range,
precision, and styling).
See the DualInputRangeSlider page in the User Guide for the full reference documentation.
"""

# [imports-start]
from ansys.solutions.dash_super_components import DualInputRangeSlider
# [imports-end]

from dash import _dash_renderer
from dash_extensions.enrich import DashProxy, Input, Output, callback, html
import dash_mantine_components as dmc

_dash_renderer._set_react_version("18.2.0")

app = DashProxy(__name__)


# [basic-layout-start]
def layout():
    return html.Div(
        [
            DualInputRangeSlider(
                min=0,
                max=100,
                aio_id="dual-input-range-slider",
            )
        ],
        style={"width": "500px"},
    )


# [basic-layout-end]


# [advanced-layout-start]
def advanced_layout():
    return html.Div(
        [
            DualInputRangeSlider(
                aio_id="custom-slider",
                min=-1,
                max=1,
                step=0.1,
                decimal_scale=2,
                value=[0.2, 0.8],
                slider_props={
                    "style": {"width": "450px"},
                    "marks": [
                        {"value": -1, "label": "-1"},
                        {"value": 0, "label": "0"},
                        {"value": 1, "label": "1"},
                    ],
                },
                lower_bound_input_props={
                    "label": "Lower",
                    "style": {"width": "130px"},
                },
                upper_bound_input_props={
                    "label": "Upper",
                    "style": {"width": "130px"},
                },
            )
        ],
    )


# [advanced-layout-end]


app.layout = dmc.MantineProvider(
    html.Div(
        [
            dmc.Title("Dual Input Range Slider — User Guide Example", order=2, mb="md"),
            dmc.Text("Basic (0 – 100):", fw=600, mb="xs"),
            layout(),
            dmc.Space(h=16),
            dmc.Text(id="slider-output", c="dimmed"),
            dmc.Divider(my="xl"),
            dmc.Text("Advanced (−1 to 1, step 0.1):", fw=600, mb="xs"),
            advanced_layout(),
        ],
        style={"maxWidth": 800, "margin": "40px auto", "padding": "0 16px"},
    )
)


@callback(
    Output("slider-output", "children"),
    Input(DualInputRangeSlider.ids.slider("dual-input-range-slider"), "value"),
)
def show_value(value):
    """Display the current range of the basic slider."""
    if value is None:
        return ""
    lower, upper = value
    return f"Basic slider range: {lower} – {upper}"


if __name__ == "__main__":
    app.run(debug=True)
