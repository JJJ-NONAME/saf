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

import os
from pathlib import Path
import shutil

import pytest


@pytest.fixture(autouse=True)
def auto_use_mock_appdata(mock_appdata: Path) -> None:
    return


@pytest.fixture
def cleanup_awp_root_env_vars(monkeypatch: pytest.MonkeyPatch):
    for key in os.environ:
        if key.startswith(("ANSYSEM_ROOT", "AWP_ROOT")):
            monkeypatch.delenv(key)


def copy_mock_solution_to_layout(
    src_dir: Path,
    solution_name: str,
    namespace_root: str,
) -> tuple[Path, tuple[str, ...], str, str]:
    """Copy a mock solution to src/<namespace_root>/<solution_name> layout."""
    source_solution_dir = Path(__file__).parent / "mocks" / "solutions" / solution_name
    if not source_solution_dir.is_dir():
        raise NotADirectoryError(f"Mock solution directory not found at {source_solution_dir}")

    namespace_root_parts = tuple(namespace_root.split("."))
    package_prefix = namespace_root
    destination_solution_dir = src_dir / Path(*namespace_root_parts) / solution_name
    expected_namespace_root_parts = namespace_root_parts
    expected_solution_name = solution_name

    destination_solution_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_solution_dir, destination_solution_dir)

    for py_file in destination_solution_dir.rglob("*.py"):
        py_file.write_text(py_file.read_text().replace("tests.mocks.solutions", package_prefix))

    module_name = f"{package_prefix}.{solution_name}.main"
    return destination_solution_dir, expected_namespace_root_parts, expected_solution_name, module_name
