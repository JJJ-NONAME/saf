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
import random
import string
from types import ModuleType

from _pytest.monkeypatch import MonkeyPatch
import pytest

from ansys.saf.desktop.orchestrator._telemetry import utilities

default_config_path = Path(utilities.__file__).parent / "configs" / "api_server_config.yaml"


def get_random_identifier() -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choices(alphabet, k=8))


def _write_blank_file(file: Path) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text("")


@pytest.fixture
def empty_solution(monkeypatch: MonkeyPatch, tmp_path: Path):
    solution_name = f"s{get_random_identifier()}"
    solution_dir = tmp_path / solution_name
    solution_module_file = solution_dir / "solution" / "definition.py"
    _write_blank_file(solution_module_file)
    monkeypatch.syspath_prepend(tmp_path)  # type: ignore
    return (f"{solution_name}.solution.definition", solution_dir)


def test_get_config_for_loadable_solution_that_omits_telemetry_directory_returns_default_config(
    empty_solution: tuple[str, Path],
):
    solution_module_name, _ = empty_solution
    assert utilities.get_config_file("api_server", solution_module_name) == default_config_path


def test_get_config_for_unloadable_solution_that_omits_telemetry_directory_returns_default_config(
    fake_solution_module_with_no_logging_config: ModuleType,
):
    assert utilities.get_config_file("api_server", fake_solution_module_with_no_logging_config) == default_config_path
