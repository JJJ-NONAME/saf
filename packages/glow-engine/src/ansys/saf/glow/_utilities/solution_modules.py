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
import importlib
import importlib.util
import inspect
import logging
import os
from pathlib import Path
import sys
import traceback
from types import ModuleType

import click

from ansys.saf.glow._core.exceptions import SolutionLoadException
from ansys.saf.glow._core.solution import Solution
from ansys.saf.glow._utilities.code import is_compiled

logger = logging.getLogger(__name__)

_ANSYS_SOLUTIONS_NOT_FOUND_ERROR = "The package 'ansys.solutions' was not found."
_AUTODISCOVERY_ENV_VARS_ERROR = (
    "Failed to discover solution modules. Set GLOW_SOLUTION_DEFINITION and GLOW_UI_MODULE environment variables."
)


def _raise_autodiscovery_env_vars_error_if_needed(error: RuntimeError) -> None:
    if str(error) == _ANSYS_SOLUTIONS_NOT_FOUND_ERROR:
        raise RuntimeError(_AUTODISCOVERY_ENV_VARS_ERROR) from None


def find_solution(definition_module: ModuleType) -> type[Solution]:
    solution_classes = [
        value
        for _, value in inspect.getmembers(
            definition_module,
            lambda x: inspect.isclass(x) and issubclass(x, Solution) and x != Solution,
        )
    ]

    if not solution_classes:
        raise SolutionLoadException("The solution definition module does not define a 'Solution' class.")

    if len(solution_classes) > 1:
        raise SolutionLoadException("The solution definition module defines more than one 'Solution' class.")

    solution_class: type[Solution] = solution_classes[0]
    return solution_class


def find_solution_name(definition_module_str: str) -> str:
    definition_module = importlib.import_module(definition_module_str)
    solution = find_solution(definition_module)
    return solution.__name__


def get_main_module(solution: str | None = None, validate_module: bool = False) -> str:
    """Get the main module for a Solution and, optionally, validate that it is correct. Raises an exception
    if a Solution main module is not found.

    Parameters
    ----------
    solution : str, optional
        The path (ansys/solutions/my_solution/main.py) or module name (ansys.solutions.my_solution.main)
        of the Solution main file. If not provided, it tries to autodiscover it.
    validate_module : bool, optional
        If True, the function validates that the identified main module is importable.

    Returns
    -------
        str
            The main module str (e.g., ansys.solutions.my_solution.main)
    """
    main_module_str, _ = _get_main_module_and_path(solution, validate_module)
    return main_module_str


def _get_main_module_and_path(solution: str | None = None, validate_module: bool = False) -> tuple[str, Path | None]:
    """Retrieve the main module associated with a Solution and its path.
    Importing the module is kept optional.
    Raises an exception if a Solution main module is not found.

    Possible scenarios:
    1. Called with a solution parameter that can be:
        a. a module string pointing to a compiled or regular module
        b. a file path to a compiled or regular python file
    2. Called without any data, relying on the autodiscovery feature.

    Notes
    -----
    - If passing a file path, it must contain "/ansys/solutions/".
    - If passing a module name, the main solution file must contain a "definition" import that points to the solution
      definition module.
    - If using autodiscovery, the solution must be in the "ansys.solutions" package and have the "definition" import
      in the main file.
    - TODO: If validation is disabled,
    """
    if solution:
        main_module_str, main_module_path = _get_main_module_from_solution_param(solution, validate_module)
    else:
        main_module_str, main_module_path = _find_main_module(validate_module)
    return main_module_str, main_module_path


def get_definition_module(
    ctx: click.Context,
    definition: str | None = None,
    solution: str | None = None,
    validate_module: bool = False,
) -> ModuleType:
    """Retrieve the definition module associated with a Solution.
    Importing other modules is kept optional to avoid bringing undesired dependencies.
    Raises an exception if a valid loadable definition module is not found.

    Possible scenarios:
    1. Called from a solution, passing the module as click's context.
    2. Called with a definition parameter that can be:
        a. a module string pointing to a compiled or regular module
        b. a file path to a compiled or regular python file
    3. Called with a solution parameter that can be:
        a. a module string pointing to a compiled or regular module
        b. a file path to a compiled or regular python file
    4. Called without any data, relying on the autodiscovery feature.

    Notes
    -----
    - If passing a file path, it must contain "/ansys/solutions/".
    - If passing a solution, the main solution file must contain a "definition" import that points to the solution
      definition module.
    - If using autodiscovery, the solution must be in the "ansys.solutions" package and have the "definition" import
      in the main file.
    - TODO: If validation is disabled,
    """
    definition_module = _get_definition_module_from_click_context(ctx)
    if definition_module:
        return definition_module
    if definition:
        return _get_definition_module_from_definition_param(definition)
    return get_definition_module_from_solution_param(solution, validate_module)


