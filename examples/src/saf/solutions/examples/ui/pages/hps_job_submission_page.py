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

# ©2026, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""user interface for the hps job submission step."""

import json
import logging

from ansys.saf.glow.client import DashClient, callback
from ansys.saf.glow.solution import MethodStatus
import dash
from dash_extensions.enrich import Input, Output, State, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from saf.solutions.examples.solution.definition import ExamplesSolution

logger = logging.getLogger(__name__)

dash.register_page(
    __name__,
    name="HPS Job Submission",
    path_template="/projects/<project_id>/hps-job-submission",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout(project: ExamplesSolution) -> html.Div:
    """Layout of the HPS job submission step page."""
    step = project.steps.hps_job_submission_step
    running = step.get_method_state("run_job").status == MethodStatus.Running
    return html.Div(
        [
            html.H1(
                "HPS Job Submission Step", className="display-3", style={"font-size": "40px", "font-weight": "bold"}
            ),
            dmc.Blockquote(
                "Compute the sum of two numbers by submitting a job to HPS.  This example step demonstrates (a) how"
                + " to use different mechanisms for transferring data to and from HPS and (b) how to display HPS job"
                + " status using SAF GLOW events including termination events.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            dmc.Space(h=20),
            dmc.NumberInput(
                label="First Argument",
                id="hps-first-arg",
                value=step.first_arg,
                placeholder="Enter first argument",
                required=True,
                style={"width": "40%", "display": "inline-block", "marginLeft": "30%"},
                disabled=running,
            ),
            dmc.Space(h=20),
            dmc.NumberInput(
                label="Second Argument",
                id="hps-second-arg",
                value=step.second_arg,
                placeholder="Enter second argument",
                required=True,
                style={"width": "40%", "display": "inline-block", "marginLeft": "30%"},
                disabled=running,
            ),
            dmc.Space(h=20),
            dmc.Button(
                "Calculate",
                id="hps-calculate",
                radius="sm",
                style={
                    "font-size": "16px",
                    "width": "40%",
                    "display": "inline-block",
                    "marginLeft": "30%",
                    "background-color": "#2790F1",
                },
                disabled=running,
                leftSection=DashIconify(icon="streamline:startup-solid"),
            ),
            dmc.Space(h=20),
            dmc.Text(
                "Status", style={"fontWeight": 700, "width": "40%", "display": "inline-block", "marginLeft": "30%"}
            ),
            dmc.Text(
                step.status,
                id="hps-progress",
                style={"width": "40%", "display": "inline-block", "marginLeft": "30%"},
            ),
            dmc.Space(h=20),
            dmc.Text(
                "Result", style={"fontWeight": 700, "width": "40%", "display": "inline-block", "marginLeft": "30%"}
            ),
            dmc.Text(
                str(step.result) if step.result is not None else "",
                id="hps-result",
                style={"width": "40%", "display": "inline-block", "marginLeft": "30%"},
            ),
            DashClient.create_event_listener(step, stream_name="status", id="hps-status_ws"),
            DashClient.create_event_listener(step, stream_name="run-job", id="hps-termination_ws"),
        ],
        style={"paddingLeft": "20px"},
    )


@callback(
    Output("hps-progress", "children", allow_duplicate=True),
    Output("hps-result", "children", allow_duplicate=True),
    Input("hps-first-arg", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def bind_first_arg(first_arg, project: ExamplesSolution) -> dmc.Text | html.Div:
    """Transfer the newly entered value of the 1st argument into the step data model.

    Resets the other step data model fields.
    """
    step = project.steps.hps_job_submission_step
    step.reset()
    if first_arg != "":
        step.first_arg = float(first_arg)
    return step.status, ""


@callback(
    Output("hps-progress", "children", allow_duplicate=True),
    Output("hps-result", "children", allow_duplicate=True),
    Input("hps-second-arg", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def bind_second_arg(second_arg, project: ExamplesSolution) -> dmc.Text | html.Div:
    """Transfer the newly entered value of the 2nd argument into the step data model.

    Resets the other step data model fields.
    """
    step = project.steps.hps_job_submission_step
    step.reset()
    if second_arg != "":
        step.second_arg = float(second_arg)
    return step.status, ""


@callback(
    Output("hps-progress", "children", allow_duplicate=True),
    Output("hps-calculate", "disabled", allow_duplicate=True),
    Output("hps-first-arg", "disabled", allow_duplicate=True),
    Output("hps-second-arg", "disabled", allow_duplicate=True),
    Output("hps-result", "children", allow_duplicate=True),
    Input("hps-calculate", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def calculate(n_clicks: int, project: ExamplesSolution) -> dmc.Text | html.Div:
    """Trigger the job submission."""
    step = project.steps.hps_job_submission_step
    step.status = "Starting calculation"
    step.write_persisted_inputs()
    step.run_job()
    return step.status, True, True, True, ""


@callback(
    Output("hps-progress", "children", allow_duplicate=True),
    Output("hps-calculate", "disabled", allow_duplicate=True),
    Output("hps-first-arg", "disabled", allow_duplicate=True),
    Output("hps-second-arg", "disabled", allow_duplicate=True),
    Output("hps-result", "children", allow_duplicate=True),
    Input("hps-status_ws", "message"),
    prevent_initial_call=True,
)
def update_status(message) -> dmc.Text | html.Div:
    """Triggered when a status event is received from HPS.

    This method updates the status displayed on the page.
    """
    message_str = json.loads(message["data"])
    return message_str, True, True, True, ""


@callback(
    Output("hps-progress", "children", allow_duplicate=True),
    Output("hps-calculate", "disabled", allow_duplicate=True),
    Output("hps-first-arg", "disabled", allow_duplicate=True),
    Output("hps-second-arg", "disabled", allow_duplicate=True),
    Output("hps-result", "children", allow_duplicate=True),
    Input("hps-termination_ws", "message"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def termination(message, project: ExamplesSolution) -> dmc.Text | html.Div:
    """Triggered when the run_job transaction method completes.

    This method re-enables the input fields of the form and displays the result of the job.
    """
    step = project.steps.hps_job_submission_step
    return step.status, False, False, False, str(step.result) if step.result is not None else ""
