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

import ast
import os
from pathlib import Path
import platform

from ansys.saf.cli._database.manager import SolutionDatabaseManager


def find_solution_root_dir(db_manager: SolutionDatabaseManager, solution: str) -> Path:
    """Find the source directory of the solution given a str that can be:
    - the name of a valid registered solution
    - the path to a solution directory
    - empty string, thus pointing to the current working directory.
    """
    if not solution:
        solution_root_dir = Path.cwd()
    registered_solutions = db_manager.get_solutions_by_name(solution)
    if not registered_solutions:
        solution_root_dir = Path(solution).expanduser().resolve()
        if not solution_root_dir.is_dir():
            raise NotADirectoryError(f"Solution not found at {solution_root_dir}")
    elif len(registered_solutions) > 1:
        error_message = f"Multiple solutions found with the name {solution}."
        for registered_solution in registered_solutions:
            error_message += f"\n- Found {registered_solution.name} at {registered_solution.root_dir}"
        error_message += (
            "\nHint: You can specify the correct one by using the full path to the solution as follows:\n"
            "saf <command> /full/path/to/your-solution/"
        )
        raise ValueError(error_message)
    else:
        solution_root_dir = registered_solutions[0].root_dir

    return solution_root_dir


def resolve_solution_main_file(solution_root_dir: Path) -> Path:
    """Find the main file of the solution given the solution directory.

    Searches for a main.py file under src/ at any namespace depth.
    If not found, falls back to searching for main.pyc.
    Expected structure: src/<namespace_path>/<solution_name>/main.py
    """
    solution_src_dir = solution_root_dir / "src"
    if not solution_src_dir.is_dir():
        raise NotADirectoryError(f"Solution source directory not found at {solution_src_dir}")

    main_files = sorted(solution_src_dir.glob("**/main.py"))
    if not main_files:
        main_files = sorted(solution_src_dir.glob("**/main.pyc"))

    if not main_files:
        raise FileNotFoundError(
            f"Solution main file not found under {solution_src_dir}. "
            f"Expected structure: src/<namespace_path>/<solution_name>/main.py",
        )
    if len(main_files) > 1:
        error_message = "Multiple main files found:\n"
        for main_file in main_files:
            error_message += f"- Found {main_file}\n"
        error_message += "Only one solution is expected in the src directory."
        raise ValueError(error_message)

    return main_files[0]


def _get_solution_module_parts(solution_main_file: Path) -> list[str]:
    """Return the dotted-module path parts after the src directory."""
    resolved_path = solution_main_file.resolve()

    try:
        src_index = resolved_path.parts.index("src")
    except ValueError:
        raise RuntimeError(f"Could not find 'src' in path: {resolved_path}") from None

    module_parts = list(resolved_path.parts[src_index + 1 :])
    if not module_parts:
        raise RuntimeError(f"Could not build module path from: {resolved_path}")

    module_parts[-1] = Path(module_parts[-1]).stem
    return module_parts


def get_main_module(solution_main_file: Path) -> str:
    """Get the main module for a Solution and, optionally, validate that it is correct. Raises an exception
    if a Solution main module is not found.

    Parameters
    ----------
    solution_main_file : Path
        The path of the Solution main file (e.g., <org>/solutions/<solution_name>/main.py).

    Returns
    -------
        str
            The main module str (e.g., my_company.solutions.my_solution.main)
    """
    return ".".join(_get_solution_module_parts(solution_main_file))


def find_solution_display_name(solution_main_file: Path) -> str | None:
    # we cannot import the solution, since the CLI env doesn't have the solution dependencies
    # We fallback then to parsing the definition.py file, which doesn't work for compiled solutions
    # shouldn't be an issue since src directories are not typically compiled.
    definition_file = solution_main_file.parent / "solution" / "definition.py"
    if not definition_file.is_file():
        return None

    display_name: str | None = None
    tree = ast.parse(definition_file.read_text())
    class_definitions = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    for class_def in class_definitions:
        if any(base.id == "Solution" for base in class_def.bases):  # pyright: ignore
            assignments = [node for node in class_def.body if isinstance(node, ast.AnnAssign)]
            for assignment in assignments:
                if assignment.target.id == "display_name":  # pyright: ignore
                    display_name = str(assignment.value.value)  # pyright: ignore
                    break
            break
    return display_name


def get_solution_venv_bin_dir(solution_root_dir: Path) -> Path:
    if platform.system() == "Windows":
        solution_venv_bin_dir = solution_root_dir / ".venv" / "Scripts"
    elif platform.system() == "Linux":
        solution_venv_bin_dir = solution_root_dir / ".venv" / "bin"
    else:
        raise ValueError("Unsupported operating system")
    return solution_venv_bin_dir


def get_exec_from_solution_venv(solution_root_dir: Path, exec_name: str) -> Path:
    solution_venv_bin_dir = get_solution_venv_bin_dir(solution_root_dir)
    if platform.system() == "Windows":
        exec_path = solution_venv_bin_dir / f"{exec_name}.exe"
    elif platform.system() == "Linux":
        exec_path = solution_venv_bin_dir / exec_name
    else:
        raise ValueError("Unsupported operating system")
    if not exec_path.is_file():
        raise FileNotFoundError(f"Executable not found at {exec_path}")
    return exec_path


def create_solution_environment(solution_root_dir: Path) -> dict[str, str]:
    solution_env = os.environ.copy()
    # Poetry will always pick the active python environment (the environment in variable VIRTUAL_ENV) when managing
    # dependencies. Removing this environment variable lets poetry use the solution's environment.
    solution_env.pop("VIRTUAL_ENV", None)
    # so internal calls to tools (e.g., poetry and sphinx in installer) resolve first to the binaries in the
    # solution's venv instead of the ones in the SAF-CLI's venv or global ones. This doesn't seem to work with others
    # such as python/pip. See _get_executable_absolute_path.
    solution_env["PATH"] = os.pathsep.join(
        [str(get_solution_venv_bin_dir(solution_root_dir)), solution_env.get("PATH", "")],
    )
    return solution_env
