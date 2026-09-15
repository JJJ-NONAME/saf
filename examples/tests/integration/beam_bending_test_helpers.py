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

"""Shared fixtures and values for beam-bending integration tests."""

from typing import Any

STANDARD_BEAM_INPUTS: dict[str, float | int] = {
    "length_a": 1000,
    "length_b": 1000,
    "diameter": 50,
    "elasticity_modulus": 210000,
    "poisson_ratio": 0.27,
    "load": 10000,
    "nbr_of_pts": 25,
    "mapdl_nbr_of_elements": 4,
}


def set_standard_beam_input_fields(step: Any) -> None:
    """Populate a beam-bending step with shared valid input values."""
    step.set_fields(STANDARD_BEAM_INPUTS)
