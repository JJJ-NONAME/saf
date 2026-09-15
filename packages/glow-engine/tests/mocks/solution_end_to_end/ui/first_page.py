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

"""Frontend of the first page."""

import logging
import os
import time

from dash import DiskcacheManager, dcc  # pyright: ignore[reportMissingTypeStubs]
from dash_extensions.enrich import Input, Output, State, Trigger, html  # pyright: ignore[reportMissingTypeStubs]
import diskcache  # pyright: ignore[reportMissingTypeStubs]
import httpx2

from ansys.saf.glow.client import callback
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution
from tests.mocks.solution_end_to_end.solution.simple_job_step import SimpleJobStep
from tests.mocks.solution_end_to_end.solution.transaction_verification_step import (
    TransactionVerificationStep,
)

logger = logging.getLogger(__name__)


def layout(step: TransactionVerificationStep):
    # Keep websockets out of this page to avoid creating websockets every time we load the page with Selenium in any
    # test.
    """Layout of the first step UI."""
    return html.Div(
        [
            html.H1("We are in First Page"),
            html.Div(
                [
                    dcc.Input(id="first-arg-inj", type="number"),
                    dcc.Input(id="second-arg-inj", type="number"),
                    html.Button("Calculate Injected", id="calculate_project_injected", n_clicks=0),
                    html.Div(id="result-inj", children=f"Result:{step.result}/PID:{os.getpid()}"),
                    dcc.Input(id="first-arg-inj-lr", type="number"),
                    dcc.Input(id="second-arg-inj-lr", type="number"),
                    html.Button(
                        "Calculate Injected Long Running",
                        id="calculate_project_injected_long_running",
                        n_clicks=0,
                    ),
                    html.Div(id="result-inj-lr", children=f"Result:{step.result}/PID:{os.getpid()}"),
                    dcc.Input(id="first-arg-inj-no-typehint", type="number"),
                    dcc.Input(id="second-arg-inj-no-typehint", type="number"),
                    html.Button(
                        "Calculate Injected NoTypeHint",
                        id="calculate_project_injected_no_typehint",
                        n_clicks=0,
                    ),
                    html.Div(id="result-inj-no-typehint", children=f"Result:{step.result}/PID:{os.getpid()}"),
                    dcc.Input(id="first-arg-inj-trig-before-pathname", type="number"),
                    dcc.Input(id="second-arg-inj-trig-before-pathname", type="number"),
                    html.Button(
                        "Calculate Injected Trigger Before Pathname",
                        id="calculate_project_injected_trigger_before_pathname",
                        n_clicks=0,
                    ),
                    html.Div(id="result-inj-trig-before-pathname", children=f"Result:{step.result}/PID:{os.getpid()}"),
                    dcc.Input(id="first-arg-inj-trig-after-pathname", type="number"),
                    dcc.Input(id="second-arg-inj-trig-after-pathname", type="number"),
                    html.Button(
                        "Calculate Injected Trigger After Pathname",
                        id="calculate_project_injected_trigger_after_pathname",
                        n_clicks=0,
                    ),
                    html.Div(id="result-inj-trig-after-pathname", children=f"Result:{step.result}/PID:{os.getpid()}"),
                    dcc.Input(id="third-arg-inj", type="number"),
                    dcc.Input(id="fourth-arg-inj", type="number"),
                    html.Button(
                        "Calculate Background New",
                        id="calculate_in_background_with_project_injected",
                        n_clicks=0,
                    ),
                    html.Div(id="result_background_new", children=f"Result:{step.result}/PID:{os.getpid()}"),
                    dcc.Input(id="third-arg-inj-lr", type="number"),
                    dcc.Input(id="fourth-arg-inj-lr", type="number"),
                    html.Button(
                        "Calculate Background Long Running",
                        id="calculate_in_background_with_project_injected_long_running",
                        n_clicks=0,
                    ),
                    html.Div(id="result_background_new_lr", children=f"Result:{step.result}/PID:{os.getpid()}"),
                ],
            ),
            html.Div(
                [
                    html.Button("Create File", id="create_file", n_clicks=0),
                    html.Div(id="created_file_check", children="File not yet created."),
                ],
            ),
            html.Div(
                [
                    html.Button("Read File", id="read_file", n_clicks=0),
                    html.Div(id="text_from_file", children="Text: Not read yet"),
                ],
            ),
            html.Div(
                [
                    html.Button("Read Entity", id="read_entity", n_clicks=0),
                    html.Div(id="text_from_entity", children="Text: Not read yet"),
                ],
            ),
            html.Div(
                [
                    html.Button("Read Lock Id", id="save_lock_id", n_clicks=0),
                    html.Div(id="lock_id", children="No lock id"),
                ],
            ),
            html.Div(
                [
                    html.Div(["Input: ", dcc.Input(id="my-input", value="", type="text")]),
                    html.Br(),
                    html.Div(id="my-output"),
                ],
            ),
            html.Div(
                [
                    html.Button("Read hps handle", id="read_hps_handle", n_clicks=0),
                    html.Div(id="handle_from_hps", children="No content yet"),
                ],
            ),
            html.Div(
                [
                    html.Button("Get Project HTTP Client", id="get_project_http_client", n_clicks=0),
                    html.Div(id="result", children="No result yet"),
                ],
            ),
        ],
    )


