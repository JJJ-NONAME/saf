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
User guide example for the Authenticator component.

Demonstrates a default authentication form and a fully customized form,
including a callback that controls the connect button's disabled state.
See the Authenticator page in the User Guide for the full reference documentation.
"""

# [imports-start]
from ansys.solutions.dash_super_components import Authenticator
from ansys.solutions.dash_super_components.utils.svg_icons import (
    IconNames,
    create_icon_span,
)
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
            html.Div(
                Authenticator(aio_id="default_authenticator_form"),
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                },
            )
        ]
    )


# [basic-layout-end]


# [advanced-layout-start]
def advanced_layout():
    authentification_form_items = [
        {
            "type": "TextInput",
            "id": "email",
            "properties": {
                "label": "Email",
                "placeholder": "Enter your email",
                "required": True,
                "leftSection": create_icon_span(
                    IconNames.IC_EMAIL, size_px=16, color="var(--mantine-color-text)"
                ),
            },
        },
        {
            "type": "TextInput",
            "id": "username",
            "properties": {
                "label": "Username",
                "placeholder": "Enter your username",
                "required": True,
                "leftSection": create_icon_span(
                    IconNames.MDI_USER, size_px=16, color="var(--mantine-color-text)"
                ),
            },
        },
        {
            "type": "PasswordInput",
            "id": "password",
            "properties": {
                "label": "Password",
                "placeholder": "Enter your password",
                "required": True,
                "leftSection": create_icon_span(
                    IconNames.MDI_SECURE, size_px=16, color="var(--mantine-color-text)"
                ),
            },
        },
        {
            "type": "Button",
            "id": "authenticate",
            "properties": {
                "children": "Authenticate",
                "leftSection": create_icon_span(
                    IconNames.HUGE_ROCKET, size_px=16, color="var(--mantine-color-text)"
                ),
            },
        },
    ]
    return html.Div(
        [
            html.Div(
                Authenticator(
                    aio_id="custom_authenticator_form",
                    items=authentification_form_items,
                    card_props={
                        "shadow": "xl",
                        "padding": "xl",
                    },
                ),
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                },
            )
        ]
    )


# [advanced-layout-end]


app.layout = dmc.MantineProvider(
    html.Div(
        [
            dmc.Title("Authenticator — User Guide Example", order=2, mb="md"),
            dmc.Text("Default form:", fw=600, mb="xs"),
            layout(),
            dmc.Divider(my="xl"),
            dmc.Text("Custom form:", fw=600, mb="xs"),
            advanced_layout(),
        ],
        style={
            "maxWidth": 600,
            "margin": "40px auto",
            "padding": "0 16px",
        },
    )
)


# [button-callback-start]
@callback(
    Output(Authenticator.ids.button("default_authenticator_form", "connect"), "disabled"),
    Input(Authenticator.ids.input("default_authenticator_form", "username"), "value"),
    Input(Authenticator.ids.password("default_authenticator_form", "password"), "value"),
)
def control_connect_button_selection(username, password):
    """Enable or disable connect button."""
    return not (username and password)


# [button-callback-end]


if __name__ == "__main__":
    app.run(debug=True)
