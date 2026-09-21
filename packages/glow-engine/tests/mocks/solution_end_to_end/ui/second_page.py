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

"""Frontend of the second page."""

import logging

from dash import dcc  # pyright: ignore[reportMissingTypeStubs]
from dash_extensions.enrich import Input, Output, State, html  # pyright: ignore[reportMissingTypeStubs]

from ansys.saf.glow.client import callback
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution
from tests.mocks.solution_end_to_end.solution.transaction_verification_step import (
    CustomTypeXYZ,
    TransactionVerificationStep,
)

logger = logging.getLogger(__name__)


def layout(step: TransactionVerificationStep):
    """Layout of the second step UI."""
    return html.Div(
        [
            html.H1("We are in Second Page"),
            html.Div(
                [
                    dcc.Input(id="x_arg", type="number"),
                    dcc.Input(id="y_arg", type="number"),
                    dcc.Input(id="z_arg", type="number"),
                    html.Button("Test non-stored I/O DashClient ", id="test_non_stored", n_clicks=0),
                    html.Div(id="test_non_stored_result", children="Workflow not run yet."),
                ],
            ),
            html.Div(
                [
                    html.Button("Render BDM Image", id="render_image", n_clicks=0),
                    html.Img(
                        id="entity_img",
                        style={"width": "100px", "height": "100px"},
                    ),
                ],
            ),
        ],
    )


@callback(
    Output("entity_img", "src"),
    Input("render_image", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def render_image(n_clicks: int, project: EndToEndSolution):
    step = project.steps.transaction_verification_step
    return step.get_entity_url("image_entity")


@callback(
    Output("test_non_stored_result", "children"),
    Input("test_non_stored", "n_clicks"),
    State("x_arg", "value"),
    State("y_arg", "value"),
    State("z_arg", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def non_stored_io_workflow(n_clicks: int, x: int, y: int, z: int, project: EndToEndSolution):
    """Callback that uses non-stored inputs and outputs on transaction methods."""
    expected_result = CustomTypeXYZ(x=x, y=y**2, z=z)

    try:
        step = project.steps.transaction_verification_step

        step.process_input_before_uploading(y=y)
        output = step.build_and_return_custom_type(x=x, z=z)
        step.store_custom_type_from_client(ct=output)

        assert step.custom_object == expected_result
        return "Workflow run successful."
    except Exception:
        logger.exception("..")
        return "Failed workflow."
