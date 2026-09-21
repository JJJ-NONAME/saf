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

"""Frontend of the display_images step."""

import time
from typing import Any

from ansys.saf.glow.client import callback
import dash
from dash_extensions.enrich import Input, Output, State, html  # pyright: ignore[reportMissingTypeStubs]
from dash_iconify import DashIconify  # pyright: ignore[reportMissingTypeStubs]
import dash_mantine_components as dmc  # pyright: ignore[reportMissingTypeStubs]

from saf.solutions.examples.solution.definition import ExamplesSolution

dash.register_page(
    __name__,
    name="Image Display",
    path_template="/projects/<project_id>/image-display",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout(project: ExamplesSolution) -> html.Div:
    """Layout of the display_images step UI."""
    return html.Div(
        [
            html.H1(
                "File-based image display", className="display-3", style={"font-size": "40px", "font-weight": "bold"}
            ),
            dmc.Blockquote(
                "Use SAF GLOW to parse and store files and display them as images in a solution UI.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            html.Br(),
            html.Br(),
            dmc.Button(
                "Create and display images",
                id="create-and-display-images",
                variant="filled",
                radius="sm",
                style={"font-size": "16px", "background-color": "#2790F1"},
                leftSection=DashIconify(icon="streamline:startup-solid"),
            ),
            html.Br(),
            html.Br(),
            html.Div(id="result-images", children=create_image_div(project)),
        ],
        style={"paddingLeft": "20px"},
    )


# This is an example callback which stores entered data and executes a method.
# This is the only place where user entered data is persisted in this Dash app.
@callback(
    Output("result-images", "children"),
    Input("create-and-display-images", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def create_images(n_clicks: int, project: ExamplesSolution) -> list[Any]:
    """Display images through callback."""
    step = project.steps.basic_step
    step.create_images()
    image_div_children = create_image_div(project)
    return image_div_children


def create_image_div(project: ExamplesSolution) -> list[Any]:
    """Create image div."""
    all_images: list[Any] = []
    step = project.steps.basic_step
    for image_url in step.get_data("result_files", substitute_file_handles_with_urls=True):
        # Adding a timestamp to the image URL to prevent browser caching issues
        all_images += [
            html.Div(html.Img(src=f"{image_url}?t={int(time.time())}", height="400px"), style={"flex": "1"}),
            dmc.Space(h=20),
        ]

    return all_images
