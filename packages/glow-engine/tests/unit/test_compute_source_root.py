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

from pathlib import Path
from types import ModuleType

import pytest

import ansys  # references directory
import ansys.saf  # references directory
import ansys.saf.glow._hps_parametric_studies.execution_specification  # references python file
from ansys.saf.glow._utilities.compute_source_root import compute_source_root
import ansys.saf.glow.solution  # references __init__.py


@pytest.mark.xfail(reason="recent flakiness")
@pytest.mark.parametrize(
    "module",
    [
        ansys,
        ansys.saf,
        ansys.saf.glow,
        ansys.saf.glow.solution,
        ansys.saf.glow._hps_parametric_studies.execution_specification,
    ],
)
def test_compute_source_root(module: ModuleType):
    source_root = compute_source_root(module)
    assert source_root.exists()
    assert source_root.is_dir()
    assert source_root == Path(__file__).parent.parent.parent / "src"