def _get_definition_module_from_click_context(ctx: click.Context) -> ModuleType | None:
    if hasattr(ctx.obj, "definition_module") and ctx.obj.definition_module is not None:
        return ctx.obj.definition_module
    return None


def _get_definition_module_from_definition_param(definition: str) -> ModuleType:
    if definition.endswith((".py", ".pyc")):
        definition_module_str = _convert_module_path_to_module_str(definition)
    else:
        definition_module_str = definition
    try:
        return importlib.import_module(definition_module_str)
    except Exception as e:
        raise RuntimeError(
            f"The solution definition module cannot be omitted in this configuration or mode: {e}",
        ) from None


def get_definition_module_from_solution_param(
    solution: str | None = None,
    validate_module: bool = False,
) -> ModuleType:
    if solution:
        main_module_str, main_module_path = _get_main_module_from_solution_param(solution, validate_module)
    else:
        try:
            main_module_str, main_module_path = _find_main_module(validate_module)
        except RuntimeError as error:
            _raise_autodiscovery_env_vars_error_if_needed(error)
            raise
    if not main_module_path and validate_module:
        # if input was a module namespace instead of a filepath
        spec = importlib.util.find_spec(main_module_str)
        if spec and spec.origin:
            main_module_path = Path(spec.origin)
    definition_module_str = _get_import_from_main_module(
        main_module_str,
        "definition",
        main_module_path,
        validate_module,
    )
    if not definition_module_str:
        # assume typical structure where main solution file is my_solution.X and
        # definition is my_solution.solution.definition
        definition_module_str = ".".join(main_module_str.split(".")[:-1] + ["solution", "definition"])
    try:
        return importlib.import_module(definition_module_str)
    except Exception as e:
        raise RuntimeError(
            f"The solution definition module cannot be omitted in this configuration or mode: {e}",
        ) from None


def get_autodiscovery_definition_module_str() -> str:
    """
    Find and return definition module str. It must NOT import the main module while finding it,
    to avoid loading the UI dependencies.
    Raise an exception if the definition is not found.
    """
    try:
        main_module_str, main_module_path = _find_main_module(validate_module=False)
    except RuntimeError as error:
        _raise_autodiscovery_env_vars_error_if_needed(error)
        raise
    definition_module_str = _get_import_from_main_module(
        main_module_str,
        "definition",
        main_module_path,
        validate_module=False,
    )
    if definition_module_str is None:
        raise RuntimeError("The solution definition module cannot be found.")
    return definition_module_str


def get_ui_module(ctx: click.Context, solution: str | None = None) -> ModuleType | None:
    """Retrieve the UI module associated with a Solution. Validation is enabled since
    importing definition dependencies is not an issue due to the UI being an extra layer added
    over the definition environment.
    Does NOT raise an exception if a valid loadable UI module is not found.

    Possible scenarios:
    1. Called from a solution, passing the module as click's context.
    2. Called with a solution parameter that can be:
        a. a module string pointing to a compiled or regular module
        b. a file path to a compiled or regular python file
    3. Called without any data, relying on the autodiscovery feature.

    Notes
    -----
    - If passing a file path, it must contain "/ansys/solutions/".
    - If passing a solution, the main solution file must contain an "app" import that points to the solution
      UI module.
    - If using autodiscovery, the solution must be in the "ansys.solutions" package and have the "app" import
      in the main file.
    """
    ui_module = _get_ui_module_from_click_context(ctx)
    if ui_module:
        return ui_module
    return get_ui_module_from_solution_param(solution)


def _get_ui_module_from_click_context(ctx: click.Context) -> ModuleType | None:
    if hasattr(ctx.obj, "ui_module") and ctx.obj.ui_module is not None:
        return ctx.obj.ui_module
    return None


