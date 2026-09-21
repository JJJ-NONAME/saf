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

"""Check that the installed examples can be turned into a desktop installer."""

import os
import platform

from tests.e2e.conftest import BuiltExamples


def test_saf_build_creates_desktop_installer(built_examples: BuiltExamples) -> None:
    """Verify ``saf build`` creates a usable installer for the current OS.

    The fixture runs ``saf build``. The resulting artifact must be present,
    non-empty, and executable on Linux.
    """
    assert built_examples.command.returncode == 0, "saf build did not complete successfully."
    assert built_examples.installer.is_file(), "saf build did not create the expected installer."
    assert built_examples.installer.stat().st_size > 0, "The generated installer is empty."
    if platform.system() == "Linux":
        assert os.access(built_examples.installer, os.X_OK), "The Linux installer is not executable."
