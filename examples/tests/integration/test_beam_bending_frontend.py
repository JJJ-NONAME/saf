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

"""Integration tests for the beam bending frontend callbacks."""

from collections.abc import Iterator
import json
import time
from typing import Any

from ansys.saf.glow._testing.solution import is_within_dash_callback_context
from ansys.saf.glow.client import InternalSolutionException
from ansys.saf.glow.solution import MethodStatus
from ansys.saf.product_manager.mapdl import MapdlManager
from beam_bending_test_helpers import STANDARD_BEAM_INPUTS
from dash.testing import ignore_register_page
from mock_mapdl import MockMapdlClient
import numpy as np
import pytest

from saf.solutions.examples.solution.definition import ExamplesSolution
from saf.solutions.examples.solution.scripts.beam_bending import theoretical_model

with ignore_register_page():
    from saf.solutions.examples.ui.app import app as examples_app
    from saf.solutions.examples.ui.pages.beam_bending import compute_page


pytestmark = [pytest.mark.usefixtures("init_dashclient")]


@pytest.fixture(scope="module")
def dash_app(init_dashclient: None) -> Any:
    """Return the example Dash app with all callbacks registered."""
    if not examples_app.callback_map:
        examples_app.register_callbacks()
    return examples_app


@pytest.fixture
def dash_ui_client(dash_app: Any) -> Iterator[Any]:
    """Provide a Flask test client for the example Dash UI."""
    with dash_app.server.test_client() as client:
        yield client


def _request_component_id(component_id: Any) -> Any:
    """Convert Dash's serialized pattern-matching IDs to request IDs."""
    if isinstance(component_id, str) and component_id.startswith("{"):
        return json.loads(component_id)
    return component_id


def _callback_outputs(callback_entry: dict[str, Any]) -> list[Any]:
    """Return callback outputs in the format expected by Dash's request endpoint."""
    outputs = callback_entry["output"]
    return list(outputs) if isinstance(outputs, (list, tuple)) else [outputs]


def _invoke_dash_callback(
    dash_ui_client: Any,
    dash_app: Any,
    *,
    input_component_id: str,
    input_values: list[Any],
    state_values: list[Any],
    changed_prop_id: str,
) -> dict[str, Any]:
    """Invoke one registered callback through Dash's update endpoint."""
    matching_callbacks = [
        (callback_id, callback_entry)
        for callback_id, callback_entry in dash_app.callback_map.items()
        if any(input_definition["id"] == input_component_id for input_definition in callback_entry["inputs"])
    ]
    if len(matching_callbacks) != 1:
        raise AssertionError(f"Expected one callback for {input_component_id!r}, found {len(matching_callbacks)}.")

    callback_id, callback_entry = matching_callbacks[0]
    callback_inputs = callback_entry["inputs"]
    callback_states = callback_entry["state"]
    if len(input_values) != len(callback_inputs):
        raise AssertionError(f"Expected {len(callback_inputs)} callback inputs, got {len(input_values)}.")
    if len(state_values) != len(callback_states):
        raise AssertionError(f"Expected {len(callback_states)} callback states, got {len(state_values)}.")

    outputs = _callback_outputs(callback_entry)
    payload = {
        "output": callback_id,
        "outputs": [
            {
                "id": output.component_id,
                "property": output.component_property,
            }
            for output in outputs
        ],
        "inputs": [
            {
                "id": _request_component_id(input_definition["id"]),
                "property": input_definition["property"],
                "value": value,
            }
            for input_definition, value in zip(callback_inputs, input_values, strict=True)
        ],
        "state": [
            {
                "id": _request_component_id(state_definition["id"]),
                "property": state_definition["property"],
                "value": value,
            }
            for state_definition, value in zip(callback_states, state_values, strict=True)
        ],
        "changedPropIds": [changed_prop_id],
    }
    context_token = is_within_dash_callback_context.set(True)
    try:
        response = dash_ui_client.post("/_dash-update-component", json=payload)
    finally:
        is_within_dash_callback_context.reset(context_token)
    assert response.status_code == 200, response.get_data(as_text=True)
    response_body = response.get_json()
    assert isinstance(response_body, dict)
    assert "response" in response_body
    return response_body["response"]


