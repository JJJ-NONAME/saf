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

import argparse
import importlib
import logging
import os
from pathlib import Path
import shutil
import sys
import tempfile
from uuid import uuid4
from zipfile import ZipFile

from dotenv import load_dotenv

from ansys.saf.desktop.orchestrator._config.schema import Settings
from ansys.saf.desktop.orchestrator._orchestration.run_solution_stack import run_solution_stack

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


def _discover_solution_parts(solution_src_dir: Path) -> list[tuple[str, ...]]:
    discovered_solution_parts: list[tuple[str, ...]] = []
    for main_path in sorted(path for path in solution_src_dir.rglob("main.py") if path.is_file()):
        package_parts = main_path.relative_to(solution_src_dir).parts[:-1]
        if len(package_parts) < 2:
            continue

        discovered_solution_parts.append(package_parts)

    if not discovered_solution_parts:
        raise ValueError(
            f"No solution module found under {solution_src_dir}. Expected at least one package entrypoint.",
        )
    return discovered_solution_parts


def _validate_importable_solution(
    solution_src_dir: Path,
    solution_parts: tuple[str, ...],
) -> Exception | None:
    solution_module = f"{'.'.join(solution_parts)}.main"
    expected_main_path = solution_src_dir.joinpath(*solution_module.split(".")).with_suffix(".py").resolve()
    try:
        imported_main = importlib.import_module(solution_module)
        imported_main_file = imported_main.__file__
        if imported_main_file is None:
            raise ImportError(f"Imported module {solution_module} does not define __file__.")
        imported_main_path = Path(str(imported_main_file)).resolve()
    except (ImportError, ModuleNotFoundError, AttributeError) as exc:
        return exc

    if imported_main_path != expected_main_path:
        raise ImportError(
            f"Solution module {solution_module} does not point to the correct solution file. "
            f"Imported {imported_main_path}, expected {expected_main_path}.",
        )
    return None


def _raise_no_importable_solution(
    solution_src_dir: Path,
    discovered_solution_parts: list[tuple[str, ...]],
    import_errors: list[tuple[str, Exception]],
) -> None:
    discovered_modules = ", ".join(f"{'.'.join(parts)}.main" for parts in discovered_solution_parts)
    details = "\n".join(f"- {module_name}: {exc}" for module_name, exc in import_errors)
    raise ValueError(
        f"No importable solution module found under {solution_src_dir}. Discovered: {discovered_modules}."
        f"\nImport errors:\n{details}",
    )


def _raise_multiple_importable_solutions(
    solution_src_dir: Path,
    importable_solution_parts: list[tuple[str, ...]],
) -> None:
    error_message = "Multiple importable solutions found:\n"
    for module_parts in importable_solution_parts:
        solution_dir = solution_src_dir.joinpath(*module_parts)
        error_message += f"- Found module {'.'.join(module_parts)} at {solution_dir}\n"
    error_message += "Only one solution is expected in the src directory."
    raise ValueError(error_message)


def _resolve_solution_package(solution_src_dir: Path) -> tuple[tuple[str, ...], str]:
    """Find a single importable solution package under ``src/**/main.py``.

    Returns
    -------
    tuple[tuple[str, ...], str]
        Namespace path parts and solution module name.
    """
    if not solution_src_dir.is_dir():
        raise NotADirectoryError(f"Solution source directory not found at {solution_src_dir}")

    discovered_solution_parts = _discover_solution_parts(solution_src_dir)
    importable_solution_parts: list[tuple[str, ...]] = []
    import_errors: list[tuple[str, Exception]] = []
    for solution_parts in discovered_solution_parts:
        solution_module = f"{'.'.join(solution_parts)}.main"
        validation_error = _validate_importable_solution(solution_src_dir, solution_parts)
        if validation_error is not None:
            import_errors.append((solution_module, validation_error))
            continue

        importable_solution_parts.append(solution_parts)

    if not importable_solution_parts:
        _raise_no_importable_solution(solution_src_dir, discovered_solution_parts, import_errors)
    if len(importable_solution_parts) > 1:
        _raise_multiple_importable_solutions(solution_src_dir, importable_solution_parts)

    solution_parts = importable_solution_parts[0]

    namespace_root_parts = solution_parts[:-1]
    solution_module_name = solution_parts[-1]
    return namespace_root_parts, solution_module_name


def run_solution():
    """Run the specified solution.

    Parameters
    ----------
    solution_path: Path
        the location of the archive file containing the solution.
    """
    parser = argparse.ArgumentParser(description="Solution App Starter")
    parser.add_argument("solution_path", type=Path)
    parser.add_argument("--log-to-files", action="store_true", help="Log to files and disable OTEL dashboard.")
    args = parser.parse_args()
    solution_path: Path = args.solution_path
    log_to_files: bool = args.log_to_files

    solution_dir = solution_path.resolve() / "src"
    if solution_path.is_file():
        temp_solution_dir = Path(tempfile.mkdtemp())
        logger.info(f"Extracting solution to temp directory {temp_solution_dir}...")
        with ZipFile(solution_path, "r") as archive:
            archive.extractall(temp_solution_dir)
        solution_dir = temp_solution_dir / "src"

    # Append solution dir to path. Also update environ var, for GLOW subprocesses.
    # We put the solution_dir first in PATH, in case there is another solution available with the
    # same name to make sure that we load the extracted one.
    sys.path.insert(0, str(solution_dir))
    os.environ["PYTHONPATH"] = os.pathsep.join(sys.path)
    logger.info(f"Added solution directory {solution_dir} to PYTHONPATH.")

    namespace_root_parts, solution_name = _resolve_solution_package(solution_dir)
    solution_module = f"{'.'.join(namespace_root_parts)}.{solution_name}.main"
    solution_file = solution_dir.joinpath(*solution_module.split(".")).with_suffix(".py")
    logger.info(f"Loading solution in file {solution_file}")
    # Projects don't interact with each other, we could reuse the same always...
    tmp_appdata_path = tempfile.mkdtemp(prefix="saf_")
    os.environ["APPDATA"] = tmp_appdata_path  # type: ignore
    os.environ["XDG_DATA_HOME"] = tmp_appdata_path  # type: ignore
    os.environ["GLOW_METHOD_EXECUTION_DIRECTORY"] = tmp_appdata_path  # type: ignore
    logger.info(f"APPDATA set to {tmp_appdata_path}.")

    # display_name is not unique, we could reuse the same always...
    project_display_name = str(uuid4())
    logger.info(f"Starting project with display_name {project_display_name}...")

    try:
        env_file = solution_dir.parent / ".env"
        if env_file.is_file():
            logger.info(f"Found environment file {env_file}.")
            logger.info(f"Loading environment variables from {env_file.resolve()}")
            load_dotenv(dotenv_path=env_file.resolve())
        # Use Settings to get proper boolean parsing from environment
        temp_settings = Settings(saf_desktop_solution_name="temp")
        log_to_files = log_to_files or temp_settings.saf_desktop_log_to_files
        run_solution_stack(
            solution_main_module_name=solution_module,
            input_project_display_name=project_display_name,
            log_to_files=log_to_files,
        )
    finally:
        # Flush and close all handlers to avoid permission errors while deleting log files.
        logging.shutdown()
        shutil.rmtree(tmp_appdata_path, ignore_errors=True)


if __name__ == "__main__":
    run_solution()
