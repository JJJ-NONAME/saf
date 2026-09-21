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


"""Application."""

import os

from ansys.saf.glow.client import callback
from ansys.solutions.dash_super_components import (
    InputForm,
    LogsSupervisor,
    add_super_components_assets,
)

# [imports-status-badge-start]
from ansys.solutions.dash_super_components import TransactionMethodStatusBadge
# [imports-status-badge-end]

# [imports-supervisor-start]
from ansys.solutions.dash_super_components import TransactionSupervisor
# [imports-supervisor-end]

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import (
    DashProxy,
    Input,
    MultiplexerTransform,
    Output,
    State,
    TriggerTransform,
    ctx,
    dcc,
    html,
)
import dash_mantine_components as dmc

from ansys.solutions.super_components_with_saf.solution.definition import (
    SuperComponentsWithSAFSolution,
)
from ansys.solutions.super_components_with_saf.solution.my_step import MyStep

app = DashProxy(
    __name__,
    suppress_callback_exceptions=True,
    transforms=[TriggerTransform(), MultiplexerTransform()],
    requests_pathname_prefix=f"{os.getenv('GLOW_UI_PATH_PREFIX', '/')}",
    # External scripts required for LogsSupervisor component:
    # This script contains custom cell and no rows text renderers for Dash AG Grid
    external_scripts=["/super-components/dashAgGridComponentFunctions.js"],
)

# Register Flask endpoint to serve super-components assets (required for LogsSupervisor)
add_super_components_assets(app)


############ Logs Supervisor Example ############


# [layout-logs-supervisor-start]
def layout_logs_supervisor(step: MyStep) -> html.Div:
    """Layout of the basic logs supervisor example."""
    return html.Div(
        [
            LogsSupervisor(
                log_file=step.get_entity_url("logfile"),
                log_format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
                aio_id="logs-supervisor",
            ),
        ]
    )


# [layout-logs-supervisor-end]


@callback(
    Output("logs-supervisor-container", "children"),
    Input("url", "pathname"),
)
def initialize_logs_supervisor(project: SuperComponentsWithSAFSolution) -> html.Div:
    """Initialize the logs supervisor on page load."""
    return layout_logs_supervisor(project.steps.my_step)


