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

import pytest

from ansys.saf.glow._core.exceptions import SolutionLoadException
from ansys.saf.glow._server.solution import SolutionService
import tests.mocks.solutions.one_method_cyclic_dependency as one_method_cyclic_dependency


def test_solution_with_one_method_cyclic_dependency():
    solution_service = SolutionService(one_method_cyclic_dependency)
    try:
        solution_service.build_and_validate()
    except SolutionLoadException as e:
        pytest.fail(f"Unexpected SolutionLoadException: {e}")