def _get_ui_module_from_solution_param(solution: str | None = None) -> ModuleType | None:
    if solution:
        main_module_str, main_module_path = _get_main_module_from_solution_param(solution, validate_module=True)
    else:
        main_module_str, main_module_path = _find_main_module(validate_module=True)
    if not main_module_path:
        # if input was a module namespace instead of a filepath
        spec = importlib.util.find_spec(main_module_str)
        if spec and spec.origin:
            main_module_path = Path(spec.origin)
    ui_module_str = _get_import_from_main_module(main_module_str, "app", main_module_path, validate_module=True)
    if not ui_module_str:
        # assume typical structure where main solution file is my_solution.X and
        # definition is my_solution.ui.app
        ui_module_str = ".".join(main_module_str.split(".")[:-1] + ["ui", "app"])
    return importlib.import_module(ui_module_str)


def get_ui_module_from_solution_param(solution: str | None = None) -> ModuleType | None:
    try:
        return _get_ui_module_from_solution_param(solution)
    except Exception:
        return


def get_autodiscovery_ui_module_str() -> str | None:
    try:
        main_module_str, main_module_path = _find_main_module(validate_module=True)
    except RuntimeError:
        # UI module is optional — return None for all autodiscovery failures, including when
        # ansys.solutions is absent (the definition path handles that error for required startup).
        return None
    ui_module_str = _get_import_from_main_module(main_module_str, "app", main_module_path, validate_module=True)
    if not ui_module_str:
        # assume typical structure where main solution file is my_solution.X and
        # definition is my_solution.ui.app
        ui_module_str = ".".join(main_module_str.split(".")[:-1] + ["ui", "app"])
    return ui_module_str


def _verify_main_module(
    main_module_str: str,
    main_module_path: Path | None = None,
    validate_module: bool = False,
) -> None:
    # Find glow_main import, as described in src/ansys/saf/glow/runtime.py
    if main_module_path and not is_compiled(main_module_path):
        if _get_import_from_python_file(main_module_path, "glow_main") is None:
            raise RuntimeError(f"{main_module_str} does not contain a definition of glow_main which is callable.")
        if validate_module:
            try:
                importlib.import_module(main_module_str)
            except Exception:
                raise RuntimeError(f"{main_module_str} could not be loaded. {traceback.format_exc()}") from None
    elif validate_module:
        if not _verify_glow_main_in_module(main_module_str):
            raise RuntimeError(f"{main_module_str} does not contain a definition of glow_main which is callable.")
    # Cannot be verified without importing it,
    # assuming that it is correct because of the module structure (main_module_str == my_solution.main)


def _get_main_module_from_solution_param(solution: str, validate_module: bool = False) -> tuple[str, Path | None]:
    main_module_path: Path | None = None
    if solution.endswith((".py", ".pyc")):
        main_module_path = Path(solution)
        main_module_str = _convert_module_path_to_module_str(solution)
    else:
        main_module_str = solution
    _verify_main_module(main_module_str, main_module_path, validate_module)
    return main_module_str, main_module_path