def _notifications(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize the single notification value returned by Dash."""
    value = result["notification-container"]["sendNotifications"]
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list) and all(isinstance(notification, dict) for notification in value):
        return value
    raise AssertionError(f"Unexpected notification payload: {value!r}")


def _start_callback_state(project_name: str) -> list[Any]:
    """Build the state values for the start-computation callback."""
    return [
        STANDARD_BEAM_INPUTS["length_a"],
        STANDARD_BEAM_INPUTS["length_b"],
        STANDARD_BEAM_INPUTS["diameter"],
        STANDARD_BEAM_INPUTS["elasticity_modulus"],
        STANDARD_BEAM_INPUTS["poisson_ratio"],
        STANDARD_BEAM_INPUTS["load"],
        STANDARD_BEAM_INPUTS["nbr_of_pts"],
        STANDARD_BEAM_INPUTS["mapdl_nbr_of_elements"],
        project_name,
    ]


def _trigger_beam_computation(dash_ui_client: Any, project_name: str) -> dict[str, Any]:
    """Start a beam computation through Dash's callback endpoint."""
    return _invoke_dash_callback(
        dash_ui_client,
        examples_app,
        input_component_id="trigger-compute-after-button-click",
        input_values=[1],
        state_values=_start_callback_state(project_name),
        changed_prop_id="trigger-compute-after-button-click.data",
    )


def _find_component_ids(value: Any) -> set[str]:
    """Recursively collect component IDs from a Dash component tree."""
    if hasattr(value, "to_plotly_json"):
        return _find_component_ids(value.to_plotly_json())
    if isinstance(value, dict):
        component_ids = set()
        props = value.get("props")
        if isinstance(props, dict) and isinstance(component_id := props.get("id"), str):
            component_ids.add(component_id)
        for child in value.values():
            component_ids.update(_find_component_ids(child))
        return component_ids
    if isinstance(value, list):
        component_ids = set()
        for child in value:
            component_ids.update(_find_component_ids(child))
        return component_ids
    return set()


def _wait_for_methods(step: Any, method_names: tuple[str, ...], timeout: float = 30.0) -> None:
    """Wait for long-running methods to complete, fail, or exceed the timeout."""
    deadline = time.monotonic() + timeout
    while True:
        method_states = {name: step.get_long_running_method_state(name) for name in method_names}
        failed_methods = [name for name, state in method_states.items() if state.status == MethodStatus.Failed]
        if failed_methods:
            pytest.fail(f"Long-running methods failed: {', '.join(failed_methods)}")
        if all(state.status == MethodStatus.Completed for state in method_states.values()):
            return
        if time.monotonic() >= deadline:
            unfinished_methods = [
                name for name, state in method_states.items() if state.status != MethodStatus.Completed
            ]
            pytest.fail(f"Timed out waiting for methods: {', '.join(unfinished_methods)}")
        time.sleep(0.1)


def test_beam_bending_compute_layout_contains_expected_controls(
    client_project: ExamplesSolution,
) -> None:
    """Verify the compute page contains its controls and event listeners."""
    layout = compute_page.layout(client_project)
    component_ids = _find_component_ids(layout.to_plotly_json())

    assert {
        "compute-deflection",
        "deflection-graph",
        "trigger-compute-after-button-click",
        "compute-theoretical-beam-deflection-listener",
        "mapdl-preprocessing-listener",
        "mapdl-solve-listener",
        "mapdl-postprocessing-listener",
    }.issubset(component_ids)


def test_compute_button_disables_inputs_and_starts_status_notification(
    dash_ui_client: Any,
) -> None:
    """Verify clicking Compute disables inputs and shows the starting notification."""
    result = _invoke_dash_callback(
        dash_ui_client,
        examples_app,
        input_component_id="compute-deflection",
        input_values=[1],
        state_values=[0],
        changed_prop_id="compute-deflection.n_clicks",
    )

    assert result["compute-deflection"] == {"disabled": True, "loading": True}
    disabled_outputs = [properties["disabled"] for properties in result.values() if "disabled" in properties]
    assert len(disabled_outputs) == 9
    assert all(disabled_outputs)
    assert result["trigger-compute-after-button-click"] == {"data": 1}
    assert _notifications(result) == [
        {
            "action": "show",
            "id": "computation-status-notification",
            "title": "Starting computation",
            "message": "The computation will start shortly. Please wait...",
            "loading": True,
            "color": "orange",
            "autoClose": False,
        }
    ]


@pytest.mark.usefixtures("mock_product_instance")
@pytest.mark.parametrize("mock_product_instance", [{MapdlManager: MockMapdlClient}], indirect=True)
def test_start_computation_persists_inputs_and_starts_analysis(
    client_project: ExamplesSolution,
    project_name: str,
    dash_ui_client: Any,
) -> None:
    """Verify computation inputs persist and the initial backend methods start."""
    result = _trigger_beam_computation(dash_ui_client, project_name)

    assert _notifications(result) == [
        {
            "action": "update",
            "id": "computation-status-notification",
            "title": "Computation started",
            "message": "The computation has been started. This may take a few moments.",
            "loading": True,
            "color": "blue",
            "autoClose": False,
        }
    ]

    step = client_project.steps.beam_bending_step

    assert step.get_fields(list(STANDARD_BEAM_INPUTS)) == STANDARD_BEAM_INPUTS

    _wait_for_methods(step, ("compute_theoretical_beam_deflection", "mapdl_preprocessing"))
    assert step.get_method_state("start_mapdl").status == "completed"


@pytest.mark.usefixtures("mock_product_instance")
@pytest.mark.parametrize("mock_product_instance", [{MapdlManager: MockMapdlClient}], indirect=True)
def test_start_computation_returns_error_when_mapdl_start_fails(
    client_project: ExamplesSolution,
    project_name: str,
    mocker: Any,
    dash_ui_client: Any,
) -> None:
    """Verify MAPDL startup errors produce an error notification."""
    error_message = "MAPDL startup failed"
    mocker.patch.object(MapdlManager, "initialize", side_effect=RuntimeError(error_message))

    result = _trigger_beam_computation(dash_ui_client, project_name)

    assert _notifications(result) == [
        {
            "title": "Error",
            "id": "mapdl-instance-error-notification",
            "action": "show",
            "message": "Failed to start MAPDL instance. Check server logs for details.",
        }
    ]
    step = client_project.steps.beam_bending_step
    _wait_for_methods(step, ("compute_theoretical_beam_deflection",))
    assert step.get_method_state("start_mapdl").status == "failed"


@pytest.mark.usefixtures("mock_product_instance")
@pytest.mark.parametrize("mock_product_instance", [{MapdlManager: MockMapdlClient}], indirect=True)
def test_computation_events_advance_mapdl_workflow_and_update_graph(
    client_project: ExamplesSolution,
    project_name: str,
    dash_ui_client: Any,
) -> None:
    """Verify completion events advance the workflow and update the deflection graph."""
    _trigger_beam_computation(dash_ui_client, project_name)

    step = client_project.steps.beam_bending_step
    _wait_for_methods(step, ("compute_theoretical_beam_deflection", "mapdl_preprocessing"))

    figure = {
        "data": [
            {"x": [0, 0], "y": [0, 0]},
            {"x": [], "y": []},
            {"x": [], "y": []},
        ],
        "layout": {"annotations": [{"ax": 0, "x": 0}]},
    }

    result = _invoke_dash_callback(
        dash_ui_client,
        examples_app,
        input_component_id="mapdl-preprocessing-listener",
        input_values=["", "preprocessing completed", "", ""],
        state_values=[project_name, figure],
        changed_prop_id="mapdl-preprocessing-listener.message",
    )
    assert result == {}

    _wait_for_methods(step, ("mapdl_solve",))
    result = _invoke_dash_callback(
        dash_ui_client,
        examples_app,
        input_component_id="mapdl-solve-listener",
        input_values=["", "", "solve completed", ""],
        state_values=[project_name, figure],
        changed_prop_id="mapdl-solve-listener.message",
    )
    assert result == {}

    _wait_for_methods(step, ("mapdl_postprocessing",))
    result = _invoke_dash_callback(
        dash_ui_client,
        examples_app,
        input_component_id="mapdl-postprocessing-listener",
        input_values=["", "", "", "postprocessing completed"],
        state_values=[project_name, figure],
        changed_prop_id="mapdl-postprocessing-listener.message",
    )

    assert _notifications(result) == [
        {
            "action": "update",
            "id": "computation-status-notification",
            "title": "Computation completed",
            "message": "The computation has been completed successfully.",
            "loading": False,
            "color": "green",
            "autoClose": 2000,
        }
    ]
    graph = result["deflection-graph"]["figure"]
    assert graph["data"][0]["x"] == [0, 2000]
    np.testing.assert_allclose(graph["data"][1]["x"], step.theoretical_deflection[0])
    np.testing.assert_allclose(graph["data"][1]["y"], step.theoretical_deflection[1])
    np.testing.assert_allclose(graph["data"][2]["x"], step.mapdl_deflection[0])
    np.testing.assert_allclose(graph["data"][2]["y"], step.mapdl_deflection[1])
    assert graph["layout"]["annotations"][0]["ax"] == 1000
    assert graph["layout"]["annotations"][0]["x"] == 1000
    assert result["compute-deflection"] == {"disabled": False, "loading": False}
    disabled_outputs = [properties["disabled"] for properties in result.values() if "disabled" in properties]
    assert len(disabled_outputs) == 9
    assert not any(disabled_outputs)


def test_failed_computation_event_returns_failure_notification(
    client_project: ExamplesSolution,
    project_name: str,
    mocker: Any,
    dash_ui_client: Any,
) -> None:
    """Verify a failed theoretical calculation produces a failure notification."""

    error_message = "Theoretical beam model failed"
    mocker.patch.object(
        theoretical_model,
        "compute_beam_deflection",
        side_effect=RuntimeError(error_message),
    )

    step = client_project.steps.beam_bending_step
    method = step.compute_theoretical_beam_deflection()
    with pytest.raises(InternalSolutionException):
        method.wait(timeout=30)

    result = _invoke_dash_callback(
        dash_ui_client,
        examples_app,
        input_component_id="compute-theoretical-beam-deflection-listener",
        input_values=["theoretical calculation failed", "", "", ""],
        state_values=[project_name, {"data": [], "layout": {}}],
        changed_prop_id="compute-theoretical-beam-deflection-listener.message",
    )

    assert _notifications(result) == [
        {
            "action": "update",
            "id": "computation-status-notification",
            "title": "Computation failed",
            "message": "The computation has failed. Please check the logs for more details.",
            "loading": False,
            "color": "red",
            "autoClose": 2000,
        }
    ]
    assert "deflection-graph" not in result
    disabled_outputs = [properties["disabled"] for properties in result.values() if "disabled" in properties]
    assert len(disabled_outputs) == 9
    assert not any(disabled_outputs)
