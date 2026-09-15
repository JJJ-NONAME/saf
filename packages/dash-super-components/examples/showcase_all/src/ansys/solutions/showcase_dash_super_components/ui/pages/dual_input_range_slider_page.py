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


"""Frontend of the dual input range slider page."""

from ansys.solutions.dash_super_components import DualInputRangeSlider
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, callback, html
import dash_mantine_components as dmc

from ansys.solutions.showcase_dash_super_components.ui.components.page_template import (
    layout as page_layout,
)
from ansys.solutions.showcase_dash_super_components.ui.utilities.common_colors import CommonColors

INFO_CARD_TEXT = [
    (
        "Dual Input Range Slider is a component that allows you to select a lower "
        "and an upper value. It can be controlled by dragging the handles or by "
        "typing the values in the input fields."
    ),
    "The slider handles and number inputs always stay in sync.",
]


def layout() -> html.Div:
    """Layout of the dual input range slider page."""
    main_content = html.Div(
        [
            html.Div(
                [
                    dmc.Text("Example 1 - Default Slider", fw=700, size="xl"),
                    dmc.Text(
                        "Minimal usage with only the required min and max arguments. "
                        "The range defaults to the full [0, 100] interval with integer steps.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    html.Div(
                        DualInputRangeSlider(
                            aio_id="slider_default",
                            min=0,
                            max=100,
                        ),
                        style={"width": "600px"},
                    ),
                ],
                style={"width": "800px"},
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text("Example 2 - Customized Fine-Grained Slider", fw=700, size="xl"),
                    dmc.Text(
                        "Advanced usage with a narrower range of [-1, 1], a step of 0.1, "
                        "two decimal places, and a pre-set initial selection of [0.2, 0.8]. "
                        "The output below the slider updates live as the handles are moved.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    html.Div(
                        DualInputRangeSlider(
                            aio_id="slider_custom",
                            min=-1,
                            max=1,
                            decimal_scale=2,
                            step=0.1,
                            value=[0.2, 0.8],
                        ),
                        style={"width": "600px"},
                    ),
                    dmc.Text(
                        "Move the slider to see its value here.", id="slider-read-output", mt="sm"
                    ),
                ],
                style={"width": "800px"},
            ),
        ],
    )
    return page_layout(
        page_title="Dual Input Range Slider",
        info_card_text=INFO_CARD_TEXT,
        main_content=main_content,
    )


@callback(
    Output("slider-read-output", "children"),
    Input(DualInputRangeSlider.ids.slider("slider_custom"), "value"),
)
def show_value(value: list[float]) -> str:
    """Display the currently selected range."""
    if not value:
        raise PreventUpdate
    lower, upper = value
    return f"Selected range: {lower} - {upper}"
