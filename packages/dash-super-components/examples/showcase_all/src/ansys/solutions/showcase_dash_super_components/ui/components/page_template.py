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


"""Info card component for displaying information."""

from typing import Any

from dash_extensions.enrich import html
import dash_mantine_components as dmc

from ansys.solutions.showcase_dash_super_components.ui.components.info_card import (
    layout as info_card_layout,
)
from ansys.solutions.showcase_dash_super_components.ui.utilities.common_classes import (
    CommonCSSClassNames,
)


def layout(page_title: str, info_card_text: list[str], main_content: Any) -> html.Div:
    """Provide the base layout template for a page in this app."""
    return html.Div(
        [
            html.H1(
                page_title,
                className=CommonCSSClassNames.DISPLAY_3,
                style={
                    "fontSize": "48px",
                    "fontWeight": "bold",
                },
            ),
            html.Hr(className=CommonCSSClassNames.HR_SPACER),
            html.Br(),
            dmc.Container(
                children=[
                    info_card_layout(info_card_text),
                    dmc.Space(h=40),
                    main_content,
                ],
                fluid=True,
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "flexDirection": "column",
                },
            ),
        ],
    )
