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

import dash  # pyright: ignore[reportMissingTypeStubs, reportUnknownMemberType]
from dash_extensions.enrich import html  # pyright: ignore[reportMissingTypeStubs]
import dash_mantine_components as dmc  # pyright: ignore[reportMissingTypeStubs, reportAttributeAccessIssue, reportUnknownMemberType]

dash.register_page(  # pyright: ignore[reportUnknownMemberType]
    __name__,
    name="About",
    path_template="/projects/<project_id>",
    icon_asset_name="material-symbols--home.svg",
    icon_asset_path="icons",
)


def layout():
    """Layout of the about page."""
    return html.Div(
        [
            html.H1("My Solution", className="display-3", style={"font-size": "48px", "fontWeight": "bold"}),
            html.P(
                "Add a short sentence to describe the goal of the solution.",
                className="lead",
                style={"font-size": "20px"},
            ),
            dmc.Space(h=20),
            dmc.Grid(
                [
                    dmc.GridCol(  # pyright: ignore[reportMissingTypeStubs, reportAttributeAccessIssue, reportUnknownMemberType]
                        [
                            dmc.Space(h=30),
                            html.H4("Description", style={"font-size": "24px", "fontWeight": "bold"}),
                            html.P(
                                "Put here a short description of the solution.",
                                style={"font-size": "16px", "textAlign": "justify"},
                            ),
                            dmc.Space(h=30),
                            html.H4("Customer Goals", style={"font-size": "24px", "fontWeight": "bold"}),
                            html.P(
                                "What are the benefits for the customer?",
                                style={"font-size": "16px", "textAlign": "justify"},
                            ),
                            dmc.Space(h=30),
                            html.H4("Engineering Goals", style={"font-size": "24px", "fontWeight": "bold"}),
                            html.P(
                                "What is the engineering problem to solve? What are the Key Performance "
                                "Indicators (KPIs) to monitor?",
                                style={"font-size": "16px", "textAlign": "justify"},
                            ),
                        ],
                        span=6,
                    ),
                    dmc.GridCol(  # pyright: ignore[reportMissingTypeStubs, reportAttributeAccessIssue, reportUnknownMemberType]
                        [
                            dmc.Image(
                                src=dash.get_asset_url("images/workflow-placeholder.png"),  # pyright: ignore[reportUnknownMemberType]
                                alt="This is the introduction image.",
                            ),
                        ],
                        span=6,
                    ),
                ],
            ),
        ],
    )
