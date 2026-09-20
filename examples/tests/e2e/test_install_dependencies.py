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

"""Check the first lifecycle step: installing the examples solution."""

import json
import subprocess

from tests.e2e.conftest import InstalledExamples


def test_saf_install_completes_successfully(
    installed_examples: InstalledExamples,
) -> None:
    """Verify the examples solution installs successfully with the real SAF CLI.

    The fixture requests the E2E dependency groups with ``saf install -f -d``.
    This test checks both the command result and the files that prove the
    workspace was prepared for building.
    """
    assert installed_examples.command.returncode == 0, "saf install -f -d did not complete successfully."
    assert (installed_examples.workspace / ".venv").is_dir(), "The install did not create a .venv directory."
    assert (installed_examples.workspace / "poetry.lock").is_file(), "The install did not create poetry.lock."


def test_saf_install_verifies_locked_dependencies(
    installed_examples: InstalledExamples,
    saf_executable: str,
) -> None:
    """Verify every dependency group requested by the install fixture is installed.

    ``poetry show`` reports both the versions resolved by ``poetry.lock`` and
    whether those exact packages are installed in the solution's virtual
    environment. The groups passed to ``poetry show`` come from the same
    ``InstalledExamples`` value used to invoke ``saf install``.
    """
    poetry_groups = ",".join(("main", *installed_examples.dependency_groups))
    dependency_check = subprocess.run(
        [
            saf_executable,
            "execute",
            f"poetry show --format=json --only {poetry_groups}",
        ],
        cwd=installed_examples.workspace,
        capture_output=True,
        text=True,
        check=False,
    )

    assert dependency_check.returncode == 0, (
        "Could not inspect the installed dependencies with Poetry.\n"
        f"stdout:\n{dependency_check.stdout}\n"
        f"stderr:\n{dependency_check.stderr}"
    )

    # ``saf execute`` prints a line such as "Environment variables loaded from ..."
    # to stdout before running the requested command whenever the solution has an
    # ``.env`` file. Locate the JSON array poetry produced instead of assuming the
    # whole stdout is JSON.
    json_start = dependency_check.stdout.find("[")
    assert json_start != -1, "Could not find a JSON array in the Poetry output.\n" f"Output:\n{dependency_check.stdout}"

    try:
        packages = json.loads(dependency_check.stdout[json_start:])
    except json.JSONDecodeError as error:
        raise AssertionError(
            "Poetry did not return valid JSON while reporting installed dependencies.\n"
            f"Output:\n{dependency_check.stdout}",
        ) from error

    assert isinstance(packages, list) and packages, "Poetry returned no locked dependencies to verify."

    packages_not_installed = []
    for package in packages:
        if not isinstance(package, dict):
            packages_not_installed.append(f"<invalid package record: {package!r}>")
            continue
        if package.get("installed_status") != "installed":
            packages_not_installed.append(
                f"{package.get('name', '<unknown>')}=={package.get('version', '<unknown>')} "
                f"(status: {package.get('installed_status', '<unknown>')})",
            )
    assert (
        not packages_not_installed
    ), "The installed environment does not match the locked dependencies:\n" + "\n".join(
        f"- {package}" for package in packages_not_installed
    )
