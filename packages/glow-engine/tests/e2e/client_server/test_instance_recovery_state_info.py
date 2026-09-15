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

import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    "solution_module",
    ["tests.mocks.solutions.invalid_recovery_state_info", "tests.mocks.solutions.invalid_recovery_state_info_unused"],
)
def test_recovery_state_info_without_defaults_fails_to_launch(solution_module: str):
    """Test that a solution with RecoveryStateInfo without default values fails to load."""
    # We cannot use our run_glow/session_glow fixtures because they require importing the solution module, and this
    # already triggers the exception. To be able to measure it when trying to run it, we need to manually launch the
    # process.
    cmd = [
        sys.executable,
        "-m",
        "ansys.saf.glow.cli",
        "api",
        "--definition",
        solution_module,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 1
    expected_error_message = (
        "InvalidRecoveryStateInfo must be instantiable without arguments: "
        "1 validation error for InvalidRecoveryStateInfo"
    )
    assert expected_error_message in p.stderr
