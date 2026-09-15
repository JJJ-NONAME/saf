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

"""GIF example page layout."""

import dash
from dash_extensions.enrich import html
import dash_gif_component as gif
from dash_iconify import DashIconify
import dash_mantine_components as dmc

dash.register_page(
    __name__,
    name="GIF Display",
    path_template="/projects/<project_id>/gif-display",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout() -> html.Div:
    """Layout of the GIF example page."""
    return html.Div(
        [
            html.H1("GIF image display", className="display-3", style={"font-size": "40px", "font-weight": "bold"}),
            html.Hr(className="my-2"),
            html.Br(),
            dmc.Blockquote(
                "Use a Dash plug-in to display a GIF image in the solution UI.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            html.Br(),
            html.Br(),
            html.Div(
                [
                    gif.GifPlayer(
                        gif="/assets/images/gif_example.gif",
                        autoplay=True,
                        still="/assets/images/gif_example.gif",
                    )
                ],
                style={
                    "height": "500px",
                    "display": "flex",
                    "justify-content": "center",
                    "align-items": "center",
                },
            ),
        ]
    )
