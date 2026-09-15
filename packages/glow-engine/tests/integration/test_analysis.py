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
import subprocess
import sys
from typing import Any
import uuid

from ansys.saf.glow._server.analysis import AnalysisResultModel
from ansys.saf.glow._utilities.solution_modules import (
    _AUTODISCOVERY_ENV_VARS_ERROR,  # pyright: ignore[reportPrivateUsage]
)
from ansys.saf.glow.cli import run_analysis
from tests.conftest import IGNORE_PYC_FILES, MOCKS_DIR, SOLUTIONS_MOCKS_DIR


def _run_cli_analysis_using_glow_module(
    definition_name: str | None = None,
    solution_name: str | None = None,
    env: dict[str, Any] | None = None,
) -> AnalysisResultModel:
    args = [sys.executable, "-m", "ansys.saf.glow.cli", "analysis"]
    if definition_name:
        args.extend(["--definition", definition_name])
    elif solution_name:
        args.extend(["--solution", solution_name])
    env = env if env is not None else os.environ.copy()
    raw_output = subprocess.check_output(args, env=env)
    return AnalysisResultModel.model_validate_json(raw_output)


def _run_cli_analysis_using_solution_module(solution_name: str) -> AnalysisResultModel:
    args = [sys.executable, "-m", solution_name, "analysis"]
    raw_output = subprocess.check_output(args)
    return AnalysisResultModel.model_validate_json(raw_output)


def _run_func_analysis_using_solution_module(solution_main_module_name: str) -> AnalysisResultModel:
    return run_analysis(solution_main_module_name=solution_main_module_name)


def _copy_solution_to_ansys_dir(tmp_path: Path, solution_dir: Path) -> dict[str, Any]:
    src_dir = tmp_path / str(uuid.uuid4())
    dest_solution_dir = src_dir / "src" / "ansys" / "solutions" / solution_dir.name
    dest_solution_dir.parent.mkdir(parents=True, exist_ok=True)
    if solution_dir.suffix == ".py":
        shutil.copyfile(solution_dir, dest_solution_dir)
    else:
        shutil.copytree(solution_dir, dest_solution_dir, dirs_exist_ok=True, ignore=IGNORE_PYC_FILES)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_dir / "src")
    env["SOLUTION_DIR"] = str(dest_solution_dir)
    return env


def _verify_valid_result(
    result: AnalysisResultModel,
    solution_name: str,
    definition_module: str,
    uses_instances: bool = False,
    ui_module: str | None = None,
):
    assert result.valid
    assert result.solution_name == solution_name
    assert result.uses_shared_product_instances == uses_instances
    assert result.solution_module == definition_module
    assert not result.ui_module if ui_module is None else result.ui_module == ui_module


def test_cli_analysis_of_definition_is_valid_and_has_correct_name_and_no_instances():
    result = _run_cli_analysis_using_glow_module(definition_name="tests.mocks.solutions.minimal_solution")
    _verify_valid_result(result, "MinimalSolution", "tests.mocks.solutions.minimal_solution")


def test_cli_analysis_of_definition_with_two_solutions_is_invalid_and_has_correct_name_and_no_instances():
    result = _run_cli_analysis_using_glow_module(definition_name="tests.mocks.solutions.two_solutions")
    assert not result.valid
    assert result.error == "The solution definition module defines more than one 'Solution' class."
    assert result.stack_trace


def test_cli_analysis_of_definition_with_instances_is_valid_and_has_correct_name_and_instances():
    result = _run_cli_analysis_using_glow_module(definition_name="tests.mocks.solutions.instances")
    _verify_valid_result(result, "InstancesSolution", "tests.mocks.solutions.instances", uses_instances=True)


def test_cli_analysis_of_solution_main_is_valid_and_has_correct_name_and_no_instances():
    # here we are also testing to access it through the solution module
    result = _run_cli_analysis_using_solution_module("tests.mocks.solution_rare_structure.minimal_main")
    _verify_valid_result(result, "MinimalSolution", "tests.mocks.solutions.minimal_solution")


def test_func_analysis_of_solution_main_is_valid_and_has_correct_name_and_no_instances():
    result = _run_func_analysis_using_solution_module("tests.mocks.solution_rare_structure.minimal_main")
    _verify_valid_result(result, "MinimalSolution", "tests.mocks.solutions.minimal_solution")


def test_cli_analysis_of_definition_using_path(tmp_path: Path):
    # Requirements:
    # - to have /ansys/solutions/ in the file path
    # - default `definition`/`app` imports in main
    env = _copy_solution_to_ansys_dir(tmp_path, SOLUTIONS_MOCKS_DIR / "instances.py")
    result = _run_cli_analysis_using_glow_module(definition_name=env["SOLUTION_DIR"])
    _verify_valid_result(result, "InstancesSolution", "ansys.solutions.instances", uses_instances=True)


def test_cli_analysis_of_solution_with_ui_is_valid():
    result = _run_cli_analysis_using_glow_module(solution_name="tests.mocks.solution_with_ui.main")
    _verify_valid_result(
        result,
        "MySolution",
        "tests.mocks.solution_with_ui.solution.definition",
        ui_module="tests.mocks.solution_with_ui.ui.app",
    )


