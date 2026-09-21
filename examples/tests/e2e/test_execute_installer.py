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

"""Check that the generated desktop installer deploys the solution."""

import pytest

from tests.e2e.conftest import InstalledDesktopExamples


@pytest.mark.xfail(
    reason="The desktop installer execution is currently unstable in CI.",
    strict=False,
)
def test_generated_installer_executes_without_errors(
    installed_desktop_examples: InstalledDesktopExamples,
) -> None:
    """Verify the generated desktop installer completes and deploys solution files.

    The fixture runs the installer without its UI. A deployed ``version.txt``
    confirms that application content was actually written.
    """
    assert installed_desktop_examples.command.returncode == 0, "The desktop installer did not complete successfully."
    assert any(
        installed_desktop_examples.installation_directory.rglob("version.txt"),
    ), "The installer did not deploy a version.txt file."