def _calculate(project: EndToEndSolution, field_1: int, field_2: int) -> str:
    step = project.steps.transaction_verification_step
    step.field_1 = field_1
    step.field_2 = field_2
    step.get_field_1_and_2_and_set_the_sum_in_result()
    return f"Result:{step.result}/PID:{os.getpid()}"


def _calculate_long_running(project: EndToEndSolution, field_1: int, field_2: int) -> str:
    step = project.steps.transaction_verification_step
    step.field_1 = field_1
    step.field_2 = field_2
    step.lr_get_field_1_and_2_and_set_the_sum_in_result().wait()
    return f"Result:{step.result}/PID:{os.getpid()}"


@callback(
    Output("result-inj", "children"),
    Input("calculate_project_injected", "n_clicks"),
    State("first-arg-inj", "value"),
    State("second-arg-inj", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def calculate_project_injected(n_clicks: int, first_arg: int, second_arg: int, project: EndToEndSolution):
    """Callback function to trigger the computation."""
    return _calculate(project, first_arg, second_arg)


@callback(
    Output("result-inj-lr", "children"),
    Input("calculate_project_injected_long_running", "n_clicks"),
    State("first-arg-inj-lr", "value"),
    State("second-arg-inj-lr", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def calculate_project_injected_long_running(n_clicks: int, first_arg: int, second_arg: int, project: EndToEndSolution):
    """Callback function to trigger the long running computation."""
    return _calculate_long_running(project, first_arg, second_arg)


@callback(
    Output("result-inj-trig-before-pathname", "children"),
    State("first-arg-inj-trig-before-pathname", "value"),
    Trigger("calculate_project_injected_trigger_before_pathname", "n_clicks"),
    State("second-arg-inj-trig-before-pathname", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def calculate_trigger_before_pathname(first_arg: int, second_arg: int, project: EndToEndSolution):
    """Callback function to trigger the computation."""
    return _calculate(project, first_arg, second_arg)


@callback(
    Output("result-inj-trig-after-pathname", "children"),
    State("first-arg-inj-trig-after-pathname", "value"),
    State("second-arg-inj-trig-after-pathname", "value"),
    State("url", "pathname"),
    Trigger("calculate_project_injected_trigger_after_pathname", "n_clicks"),
    prevent_initial_call=True,
)
def calculate_project_injected_trigger_after_pathname(first_arg: int, second_arg: int, project: EndToEndSolution):
    """Callback function to trigger the computation."""
    return _calculate(project, first_arg, second_arg)


@callback(
    Output("result-inj-no-typehint", "children"),
    Input("calculate_project_injected_no_typehint", "n_clicks"),
    State("first-arg-inj-no-typehint", "value"),
    State("second-arg-inj-no-typehint", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def calculate_project_injected_no_typehint(n_clicks, first_arg, second_arg, project: EndToEndSolution):  # type: ignore
    """Callback function to trigger the computation."""
    return _calculate(project, first_arg, second_arg)  # type: ignore


cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)


@callback(
    Output("result_background_new", "children"),
    Input("calculate_in_background_with_project_injected", "n_clicks"),
    State("third-arg-inj", "value"),
    State("fourth-arg-inj", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
    background=True,
    manager=background_callback_manager,
)
def calculate_in_background_with_project_injected(
    n_clicks: int,
    third_arg: int,
    fourth_arg: int,
    project: EndToEndSolution,
):
    """Background callback function to trigger the computation using diskcache as backend."""
    return _calculate(project, third_arg, fourth_arg)


@callback(
    Output("result_background_new_lr", "children"),
    Input("calculate_in_background_with_project_injected_long_running", "n_clicks"),
    State("third-arg-inj-lr", "value"),
    State("fourth-arg-inj-lr", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
    background=True,
    manager=background_callback_manager,
)
def calculate_in_background_with_project_injected_long_running(
    n_clicks: int,
    third_arg: int,
    fourth_arg: int,
    project: EndToEndSolution,
):
    """Background callback function to trigger the long running computation using diskcache as backend."""
    return _calculate_long_running(project, third_arg, fourth_arg)


@callback(
    Output("created_file_check", "children"),
    Input("create_file", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def create_text_file(n_clicks: int, project: EndToEndSolution):
    """Callback function to create and upload a text file."""
    storage_root = project.storage_scope.get_storage_root()
    text_file = storage_root / "myfile.txt"
    text_file.write_text("text from ui callback")
    project.steps.transaction_verification_step.file_entity = project.storage_scope.store(text_file)
    return "File Created!"


@callback(
    Output("text_from_file", "children"),
    Input("read_file", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def read_text_file(n_clicks: int, project: EndToEndSolution):
    """Callback function to read and display text from file."""
    file_entity = project.steps.transaction_verification_step.file_entity
    text_file = project.storage_scope.get_cached(file_entity)
    text_file_content = text_file.read_text()
    return f"Text: {text_file_content}"


@callback(
    Output("text_from_entity", "children"),
    Input("read_entity", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def read_entity_handle_with_project_injected(n_clicks: int, project: EndToEndSolution):
    """Callback function to read and display text from entity handle."""
    step = project.steps.transaction_verification_step
    text_file_content = project.storage_scope.get_text(step.file_entity)
    return f"Text: {text_file_content}"


@callback(
    Output("lock_id", "children"),
    Input("save_lock_id", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def save_lock_id(n_clicks: int, project: EndToEndSolution):
    """Save bdm lock id to verify that it is being deleted at the end of the callback."""
    step = project.steps.transaction_verification_step
    lock_id = project.storage_scope._lock_id  # pyright: ignore
    step.lock_id = lock_id
    response = httpx2.get(f"{project.url}/bdm-locks/{lock_id}")
    response.raise_for_status()
    return "ok"


@callback(
    Output(component_id="my-output", component_property="children"),
    Input(component_id="my-input", component_property="value"),
    State("url", "pathname"),
)
def update_text_content(input_value: str, project: EndToEndSolution):
    project.steps.transaction_verification_step.text_content = input_value
    return f"Value: {input_value}"


@callback(
    Output("handle_from_hps", "children"),
    Input("read_hps_handle", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def read_entity_handle_from_hps(n_clicks: int, project: EndToEndSolution):
    """Callback function to read and display text from entity handle."""
    step = project.steps.simple_job_step
    step.start_job().wait()
    step.query_hps()

    attempts = 0
    while step.step_state == SimpleJobStep.State.Calculating and attempts < 30:
        step.query_hps()
        time.sleep(1)
        attempts += 1

    step.fetch_file()
    result_path = project.storage_scope.get_cached(step.result_handle)
    return f"Text: {result_path.read_text()}"


@callback(
    Output("result", "children"),
    Input("get_project_http_client", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def return_project_http_client(n_clicks: int, project: EndToEndSolution):  # type: ignore
    return str(project._http_client)  # type: ignore
