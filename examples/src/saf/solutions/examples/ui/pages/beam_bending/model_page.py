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

"""Frontend of the first step."""

import base64
import os
from pathlib import Path

import dash
from dash_extensions.enrich import dcc, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

dash.register_page(
    __name__,
    name="Beam Bending Model",
    path_template="/projects/<project_id>/beam-bending-model",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout() -> html.Div:
    """Layout of the about page."""
    sketch = base64.b64encode(
        open(
            os.path.join(Path(__file__).absolute().parent.parent.parent, "assets", "images", "beam_model.png"), "rb"
        ).read()
    )

    return html.Div(
        dmc.Container(
            [
                html.H1("Beam Deflection", className="display-3", style={"font-size": "40px", "font-weight": "bold"}),
                dmc.Blockquote(
                    "In this example, we will predict the deflection of a simply supported beam subjected to a "
                    "concentrated load using the Euler-Bernoulli beam theory and Ansys MAPDL. The goal is to "
                    "show how to use SAF GLOW to invoke a simple business logic and how to invoke Ansys products "
                    "via the instance management API.",
                    icon=DashIconify(icon="material-symbols:info", width=30),
                    style={"font-size": "18px", "fontStyle": "italic"},
                ),
                dmc.Space(h=20),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Grid(
                                    [
                                        dcc.Markdown(
                                            """
                                            **Engineering problem**

                                            Consider a simply supported uniform beam of
                                            length $l$ subjected to a concentrated
                                            load $P$ applied at a specific point. We want to predict the beam deflection
                                            given the position of $P$ along the beam centerline.
                                            """,
                                            mathjax=True,
                                            className="lead",
                                            style={
                                                "textAlign": "left",
                                                "marginLeft": "auto",
                                                "marginRight": "auto",
                                                "font-size": "16px",
                                            },
                                        ),
                                        html.Br(),
                                        dcc.Markdown(
                                            """
                                            **Model**

                                            The Euler-Bernoulli beam theory is used to predict the deflection.

                                            Assumptions:
                                            - $H_1$: two-dimensional problem.
                                            - $H_2$: the gravity is neglected.
                                            - $H_3$: the beam deflection is very small compared
                                            to the length of the beam.
                                            - $H_3$: the beam is made of an homogeneous elastic material.

                                            Geometry parameters
                                            - $l$: beam length.
                                            - $a$: distance of the load P with respect to the left support.
                                            - $b$: distance of the load P with respect to the right support.
                                            - $d$: diameter of the beam section.

                                            Material
                                            - $E$: Young's modulus of elasticity.

                                            Loading
                                            - $P$: concentrated force.
                                            """,
                                            mathjax=True,
                                            className="lead",
                                            style={
                                                "textAlign": "left",
                                                "marginLeft": "auto",
                                                "marginRight": "auto",
                                                "font-size": "16px",
                                            },
                                        ),
                                    ]
                                )
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Grid(
                                    [
                                        dcc.Markdown(
                                            """
                                            **Solution**

                                            Deflection at any section for $0<x<a$:
                                            $$
                                            y = \\frac{Pbx}{6lEI} (l^2-x^2-b^2)
                                            $$

                                            Deflection at any section for $a<x<l$:
                                            $$
                                            y = \\frac{Pb}{6lEI} (\\frac{l}{b}(x-a)^3+(l^2-b^2)x-x^3)
                                            $$
                                            """,
                                            mathjax=True,
                                            className="lead",
                                            style={
                                                "textAlign": "left",
                                                "marginLeft": "auto",
                                                "marginRight": "auto",
                                                "font-size": "16px",
                                            },
                                        ),
                                        html.Br(),
                                        dmc.Card(
                                            [
                                                dmc.Image(
                                                    src="data:image/png;base64,{}".format(sketch.decode()),
                                                    style={
                                                        "width": "100%",
                                                        "border": "1px solid var(--mantine-color-default-border)",
                                                        "border-radius": "10px",
                                                        "padding": "10px",
                                                    },
                                                ),
                                                dmc.CardSection(
                                                    "Problem parametrization",
                                                    style={"text-align": "center"},
                                                ),
                                            ],
                                            style={"width": "50rem"},
                                        ),
                                    ]
                                )
                            ],
                            span=6,
                        ),
                    ]
                ),
            ],
            fluid=True,
            className="py-3",
        ),
        style={
            "border-radius": "10px",
            "padding": "20px",
            "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
        },
    )
