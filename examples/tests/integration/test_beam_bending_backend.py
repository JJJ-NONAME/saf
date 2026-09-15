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

"""Integration tests for the beam bending backend."""

from typing import Any

from ansys.saf.glow.client import InternalSolutionException
from ansys.saf.glow.solution import NO_ENTITY, EntityHandle
from ansys.saf.product_manager.mapdl import MapdlManager
from beam_bending_test_helpers import STANDARD_BEAM_INPUTS, set_standard_beam_input_fields
from mock_mapdl import MockMapdlClient
import numpy as np
import pytest

from saf.solutions.examples.solution.definition import ExamplesSolution
from saf.solutions.examples.solution.scripts.beam_bending import theoretical_model


def test_beam_bending_fields_exposed_and_persisted(
    client_project: ExamplesSolution,
) -> None:
    """Verify default beam fields and updates are exposed and persisted."""
    step = client_project.steps.beam_bending_step

    assert step.get_fields(
        [
            "length_a",
            "length_b",
            "diameter",
            "elasticity_modulus",
            "poisson_ratio",
            "load",
            "nbr_of_pts",
            "mapdl_nbr_of_elements",
            "mapdl_version",
            "mapdl_host",
            "mapdl_port",
            "mapdl_start_timeout",
            "mapdl_loglevel",
            "mapdl_nproc",
            "mapdl_jobname",
            "mapdl_instance_started",
        ],
    ) == {
        "length_a": 1000,
        "length_b": 1000,
        "diameter": 50,
        "elasticity_modulus": 210000,
        "poisson_ratio": 0.27,
        "load": 10000,
        "nbr_of_pts": 100,
        "mapdl_nbr_of_elements": 4,
        "mapdl_version": 252,
        "mapdl_host": "127.0.0.1",
        "mapdl_port": 8080,
        "mapdl_start_timeout": 60,
        "mapdl_loglevel": "INFO",
        "mapdl_nproc": 2,
        "mapdl_jobname": "mapdl_2d_beam",
        "mapdl_instance_started": False,
    }

    set_standard_beam_input_fields(step)

    assert (
        step.get_fields(
            [
                "length_a",
                "length_b",
                "diameter",
                "elasticity_modulus",
                "poisson_ratio",
                "load",
                "nbr_of_pts",
                "mapdl_nbr_of_elements",
            ],
        )
        == STANDARD_BEAM_INPUTS
    )
    assert step.theoretical_deflection == []
    assert step.mapdl_deflection == []
    assert step.mapdl_nodal_displacement == NO_ENTITY
    assert step.mapdl_element_stress == NO_ENTITY


def test_compute_theoretical_deflection(
    client_project: ExamplesSolution,
) -> None:
    """Verify the theoretical-deflection transaction stores the expected result."""

    step = client_project.steps.beam_bending_step
    set_standard_beam_input_fields(step)

    method = step.compute_theoretical_beam_deflection()
    method.wait(timeout=30)

    expected = theoretical_model.compute_beam_deflection(
        step.length_a,
        step.length_b,
        step.diameter,
        step.elasticity_modulus,
        step.load,
        n=step.nbr_of_pts,
    )
    np.testing.assert_allclose(step.theoretical_deflection, expected)
    assert len(step.theoretical_deflection) == 2
    assert all(len(values) == step.nbr_of_pts for values in step.theoretical_deflection)
    assert step.get_method_state("compute_theoretical_beam_deflection").status == "completed"


def test_theoretical_deflection_failure_is_reported(
    client_project: ExamplesSolution,
    mocker: Any,
) -> None:
    """Verify a theoretical-model exception produces a failed method state."""

    error_message = "Theoretical beam model failed"
    mocker.patch.object(
        theoretical_model,
        "compute_beam_deflection",
        side_effect=RuntimeError(error_message),
    )

    step = client_project.steps.beam_bending_step
    set_standard_beam_input_fields(step)
    method = step.compute_theoretical_beam_deflection()

    with pytest.raises(InternalSolutionException):
        method.wait(timeout=30)

    method_state = step.get_method_state("compute_theoretical_beam_deflection")
    assert method_state.status == "failed"
    assert method_state.status_code == 500
    assert method_state.exception_message


@pytest.mark.usefixtures("mock_product_instance")
@pytest.mark.parametrize("mock_product_instance", [{MapdlManager: MockMapdlClient}], indirect=True)
def test_mapdl_workflow_analysis(
    client_project: ExamplesSolution,
) -> None:
    """Verify the MAPDL workflow completes and stores its numerical outputs."""
    step = client_project.steps.beam_bending_step
    set_standard_beam_input_fields(step)

    step.start_mapdl()
    assert step.get_method_state("start_mapdl").status == "completed"
    preprocessing = step.mapdl_preprocessing()
    preprocessing.wait(timeout=30)
    assert step.get_method_state("mapdl_preprocessing").status == "completed"
    solve = step.mapdl_solve()
    solve.wait(timeout=30)
    assert step.get_method_state("mapdl_solve").status == "completed"
    postprocessing = step.mapdl_postprocessing()
    postprocessing.wait(timeout=30)
    assert step.get_method_state("mapdl_postprocessing").status == "completed"

    assert len(step.mapdl_deflection) == 2
    assert len(step.mapdl_deflection[0]) == 5
    assert len(step.mapdl_deflection[1]) == 5
    np.testing.assert_allclose(step.mapdl_deflection[0], np.linspace(0, 2000, 5))
    # zero because the mock is returning zeros for nodal displacement
    np.testing.assert_allclose(step.mapdl_deflection[1], np.zeros(5))
    assert step.mapdl_nodal_displacement != NO_ENTITY
    assert step.mapdl_element_stress != NO_ENTITY
    assert isinstance(step.mapdl_nodal_displacement, EntityHandle)
    assert isinstance(step.mapdl_element_stress, EntityHandle)

    storage_scope = client_project.storage_scope
    assert storage_scope.get_cached(step.mapdl_nodal_displacement).is_file()
    assert storage_scope.get_cached(step.mapdl_element_stress).is_file()


@pytest.mark.usefixtures("mock_product_instance")
@pytest.mark.parametrize("mock_product_instance", [{MapdlManager: MockMapdlClient}], indirect=True)
def test_mapdl_solve_failure_is_reported(
    client_project: ExamplesSolution,
    mocker: Any,
) -> None:
    """Verify a MAPDL solve exception produces a failed method state."""

    step = client_project.steps.beam_bending_step
    set_standard_beam_input_fields(step)
    step.start_mapdl()
    preprocessing = step.mapdl_preprocessing()
    preprocessing.wait(timeout=30)

    error_message = "MAPDL solve failed"
    mocker.patch.object(MockMapdlClient, "solve", side_effect=RuntimeError(error_message))
    method = step.mapdl_solve()

    with pytest.raises(InternalSolutionException):
        method.wait(timeout=30)

    method_state = step.get_method_state("mapdl_solve")
    assert method_state.status == "failed"
    assert method_state.status_code == 500
    assert method_state.exception_message
