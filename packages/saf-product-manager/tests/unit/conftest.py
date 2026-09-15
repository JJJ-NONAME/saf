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


@pytest.fixture(scope="session", autouse=True)
def configure_solution_modules(monkeysession: pytest.MonkeyPatch) -> None:
    monkeysession.setenv("GLOW_SOLUTION_DEFINITION", "tests.mocks.solution_end_to_end.solution.definition")
    monkeysession.setenv("GLOW_UI_MODULE", "tests.mocks.solution_end_to_end.ui.app")
    # Geometry is the only product configuration that looks for the geometry installation on config instantiation
    # instead of when trying to use it (e.g., when calling exe_path_for_pim).
    monkeysession.setenv("GEOMETRY_ROOT252", "fake_path_to_geometry")
