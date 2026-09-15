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


"""Initialization of the frontend layout across all the steps."""

import webbrowser

from ansys.saf.glow.client import DashClient, Deployment, callback
from ansys.solutions.dash_super_components import Tree
from ansys.solutions.dash_super_components.utils.svg_icons import (
    IconNames,
    create_base64_svg_src,
    create_icon_span,
)

try:
    # dash >=3.2.0
    from dash import NoUpdate
except ImportError:
    # dash >=2.18.2, <3.2.0
    from dash._callback import NoUpdate  # pyright: ignore[reportPrivateImportUsage]

from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_extensions.enrich import Input, Output, callback_context, dcc, html, no_update
import dash_mantine_components as dmc

from ansys.solutions.showcase_dash_super_components.solution.definition import (
    SuperComponentsExamplesSolution,
)
from ansys.solutions.showcase_dash_super_components.ui.pages import (
    about_page,
    authenticator_page,
    dual_input_range_slider_page,
    folder_selector_page,
    input_form_page,
    input_row_array_page,
    logs_supervisor_page,
    transaction_method_status_badge_page,
    transaction_supervisor_page,
    tree_page,
)
from ansys.solutions.showcase_dash_super_components.ui.utilities.common_colors import CommonColors

page_items = [
    {
        "id": "about_page",
        "text": "About",
        "icon": create_base64_svg_src(IconNames.MATERIAL_HOME),
        "expanded": True,
        "disabled": False,
        "description": "Overview of the solution.",
    },
    {
        "id": "authenticator_page",
        "text": "Authenticator",
        "icon": create_base64_svg_src(IconNames.ICON_PARK_PERMISSIONS),
        "expanded": True,
        "disabled": False,
        "description": "Authentication form.",
    },
    {
        "id": "dual_input_range_slider_page",
        "text": "Dual Input Range Slider",
        "icon": create_base64_svg_src(IconNames.MDI_SLIDER),
        "expanded": True,
        "disabled": False,
        "description": "Range slider with number inputs.",
    },
    {
        "id": "folder_selector_page",
        "text": "Folder Selector",
        "icon": create_base64_svg_src(IconNames.MDI_FOLDER_SEARCH),
        "expanded": True,
        "disabled": False,
        "description": "Open folder dialog.",
    },
    {
        "id": "input_form_page",
        "text": "Input Form",
        "icon": create_base64_svg_src(IconNames.MDI_FORM_OUTLINE),
        "expanded": True,
        "disabled": False,
        "description": "Enable quick input form crafting.",
    },
    {
        "id": "input_row_array_page",
        "text": "Input Row Array",
        "icon": create_base64_svg_src(IconNames.MATERIAL_LIST),
        "expanded": True,
        "disabled": False,
        "description": "Configurable input row.",
    },
    {
        "id": "logs_supervisor_page",
        "text": "Logs Supervisor",
        "icon": create_base64_svg_src(IconNames.MDI_TABLE_EYE),
        "expanded": True,
        "disabled": False,
        "description": "Collect and display process logs.",
    },
    {
        "id": "transaction_method_status_badge_page",
        "text": "Transaction Method Status Badge",
        "icon": create_base64_svg_src(IconNames.FLUENT_DATA_SUNBURST),
        "expanded": True,
        "disabled": False,
        "description": "Monitoring of a transaction method.",
    },
    {
        "id": "transaction_supervisor_page",
        "text": "Transaction Supervisor",
        "icon": create_base64_svg_src(IconNames.EOS_MONITORING),
        "expanded": True,
        "disabled": False,
        "description": "Tracking the status of a transaction method.",
    },
    {
        "id": "tree_page",
        "text": "Tree",
        "icon": create_base64_svg_src(IconNames.MDI_FILE_TREE),
        "expanded": True,
        "disabled": False,
        "description": "Expand and collapse tree structures.",
    },
]


header = dmc.AppShellHeader(
    dmc.Flex(
        [
            dmc.Image(
                id="logo-image",
                src=r"/assets/logos/placeholder_logo_light.png",
                w=350,
                darkHidden=True,
            ),
            dmc.Image(
                id="logo-image-dark",
                src=r"/assets/logos/placeholder_logo_dark.png",
                w=350,
                lightHidden=True,
            ),
            dmc.Group(
                [
                    dmc.Text(
                        "Project name:",
                        id="project-name",
                        size="sm",
                        style={"fontSize": "16px", "color": CommonColors.MANTINE_TEXT},
                    ),
                    dmc.Space(w=10),
                    dmc.ColorSchemeToggle(
                        id="color-scheme-toggle",
                        lightIcon=create_icon_span(
                            IconNames.RADIX_SUN, size_px=36, color=CommonColors.MANTINE_TEXT
                        ),
                        darkIcon=create_icon_span(
                            IconNames.RADIX_MOON, size_px=36, color=CommonColors.MANTINE_TEXT
                        ),
                        size="lg",
                        m="xl",
                    ),
                    dmc.ActionIcon(
                        create_icon_span(IconNames.TEENYICONS_DOC_SOLID, size_px=36),
                        id="access-super-components-docs",
                        variant="transparent",
                        style={"color": CommonColors.MANTINE_TEXT},
                        size=36,  # type: ignore
                    ),
                    dbc.Popover(
                        "Get access to the Super Components for Dash Documentation.",
                        target="access-super-components-docs",
                        body=True,
                        trigger="hover",
                    ),
                    html.Div(id="return-to-portal"),
                ],
                gap=10,
            ),
        ],
        justify="space-between",
        align="center",
        direction="row",
        wrap="wrap",
        h="100%",
        px="md",
    )
)


