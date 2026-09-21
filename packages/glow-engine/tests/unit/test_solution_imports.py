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
import subprocess
import sys


def test_public_imports_dont_import_hps():
    # the body of the test is run in a separate process to avoid the legitimate inclusion of the HPS client
    # by the other tests and test fixtures in the test suite
    result = subprocess.run(
        [sys.executable, (Path(__file__).parent / "public_import.py").as_posix()],
        capture_output=True,
    )

    # Top tip: when the following assert fails you won't get much help from the pytest output.
    # To diagnose the failure insert a temporary syntax error into
    # .venv/lib/<the python dir>/site-packages/ansys/hps/client/__init__.py
    # and run
    # poetry run python tests/unit/solution_import.py
    # The resulting stack trace will indicate the import chain that is importing
    # the HPS client

    assert result.returncode == 0, result.stdout.decode("utf-8") + result.stderr.decode("utf-8")