# [generate-logs-and-monitor-start]
@callback(
    Output(LogsSupervisor.ids.activate_monitoring("logs-supervisor"), "data"),
    Input("generate-logs-button", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def generate_logs_and_start_monitoring(
    n_clicks: int, project: SuperComponentsWithSAFSolution
) -> bool:
    """Trigger the generate_random_logs transaction and activate the basic supervisor."""
    if not ctx.triggered_id or not n_clicks:
        raise PreventUpdate
    step = project.steps.my_step
    step.generate_random_logs()
    return True


# [generate-logs-and-monitor-end]


############ Transaction Method Status Badge Example ############


# [layout-status-badge-start]
def layout_transaction_method_status_badge():
    return html.Div(
        [
            dmc.Button(
                "Run method",
                id="run_method_button",
            ),
            dmc.Space(h=16),
            html.Div(
                id="transaction-method-status-badge-container",
                style={"width": "200px"},
            ),
        ]
    )


# [layout-status-badge-end]


def layout_transaction_method_status_badge_advanced():
    return html.Div(
        [
            dmc.Button(
                "Run another method",
                id="run_method_button_advanced",
            ),
            dmc.Space(h=16),
            html.Div(
                id="transaction-method-status-badge-container-advanced",
                style={"width": "200px"},
            ),
        ]
    )


# [add-status-badge-callback-start]
@callback(
    Output("transaction-method-status-badge-container", "children"),
    Input("url", "pathname"),
)
def initialize_transaction_method_status_badge(
    project: SuperComponentsWithSAFSolution,
) -> TransactionMethodStatusBadge:
    """Initialize the transaction method status badge."""
    return TransactionMethodStatusBadge(
        url=project.url,
        step_name="my_step",
        method_name="my_method",
        aio_id="my_method_badge",
    )


# [add-status-badge-callback-end]


# [add-status-badge-advanced-callback-start]
@callback(
    Output("transaction-method-status-badge-container-advanced", "children"),
    Input("url", "pathname"),
)
def initialize_transaction_method_status_badge_advanced(
    project: SuperComponentsWithSAFSolution,
) -> TransactionMethodStatusBadge:
    """Initialize the transaction method status badge."""
    return TransactionMethodStatusBadge(
        url=project.url,
        step_name="my_step",
        method_name="my_method_2",
        aio_id="my_method_badge_advanced",
        label_props={"children": "Method Status:"},
        interval_props={"interval": 2000},
        badge_props={"size": "md"},
        auto_mode=False,
    )


# [add-status-badge-advanced-callback-end]


# [activate-status-badge-callback-start]
@callback(
    Output(
        TransactionMethodStatusBadge.ids.activate_monitoring("my_method_badge"),
        "data",
    ),
    Input("run_method_button", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def start_method_and_monitor(n_clicks: int, project: SuperComponentsWithSAFSolution) -> bool:
    """Start the method and activate badge monitoring."""
    if n_clicks:
        project.steps.my_step.my_method()
        return True  # Activate monitoring
    raise PreventUpdate


# [activate-status-badge-callback-end]


@callback(
    Output(
        TransactionMethodStatusBadge.ids.activate_monitoring("my_method_badge_advanced"),
        "data",
    ),
    Input("run_method_button_advanced", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def start_method_and_monitor_advanced(
    n_clicks: int, project: SuperComponentsWithSAFSolution
) -> bool:
    """Activate badge monitoring for the advanced badge."""
    if n_clicks:
        project.steps.my_step.my_method_2()
        return True  # Activate monitoring
    raise PreventUpdate


############ Transaction Supervisor Example ############


# [layout-supervisor-start]
def layout_transaction_supervisor():
    return html.Div(
        [
            dmc.Button(
                "Run method",
                id="run_method_button_supervisor",
            ),
            dmc.Space(h=16),
            html.Div(id="transaction_supervisor_container"),
        ]
    )


# [layout-supervisor-end]


def layout_transaction_supervisor_advanced():
    return html.Div(
        [
            dmc.Button(
                "Run another method",
                id="run_method_button_supervisor_advanced",
            ),
            dmc.Space(h=16),
            html.Div(id="transaction_supervisor_container_advanced"),
        ]
    )


# [add-transaction-supervisor-callback-start]
@callback(
    Output("transaction_supervisor_container", "children"),
    Input("url", "pathname"),
)
def initialize_transaction_supervisor(
    project: SuperComponentsWithSAFSolution,
) -> TransactionSupervisor:
    """Initialize the transaction supervisor on page load."""
    return TransactionSupervisor(
        aio_id="transaction_supervisor",
        url=project.url,
        step_name="my_step",
        method_name="my_method_synchronous",
    )


# [add-transaction-supervisor-callback-end]


# [add-transaction-supervisor-advanced-callback-start]
@callback(
    Output("transaction_supervisor_container_advanced", "children"),
    Input("url", "pathname"),
)
def initialize_transaction_supervisor_advanced(
    project: SuperComponentsWithSAFSolution,
) -> TransactionSupervisor:
    """Initialize the transaction supervisor on page load."""
    return TransactionSupervisor(
        aio_id="transaction_supervisor_advanced",
        title="Transaction Supervisor",
        url=project.url,
        step_name="my_step",
        method_name="my_method_synchronous_2",
        width=500,
        show=True,
        orientation="vertical",
        title_font_size="20px",
        font_size="16px",
    )


# [add-transaction-supervisor-advanced-callback-end]


# [activate-transaction-supervision-callback-start]
@callback(
    Output(TransactionSupervisor.ids.activate_monitoring("transaction_supervisor"), "data"),
    Input("run_method_button_supervisor", "n_clicks"),
    prevent_initial_call=True,
)
def monitor_method(n_clicks):
    """Activate monitoring when the method is triggered."""
    if n_clicks:
        return True
    raise PreventUpdate


@callback(
    Input("run_method_button_supervisor", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def run_method(n_clicks: int, project: SuperComponentsWithSAFSolution) -> str:
    """Run the method and return its output."""
    if n_clicks:
        step = project.steps.my_step
        step.my_method_synchronous()
    raise PreventUpdate


# [activate-transaction-supervision-callback-end]


@callback(
    Output(
        TransactionSupervisor.ids.activate_monitoring("transaction_supervisor_advanced"), "data"
    ),
    Input("run_method_button_supervisor_advanced", "n_clicks"),
    prevent_initial_call=True,
)
def monitor_method_advanced(n_clicks):
    """Activate monitoring when the method is triggered."""
    if n_clicks:
        return True
    raise PreventUpdate


@callback(
    Input("run_method_button_supervisor_advanced", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def run_method_advanced(n_clicks: int, project: SuperComponentsWithSAFSolution) -> str:
    """Run the method and return its output."""
    if n_clicks:
        step = project.steps.my_step
        step.my_method_synchronous_2()
    raise PreventUpdate


############ Input Form Example ############


# [layout-input-form-start]
def layout_input_form(step: MyStep) -> InputForm:
    """Layout of the InputForm backend-persistence example."""
    return InputForm(
        [
            {
                "id": "project-row",
                "label": "Project Name",
                "fields": [
                    {
                        "type": "TextInput",
                        "id": "project-name",
                        "placeholder": "Enter project name",
                        "value": step.project_name,
                    }
                ],
            },
            {
                "id": "iterations-row",
                "label": "Max Iterations",
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "max-iterations",
                        "min": 1,
                        "max": 10000,
                        "value": step.max_iterations,
                    }
                ],
            },
        ],
        aio_id="backend-form",
        title="Project Configuration",
        columns=["label", "fields"],
    )


# [layout-input-form-end]


@callback(
    Output("input-form-container", "children"),
    Input("url", "pathname"),
)
def initialize_input_form(project: SuperComponentsWithSAFSolution) -> InputForm:
    """Initialize the InputForm with values from the backend on page load."""
    return layout_input_form(project.steps.my_step)


# [save-input-form-start]
@callback(
    Input("save-input-form-btn", "n_clicks"),
    State(
        InputForm.ids.field("backend-form", "TextInput", "project-name", "project-row"),
        "value",
    ),
    State(
        InputForm.ids.field("backend-form", "NumberInput", "max-iterations", "iterations-row"),
        "value",
    ),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def save_input_form(
    n_clicks: int,
    project_name: str,
    max_iterations: int,
    project: SuperComponentsWithSAFSolution,
) -> None:
    """Write InputForm values to the backend solution model."""
    if not n_clicks:
        raise PreventUpdate
    step = project.steps.my_step
    step.project_name = project_name or ""
    step.max_iterations = max_iterations or 100


# [save-input-form-end]


app.layout = dmc.MantineProvider(
    [
        dmc.NotificationContainer(
            id="notification-container",
            position="top-right",
            notificationMaxHeight=400,
        ),
        html.Div(
            [
                dcc.Location("url", refresh=False),
                dmc.Title("Logs Supervisor — User Guide Example", order=2, mb="md"),
                dmc.Text(
                    "Click 'Generate logs and start monitoring' to run a transaction that "
                    "generates logs and watch the Logs Supervisor display them in real time.",
                    c="dimmed",
                    mb="xl",
                ),
                dmc.Button(
                    "Generate Logs",
                    id="generate-logs-button",
                ),
                dmc.Space(h=16),
                html.Div(
                    id="logs-supervisor-container",
                ),
                dmc.Divider(my="xl"),
                dmc.Space(h=40),
                dmc.Title("Transaction Method Status Badge — User Guide Example", order=2, mb="md"),
                dmc.Text(
                    "Click 'Run method' to run a transaction and watch the badge update.",
                    c="dimmed",
                    mb="xl",
                ),
                layout_transaction_method_status_badge(),
                dmc.Divider(my="xl"),
                dmc.Text(
                    "Advanced Configuration. Click 'Run another method' to run a transaction and "
                    "watch the badge update.",
                    c="dimmed",
                    mb="md",
                ),
                layout_transaction_method_status_badge_advanced(),
                dmc.Divider(my="xl"),
                dmc.Space(h=40),
                dmc.Title("Transaction Supervisor - User Guide Example", order=2, mb="md"),
                dmc.Text(
                    "Click 'Run method' to run a transaction and watch the supervisor update.",
                    c="dimmed",
                    mb="md",
                ),
                layout_transaction_supervisor(),
                dmc.Divider(my="xl"),
                dmc.Text(
                    "Advanced Configuration. Click 'Run another method' to run a transaction and "
                    "watch the supervisor update.",
                    c="dimmed",
                    mb="md",
                ),
                layout_transaction_supervisor_advanced(),
                dmc.Divider(my="xl"),
                dmc.Space(h=40),
                dmc.Title("Input Form — User Guide Example", order=2, mb="md"),
                dmc.Text(
                    "Edit the fields and click 'Save to backend' to persist values on the server. "
                    "Switch projects and return to verify that the saved values are restored on "
                    "reload.",
                    c="dimmed",
                    mb="xl",
                ),
                html.Div(id="input-form-container"),
                dmc.Space(h=12),
                dmc.Button("Save to backend", id="save-input-form-btn"),
            ],
            style={"maxWidth": 800, "margin": "40px auto", "padding": "0 16px"},
        ),
    ]
)