def test_cli_analysis_of_solution_main_is_valid_and_has_ui():
    # here we are also testing to access it through the solution module
    result = _run_cli_analysis_using_solution_module("tests.mocks.solution_with_ui.main")
    _verify_valid_result(
        result,
        "MySolution",
        "tests.mocks.solution_with_ui.solution.definition",
        ui_module="tests.mocks.solution_with_ui.ui.app",
    )


def test_func_analysis_of_solution_main_is_valid_and_has_ui():
    # here we are also testing to access it through the solution module
    result = _run_func_analysis_using_solution_module("tests.mocks.solution_with_ui.main")
    _verify_valid_result(
        result,
        "MySolution",
        "tests.mocks.solution_with_ui.solution.definition",
        ui_module="tests.mocks.solution_with_ui.ui.app",
    )


def test_cli_analysis_of_solution_using_path_with_ui_is_valid(tmp_path: Path):
    # Requirements:
    # - to have /ansys/solutions/ in the file path
    # - default `definition`/`app` imports in main
    env = _copy_solution_to_ansys_dir(tmp_path, MOCKS_DIR / "solution_with_ui_in_ansys")
    result = _run_cli_analysis_using_glow_module(solution_name=f"{env['SOLUTION_DIR']}/main.py")
    _verify_valid_result(
        result,
        "MySolution",
        "ansys.solutions.solution_with_ui_in_ansys.solution.definition",
        ui_module="ansys.solutions.solution_with_ui_in_ansys.ui.app",
    )


def test_func_analysis_of_solution_using_path_with_ui_is_valid(tmp_path: Path):
    # Requirements:
    # - to have /ansys/solutions/ in the file path
    # - default `definition`/`app` imports in main
    env = _copy_solution_to_ansys_dir(tmp_path, MOCKS_DIR / "solution_with_ui_in_ansys")
    result = _run_func_analysis_using_solution_module(f"{env['SOLUTION_DIR']}/main.py")
    _verify_valid_result(
        result,
        "MySolution",
        "ansys.solutions.solution_with_ui_in_ansys.solution.definition",
        ui_module="ansys.solutions.solution_with_ui_in_ansys.ui.app",
    )


def test_cli_analysis_solution_using_path_without_ui(tmp_path: Path):
    # Requirements:
    # - to have /ansys/solutions/ in the file path
    # - default `definition`/`app` imports in main
    env = _copy_solution_to_ansys_dir(tmp_path, MOCKS_DIR / "solution_without_ui_in_ansys")
    result = _run_cli_analysis_using_glow_module(solution_name=f"{env['SOLUTION_DIR']}/main.py")
    _verify_valid_result(result, "MySolution", "ansys.solutions.solution_without_ui_in_ansys.solution.definition")


def test_func_analysis_solution_using_path_without_ui(tmp_path: Path):
    # Requirements:
    # - to have /ansys/solutions/ in the file path
    # - default `definition`/`app` imports in main
    env = _copy_solution_to_ansys_dir(tmp_path, MOCKS_DIR / "solution_without_ui_in_ansys")
    result = _run_func_analysis_using_solution_module(f"{env['SOLUTION_DIR']}/main.py")
    _verify_valid_result(result, "MySolution", "ansys.solutions.solution_without_ui_in_ansys.solution.definition")


def test_cli_analysis_solution_using_path_without_ansys_solutions():
    solution_main_file = MOCKS_DIR / "solution_with_ui" / "main.py"
    args = [
        sys.executable,
        "-m",
        "ansys.saf.glow.cli",
        "analysis",
        "--solution",
        str(solution_main_file),
    ]
    p = subprocess.run(args, stderr=subprocess.PIPE)
    assert f"Error: {_AUTODISCOVERY_ENV_VARS_ERROR}" in p.stderr.decode("utf8")


def test_cli_analysis_solution_using_autodiscovery_with_ui_is_valid(tmp_path: Path):
    # Requirements:
    # - to have the solution in ansys.solutions namespace
    # - added to the pythonpath
    # - default `definition`/`app` imports in main
    env = _copy_solution_to_ansys_dir(tmp_path, MOCKS_DIR / "solution_with_ui_in_ansys")
    result = _run_cli_analysis_using_glow_module(env=env)
    _verify_valid_result(
        result,
        "MySolution",
        "ansys.solutions.solution_with_ui_in_ansys.solution.definition",
        ui_module="ansys.solutions.solution_with_ui_in_ansys.ui.app",
    )


def test_cli_analysis_solution_using_autodiscovery_without_ui(tmp_path: Path):
    # Requirements:
    # - to have the solution in ansys.solutions namespace
    # - added to the pythonpath
    # - default `definition`/`app` imports in main
    env = _copy_solution_to_ansys_dir(tmp_path, MOCKS_DIR / "solution_without_ui_in_ansys")
    result = _run_cli_analysis_using_glow_module(env=env)
    _verify_valid_result(result, "MySolution", "ansys.solutions.solution_without_ui_in_ansys.solution.definition")
