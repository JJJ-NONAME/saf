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

"""Testing project injection with future annotations"""

from __future__ import annotations

import logging

from dash import dcc  # pyright: ignore[reportMissingTypeStubs]
from dash_extensions.enrich import Input, Output, State, html  # pyright: ignore[reportMissingTypeStubs]

from ansys.saf.glow.client import callback
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution  # noqa: TC001
from tests.mocks.solution_end_to_end.solution.transaction_verification_step import (
    TransactionVerificationStep,  # noqa: TC001
)

logger = logging.getLogger(__name__)


def layout(step: TransactionVerificationStep):
    """Layout of the future step UI."""
    return html.Div(
        [
            html.H1("We are in Future Page"),
            html.Div(
                [
                    dcc.Input(id="arg1", type="number"),
                    dcc.Input(id="arg2", type="number"),
                    html.Button("Calculate", id="calculate-future", n_clicks=0),
                    html.Div(id="result-future", children=f"Result:{step.result}"),
                ],
            ),
        ],
    )


@callback(
    Output("result-future", "children"),
    Input("calculate-future", "n_clicks"),
    State("arg1", "value"),
    State("arg2", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def calculate_project_injected(n_clicks: int, first_arg: int, second_arg: int, project: EndToEndSolution):
    """Callback function to trigger the computation."""
    step = project.steps.transaction_verification_step
    step.field_1 = first_arg
    step.field_2 = second_arg
    step.get_field_1_and_2_and_set_the_sum_in_result()
    return f"Result:{step.result}"
