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

from typing import Any

from dash_extensions.enrich import Input, Output, State, Trigger  # type: ignore

from ansys.saf.glow.client import callback
from tests.mocks.solution_with_ui.solution.definition import MySolution


@callback(
    Output("result", "children"),
    Input("calculate", "n_clicks"),
    State("first-arg", "value"),
    State("second-arg", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def return_project(n_clicks: int, first_arg: int, second_arg: int, project: MySolution):
    return f"{project.url=}"


@callback(
    Output("result", "children"),
    Output("result", "children"),
    Output("result", "children"),
    Output("result", "children"),
    Output("result", "children"),
    Input("calculate", "n_clicks"),
    State("first-arg", "value"),
    State("url", "pathname"),
    State("second-arg", "value"),
)
def return_project_many_outputs_project_in_middle(n_clicks: int, first_arg: int, project: MySolution, second_arg: int):
    return f"{project.url=}"


@callback(
    State("url", "pathname"),
    Input("calculate", "n_clicks"),
    State("first-arg", "value"),
    State("second-arg", "value"),
)
def return_project_no_output_project_first(project: MySolution, n_clicks: int, first_arg: int, second_arg: int):
    return f"{project.url=}"


@callback(
    Output("result", "children"),
    Input("calculate", "n_clicks"),
    State("first-arg", "value"),
    State("second-arg", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def return_pathname(n_clicks: int, first_arg: int, second_arg: int, pathname: str):
    return pathname


@callback(
    Output("result", "children"),
    Input("calculate", "n_clicks"),
    State("first-arg", "value"),
    State("second-arg", "value"),
    prevent_initial_call=True,
)
def no_pathname(n_clicks: int, first_arg: int, second_arg: int): ...


@callback(
    [
        Output("result", "children"),
    ],
    [
        Input("calculate", "n_clicks"),
    ],
    [
        State("first-arg", "value"),
        State("second-arg", "value"),
        State("url", "pathname"),
    ],
    prevent_initial_call=True,
)
def return_project_list_outputs_inputs_states(n_clicks: int, first_arg: int, second_arg: int, project: MySolution):
    return f"{project.url=}"


@callback(
    [
        Output("result", "children"),
    ],
    [
        Input("calculate", "n_clicks"),
    ],
    [
        State("first-arg", "value"),
        State("second-arg", "value"),
        State("url", "pathname"),
    ],
    prevent_initial_call=True,
)
def return_project_no_typehint(n_clicks, first_arg, second_arg, project: MySolution):  # type: ignore
    return f"{project.url=}"


@callback(
    [
        Output("result", "children"),
    ],
    [
        Input("calculate", "n_clicks"),
    ],
    [
        State("first-arg", "value"),
        State("second-arg", "value"),
        State("url", "pathname"),
    ],
    prevent_initial_call=True,
)
def return_project_partial_typehints(n_clicks, first_arg: int, second_arg, project: MySolution):  # type: ignore
    return f"{project.url=}"


@callback(
    outputs=[
        Output("result", "children"),
    ],
    inputs=[
        Input("calculate", "n_clicks"),
        State("first-arg", "value"),
        State("second-arg", "value"),
        State("url", "pathname"),
    ],
    prevent_initial_call=True,
)
def return_project_keyword_args(n_clicks: int, first_arg: int, second_arg: int, project: MySolution):
    return f"{project.url=}"


@callback(
    Output("result", "children"),
    Trigger("calculate", "n_clicks"),
    State("first-arg", "value"),
    State("second-arg", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def return_project_trigger_before_pathname(first_arg: int, second_arg: int, project: MySolution):
    return f"{project.url=}"


@callback(
    Output("result", "children"),
    State("first-arg", "value"),
    State("second-arg", "value"),
    State("url", "pathname"),
    Trigger("calculate", "n_clicks"),
    prevent_initial_call=True,
)
def return_project_trigger_after_pathname(first_arg: int, second_arg: int, project: MySolution):
    return f"{project.url=}"


@callback(
    outputs=[
        Output("result", "children"),
    ],
    inputs=[
        Trigger("calculate", "n_clicks"),
        State("first-arg", "value"),
        State("second-arg", "value"),
        State("url", "pathname"),
    ],
    prevent_initial_call=True,
)
def return_project_keyword_args_with_trigger(first_arg: int, second_arg: int, project: MySolution):
    return f"{project.url=}"


@callback(
    [
        Output("result", "children"),
    ],
    [
        Trigger("calculate", "n_clicks"),
    ],
    [
        State("first-arg", "value"),
        State("second-arg", "value"),
        State("url", "pathname"),
    ],
    prevent_initial_call=True,
)
def return_project_list_outputs_inputs_states_with_trigger(first_arg: int, second_arg: int, project: MySolution):
    return f"{project.url=}"


@callback(
    [
        Output("result", "children"),
    ],
    [
        Input("calculate", "n_clicks"),
    ],
    [
        State("first-arg", "value"),
        State("second-arg", "value"),
        State("third-arg", "value"),
        State("fourth-arg", "value"),
        State("fifth-arg", "value"),
        State("url", "pathname"),
    ],
    prevent_initial_call=True,
)
def return_project_different_annotations(
    n_clicks: int,
    first_arg: list[int],
    second_arg: dict[str, Any],
    third_arg: tuple[str, dict[str, int]],
    fourth_arg: str | int | None,
    project: MySolution,
):
    return f"{project.url=}"


@callback(
    State("url", "pathname"),
    prevent_initial_call=True,
)
def return_entity_url(project: MySolution):
    step = project.steps.my_step
    return step.get_entity_url("file_entity")


@callback(
    Output("result", "children"),
    Input("calculate", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def return_project_display_name(n_clicks: int, project: MySolution):
    return project.project_display_name


@callback(
    Output("result", "children"),
    Output("result2", "children"),
    Input("calculate", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def return_solution_type_and_steps(n_clicks: int, project: MySolution):  # type: ignore
    return project._solution_type, project.steps  # type: ignore