def _find_main_module(validate_module: bool = False) -> tuple[str, Path]:
    spec = importlib.util.find_spec("ansys.solutions")
    if not spec or not spec.submodule_search_locations:
        raise RuntimeError(_ANSYS_SOLUTIONS_NOT_FOUND_ERROR) from None

    ansys_solutions_module_paths = spec.submodule_search_locations
    solution_directories = [
        solution_dir
        for ansys_solutions_module_path in ansys_solutions_module_paths
        for solution_dir in Path(ansys_solutions_module_path).iterdir()
        if solution_dir.is_dir()
    ]
    # there can be duplicates in spec.submodule_search_locations which triggers an exception
    # of multiple solutions.
    solution_directories = list(set(solution_directories))

    main_modules: list[tuple[str, Path]] = []
    reasons: list[str] = []
    solution_dirs_missing_main: list[str] = []
    for solution_dir in solution_directories:
        main_module_path = solution_dir / "main.py"
        if not main_module_path.is_file():
            main_module_path = main_module_path.with_suffix(".pyc")
        if not main_module_path.is_file():
            solution_dirs_missing_main.append(str(solution_dir))
            continue
        main_module_str = _convert_module_path_to_module_str(str(main_module_path))
        try:
            _verify_main_module(main_module_str, main_module_path, validate_module)
            main_modules.append((main_module_str, main_module_path))
        except Exception as e:
            reasons.append(str(e))
            continue

    if not solution_directories:
        reasons.append(
            "There are no solutions defined within ansys.solutions.\n"
            "Create a 'main' module in a package within 'ansys.solutions'.",
        )
    if not main_modules:
        if not reasons and solution_dirs_missing_main:
            solution_dirs_missing_main_str = "\n" + "\n".join(solution_dirs_missing_main)
            reasons.append(
                "None of the following directories contain main.py "
                f"or main.pyc files:{solution_dirs_missing_main_str}.",
            )
        reasons_str = "\n" + "\n".join(reasons)
        raise RuntimeError(
            f"Failed to find a viable solution entry point.{reasons_str}\n"
            "Correct the above errors or use the '--solution' option to specify a solution entry point module.",
        )
    if len(main_modules) > 1:
        raise RuntimeError(
            "Detected multiple solution entry points in ansys.solutions module."
            " Use the '--solution' option to specify the solution entry point module that "
            "should be utilized.",
        )
    return main_modules[0]


def _convert_module_path_to_module_str(module_path: str) -> str:
    """Take an absolute path, extract the solution package path from the path,
    add the root package to sys.path and return the module."""
    filepath = (Path.cwd() / module_path).resolve().as_posix()  # handle both absolute and relative solution path.
    ansys_solution_folder = "/ansys/solutions/"
    try:
        ansys_index = filepath.rindex(ansys_solution_folder)
    except ValueError:
        raise RuntimeError(_AUTODISCOVERY_ENV_VARS_ERROR) from None
    # now translate /ansys/solutions/x/y.py to ansys.solutions.x.y.py[c]
    module_str = filepath[ansys_index + 1 :].replace("/", ".")
    # remove .py/.pyc extension
    module_str = ".".join(module_str.split(".")[:-1])
    # add root path to sys.path if necessary
    root_path = str(Path(filepath[:ansys_index]).absolute())
    if root_path not in sys.path:
        sys.path.append(root_path)
        os.environ["PYTHONPATH"] = os.pathsep.join(sys.path)
    return module_str


def _get_import_from_main_module(
    main_module_str: str,
    import_name: str,
    main_module_path: Path | None = None,
    validate_module: bool = False,
) -> str | None:
    if main_module_path and not is_compiled(main_module_path):
        return _get_import_from_python_file(main_module_path, import_name)
    elif validate_module:
        return _get_import_from_module(main_module_str, import_name)
    return None


def _verify_glow_main_in_module(module_str: str) -> bool:
    try:
        module = importlib.import_module(module_str)
    except Exception:
        raise RuntimeError(f"{module_str} could not be loaded. {traceback.format_exc()}") from None
    glow_main = getattr(module, "glow_main", None)
    return bool(glow_main and callable(glow_main))


def _get_import_from_module(module_str: str, import_name: str) -> str | None:
    try:
        module = importlib.import_module(module_str)
    except Exception:
        raise RuntimeError(f"{module_str} could not be loaded. {traceback.format_exc()}") from None
    for name, value in inspect.getmembers(module):
        if name != import_name:
            continue
        if not inspect.ismodule(value):
            continue
        return value.__name__
    return None


def _get_import_from_python_file(module_path: Path, import_name: str) -> str | None:
    try:
        tree = ast.parse(module_path.read_text())
    except Exception:
        raise RuntimeError(f"{module_path} could not be parsed. {traceback.format_exc()}") from None
    for item in tree.body:
        if isinstance(item, ast.ImportFrom) and item.module:
            for alias in item.names:
                # Supports cases:
                # - from my_solution.solution import {import_name}
                # - from my_solution.solution import Z as {import_name}
                if alias.asname == import_name or alias.name == import_name:
                    return item.module + f".{alias.name}"
        elif isinstance(item, ast.Import):
            for alias in item.names:
                if alias.asname == import_name or alias.name.endswith(f".{import_name}"):
                    # Supports cases:
                    # - import my_solution.solution.Z as {import_name}
                    # - import my_solution.solution.{import_name}
                    return alias.name
    return None
