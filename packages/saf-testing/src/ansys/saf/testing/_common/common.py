# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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

from collections.abc import Generator
from importlib.util import find_spec
from pathlib import Path
import platform
from typing import TypeVar

F = TypeVar("F")
YieldFixture = Generator[F, None, None]


def find_exec_in_venv(venv_parent_dir: Path, exec_name: str, verify: bool = True) -> Path:
    if platform.system() == "Windows":
        exec_path = venv_parent_dir / ".venv" / "Scripts" / f"{exec_name}.exe"
        if verify and not exec_path.is_file():
            exec_path = venv_parent_dir / ".venv" / "Scripts" / f"{exec_name}.cmd"
    else:
        exec_path = venv_parent_dir / ".venv" / "bin" / exec_name
    if verify and not exec_path.is_file():
        raise FileNotFoundError(f"Executable {exec_name} not found in {venv_parent_dir}")
    return exec_path


def has_modules_installed(modules: list[str]) -> bool:
    """Return True if all modules in the list are importable via find_spec."""
    for module in modules:
        try:
            if find_spec(module) is None:
                return False
        except (ImportError, ModuleNotFoundError):
            return False
    return True
