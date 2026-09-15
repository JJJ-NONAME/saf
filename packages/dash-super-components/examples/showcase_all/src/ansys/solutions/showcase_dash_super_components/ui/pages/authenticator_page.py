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


"""Frontend of the authentication page."""

from ansys.saf.glow.client import callback
from ansys.solutions.dash_super_components import Authenticator
from ansys.solutions.dash_super_components.utils.svg_icons import (
    IconNames,
    create_icon_span,
)
from dash_extensions.enrich import Input, Output, State, html
import dash_mantine_components as dmc

from ansys.solutions.showcase_dash_super_components.ui.components.page_template import (
    layout as page_layout,
)
from ansys.solutions.showcase_dash_super_components.ui.utilities.common_colors import CommonColors

INFO_CARD_TEXT = [
    ("Authenticator is a component that allows you to easily build authentication forms."),
    (
        "Note: Authenticator does not handle the authentication logic, it only provides "
        "the UI components."
    ),
    (
        "In the examples below, the page logic enables the buttons only if all the "
        "required fields are filled. Clicking the submit button then updates "
        "a status badge. In a real application, you would replace this with "
        "your authentication logic."
    ),
]

PAGE_TITLE = "Authenticator"


def layout() -> html.Div:
    """Layout of the authentication page page."""
    custom_authenticator_items = [
        {
            "type": "TextInput",
            "id": "email",
            "properties": {
                "label": "Email",
                "placeholder": "Enter your email",
                "required": True,
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
                    IconNames.MDI_USER, size_px=16, color=CommonColors.MANTINE_TEXT
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
                    IconNames.MDI_SECURE, size_px=16, color=CommonColors.MANTINE_TEXT
                ),
            },
        },
        {
            "type": "Button",
            "id": "authenticate",
            "properties": {
                "children": "Authenticate",
                "leftSection": create_icon_span(
                    IconNames.HUGE_ROCKET, size_px=16, color=CommonColors.MANTINE_TEXT
                ),
            },
        },
    ]

    main_content = html.Div(
        [
            dmc.Text("Example 1 - Default Authenticator", fw=700, size="xl"),
            dmc.Text(
                "Minimal usage relying on the built-in username and password "
                "fields. The submit button is enabled only once both fields "
                "are filled in.",
                size="sm",
                c=CommonColors.MANTINE_DIMMED,
                mb="sm",
            ),
            dmc.Space(h=10),
            dmc.Grid(
                [
                    dmc.GridCol(
                        children=[
                            Authenticator(aio_id="default_authenticator_form"),
                        ],
                        span="content",
                    ),
                    dmc.GridCol(
                        children=[
                            html.Div(
                                dmc.Badge(
                                    id="default_authenticator_status",
                                    size="xl",
                                    radius="xl",
                                ),
                                style={
                                    "display": "flex",
                                    "justifyContent": "center",
                                    "alignItems": "center",
                                    "height": "100%",
                                },
                            ),
                        ],
                        span="content",
                    ),
                ],
                gutter="md",
                align="stretch",
            ),
            dmc.Space(h=60),
            dmc.Text("Example 2 - Custom Authenticator", fw=700, size="xl"),
            dmc.Text(
                "Advanced usage with a fully custom item list: email, username, "
                "and password fields each decorated with a left-section icon, "
                "plus a custom authenticate button. All three fields must be "
                "filled before the button is enabled.",
                size="sm",
                c=CommonColors.MANTINE_DIMMED,
                mb="sm",
            ),
            dmc.Space(h=10),
            dmc.Grid(
                [
                    dmc.GridCol(
                        children=[
                            Authenticator(
                                aio_id="custom_authenticator_form", items=custom_authenticator_items
                            ),
                        ],
                        span="content",
                    ),
                    dmc.GridCol(
                        children=[
                            html.Div(
                                dmc.Badge(
                                    id="custom_authenticator_status",
                                    size="xl",
                                    radius="xl",
                                ),
                                style={
                                    "display": "flex",
                                    "justifyContent": "center",
                                    "alignItems": "center",
                                    "height": "100%",
                                },
                            ),
                        ],
                        span="content",
                    ),
                ],
                gutter="md",
                align="stretch",
            ),
        ],
        style={"maxWidth": "800px"},
    )

    return page_layout(
        page_title=PAGE_TITLE,
        info_card_text=INFO_CARD_TEXT,
        main_content=main_content,
    )


@callback(
    Output(Authenticator.ids.button("default_authenticator_form", "connect"), "disabled"),
    Input(Authenticator.ids.input("default_authenticator_form", "username"), "value"),
    Input(Authenticator.ids.password("default_authenticator_form", "password"), "value"),
)
def control_connect_button_selection_default_form(username: str, password: str) -> bool:
    """Enable or disable connect button."""
    return not (username and password)


@callback(
    Output(Authenticator.ids.button("custom_authenticator_form", "authenticate"), "disabled"),
    Input(Authenticator.ids.input("custom_authenticator_form", "email"), "value"),
    Input(Authenticator.ids.input("custom_authenticator_form", "username"), "value"),
    Input(Authenticator.ids.password("custom_authenticator_form", "password"), "value"),
)
def control_connect_button_selection_custom_form(
    email: str,
    username: str,
    password: str,
) -> bool:
    """Enable or disable connect button."""
    return not (email and username and password)


@callback(
    Output("default_authenticator_status", "children"),
    Output("default_authenticator_status", "color"),
    Output("default_authenticator_status", "variant"),
    Input(Authenticator.ids.button("default_authenticator_form", "connect"), "n_clicks"),
    State(Authenticator.ids.input("default_authenticator_form", "username"), "value"),
    State(Authenticator.ids.password("default_authenticator_form", "password"), "value"),
)
def update_authentication_status_default_form(
    n_clicks: int, username: str, password: str
) -> tuple[str, str, str]:
    """Update authentication status."""
    # In a real application, you would replace this with your authentication logic.
    # Here, we just check if the button has been clicked.
    if n_clicks and n_clicks > 0:
        return "Connected", CommonColors.GREEN, "filled"
    return "Not connected", CommonColors.MANTINE_PRIMARY_COLOR, "outline"


@callback(
    Output("custom_authenticator_status", "children"),
    Output("custom_authenticator_status", "color"),
    Output("custom_authenticator_status", "variant"),
    Input(Authenticator.ids.button("custom_authenticator_form", "authenticate"), "n_clicks"),
    State(Authenticator.ids.input("custom_authenticator_form", "email"), "value"),
    State(Authenticator.ids.input("custom_authenticator_form", "username"), "value"),
    State(Authenticator.ids.password("custom_authenticator_form", "password"), "value"),
)
def update_authentication_status_custom_form(
    n_clicks: int, email: str, username: str, password: str
) -> tuple[str, str, str]:
    """Update authentication status."""
    # In a real application, you would replace this with your authentication logic.
    # Here, we just check if the button has been clicked.
    if n_clicks and n_clicks > 0:
        return "Authenticated", CommonColors.GREEN, "filled"
    return "Not authenticated", CommonColors.MANTINE_PRIMARY_COLOR, "outline"