navbar = dmc.AppShellNavbar(
    Tree(
        aio_id="navigation_tree",
        items=page_items,
        selected_item="about_page",
    ),
    id="navbar-content",
    p="md",
)


main_layout = dmc.AppShellMain(
    dmc.Box(
        id="page-content",
        style={
            "paddingRight": "0.7%",
            "paddingLeft": "0.7%",
            "paddingBottom": "1.5rem",
            "minHeight": "100vh",
        },
    ),
)


layout = dmc.MantineProvider(
    [
        dmc.NotificationContainer(
            id="notification-container",
            position="top-right",
            notificationMaxHeight=400,
        ),
        dmc.AppShell(
            [
                header,
                navbar,
                main_layout,
            ],
            header={"height": 70},
            navbar={
                "width": 300,
                "breakpoint": "sm",
                "collapsed": {"mobile": True},
            },
        ),
        dcc.Location(id="url", refresh=False),
        html.Div(
            id="alerts-container",
            style={"position": "fixed", "top": 90, "right": 10, "width": 350, "zIndex": 1000},
        ),
    ],
    id="mantine-provider",
    defaultColorScheme="light",
    theme={
        "primaryColor": "blue",
    },
)


@callback(
    Output("return-to-portal", "children"),
    Input("url", "pathname"),
)
def return_to_portal(pathname: str) -> list[html.A]:
    """Display Solution Portal when back-to-portal button gets selected."""
    portal_ui_url = DashClient.get_portal_ui_url()

    if portal_ui_url is None:
        return []

    popover_text = (
        "Back to Projects"
        if DashClient.get_deployment_type() == Deployment.Desktop
        else "Back to Portal"
    )

    return [
        html.A(
            [
                dmc.ActionIcon(
                    create_icon_span(
                        IconNames.CARBON_RETURN, size_px=36, color=CommonColors.MANTINE_TEXT
                    ),
                    id="back-to-projects-icon",
                    variant="transparent",
                ),
                dbc.Popover(
                    popover_text,
                    target="back-to-projects-icon",
                    body=True,
                    trigger="hover",
                ),
            ],
            href=portal_ui_url,
        )
    ]


@callback(
    Output("project-name", "children"),
    Input("url", "pathname"),
)
def display_project_name(project: SuperComponentsExamplesSolution) -> str:
    """Display current project name."""
    return f"Project Name: {project.project_display_name}"


@callback(
    Output("access-super-components-docs", "children"),
    Input("access-super-components-docs", "n_clicks"),
    prevent_initial_call=True,
)
def access_super_components_docs(n_clicks: int) -> NoUpdate:
    """Open the Super Components for Dash Documentation home page in the web browser."""
    webbrowser.open_new("https://super-components-for-dash.docs.solutions.ansys.com/")
    return no_update


@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input(Tree.ids.selected_item("navigation_tree"), "data"),
    prevent_initial_call=True,
)
def display_page(
    project: SuperComponentsExamplesSolution, selected_item: dict[str, str] | None
) -> html.Div:
    """Display page content."""
    triggered_id = callback_context.triggered_id

    if triggered_id == "url" or not selected_item:
        return about_page.layout()
    elif triggered_id == Tree.ids.selected_item("navigation_tree"):
        page_id = Tree.ids.get_index_from_navlink_item_id(selected_item)
        page_map = {
            "about_page": lambda: about_page.layout(),
            "input_form_page": lambda: input_form_page.layout(project.steps.simple_step),
            "dual_input_range_slider_page": lambda: dual_input_range_slider_page.layout(),
            "folder_selector_page": lambda: folder_selector_page.layout(),
            "authenticator_page": lambda: authenticator_page.layout(),
            "input_row_array_page": lambda: input_row_array_page.layout(),
            "tree_page": lambda: tree_page.layout(project.steps.simple_step),
            "transaction_supervisor_page": lambda: transaction_supervisor_page.layout(
                project.steps.simple_step
            ),
            "logs_supervisor_page": lambda: logs_supervisor_page.layout(project.steps.simple_step),
            "transaction_method_status_badge_page": lambda: (
                transaction_method_status_badge_page.layout(
                    project.steps.simple_step,
                )
            ),
        }
        page_factory = page_map.get(page_id)
        if page_factory is not None:
            return page_factory()
        else:
            raise ValueError(f"Unknown page selection: {page_id}")
    raise PreventUpdate
