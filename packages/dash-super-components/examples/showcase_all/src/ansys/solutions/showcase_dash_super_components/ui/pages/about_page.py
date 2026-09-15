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


"""Frontend of the about page."""

from dash import dcc
from dash_extensions.enrich import html
import dash_mantine_components as dmc

from ansys.solutions.showcase_dash_super_components.ui.utilities.common_classes import (
    CommonCSSClassNames,
)


def layout() -> html.Div:
    """Layout of the about page."""
    return html.Div(
        [
            html.H1(
                "Showcase Super Components for Dash",
                className=CommonCSSClassNames.DISPLAY_3,
                style={
                    "fontSize": "48px",
                    "fontWeight": "bold",
                },
            ),
            html.P(
                (
                    "This solution showcases the use of Super Components for Dash in a SAF-based "
                    "solution."
                ),
                className=CommonCSSClassNames.LEAD,
                style={"fontSize": "20px"},
            ),
            dmc.Space(h=20),
            html.H4(
                "Description",
                style={
                    "fontSize": "24px",
                    "fontWeight": "bold",
                },
            ),
            dcc.Markdown(
                (
                    "This is a minimal SAF-based solution for showcasing and testing "
                    "Super Components for Dash.\n\n"
                    "The solution contains a page for each Super Component, showcasing "
                    "how to use the component and providing configuration examples.\n\n"
                    "Note that some components are only present in the UI, but not connected "
                    "to any backend logic."
                ),
                style={
                    "fontSize": "16px",
                    "textAlign": "justify",
                },
            ),
        ]
    )
