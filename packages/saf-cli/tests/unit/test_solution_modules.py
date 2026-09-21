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
import re
import uuid

import click
import pytest
import pytest_mock

from ansys.saf.cli._cli.main import _validate_namespace_root  # pyright: ignore[reportPrivateUsage]
from ansys.saf.cli._database.manager import SolutionDatabaseManager
from ansys.saf.cli._database.models import SolutionRegistry
from ansys.saf.cli._utilities.solution_modules import (
    find_solution_display_name,
    find_solution_root_dir,
    get_exec_from_solution_venv,
    get_main_module,
    resolve_solution_main_file,
)


@pytest.mark.parametrize(
    "namespace",
    ["mynamespace", "org.project", "org.project_module"],
)
def test_validate_namespace_root(namespace: str):
    ctx = click.Context(click.Command("test"))
    param = click.Option(["--namespace"])
    assert _validate_namespace_root(ctx, param, namespace) == namespace


@pytest.mark.parametrize(
    ("namespace", "expected_error"),
    [
        (" ", "cannot be empty or just whitespace"),
        ("MyOrg.project", "must be lowercase"),
        ("my-org.project", "can contain only lowercase letters, numbers, and underscores"),
        ("my/org.project", "can contain only lowercase letters, numbers, and underscores"),
        ("my org.project", "can contain only lowercase letters, numbers, and underscores"),
        (".myorg.project", "must not start or end with a dot"),
        ("myorg.project.", "must not start or end with a dot"),
        ("myorg..project", "must not contain empty segments"),
        ("123org.project", "must start with a letter or underscore"),
        ("org.class", "is a Python keyword and is not allowed"),
    ],
)
def test_validate_namespace_root_invalid(namespace: str, expected_error: str):
    ctx = click.Context(click.Command("test"))
    param = click.Option(["--namespace"])
    with pytest.raises(click.BadParameter, match=re.escape(expected_error)):
        _validate_namespace_root(ctx, param, namespace)


def test_find_solution_dir_with_existing_solution_name(tmp_path: Path):
    # Register a solution in the database
    db = SolutionDatabaseManager()
    db.store_solution(
        SolutionRegistry(
            name="my_solution",
            root_dir=tmp_path,
            display_name="My Solution",
        ),
    )

    # Find the solution directory
    assert find_solution_root_dir(db, "my_solution") == tmp_path


def test_find_solution_dir_with_existing_solution_name_of_invalid_solution(tmp_path: Path):
    # Register a solution in the database with an inexistent path, which results in an invalid solution
    invalid_solution = SolutionRegistry(
        name=str(uuid.uuid4()),
        root_dir=(tmp_path / "a"),
        display_name="My Solution",
    )
    assert not invalid_solution.is_valid
    db = SolutionDatabaseManager()
    db.store_solution(invalid_solution)

    # Solution cannot be found
    expected_path = Path(invalid_solution.name).expanduser().resolve()
    with pytest.raises(
        NotADirectoryError,
        match=re.escape(f"Solution not found at {expected_path}"),
    ):
        find_solution_root_dir(db, invalid_solution.name)


def test_find_solution_dir_with_duplicated_solution_name(tmp_path: Path):
    # Register a couple of solution in the database with the same name
    solution_root_dir_a = tmp_path / "a"
    solution_root_dir_a.mkdir()
    solution_root_dir_b = tmp_path / "b"
    solution_root_dir_b.mkdir()
    db = SolutionDatabaseManager()
    db.store_solution(
        SolutionRegistry(
            name="my_solution",
            root_dir=solution_root_dir_a,
            display_name="My Solution",
        ),
    )
    db.store_solution(
        SolutionRegistry(
            name="my_solution",
            root_dir=solution_root_dir_b,
            display_name="My Solution",
        ),
    )

    # Find the solution directory
    with pytest.raises(ValueError, match="Multiple solutions found with the name my_solution") as exc_info:
        find_solution_root_dir(db, "my_solution")

    error_message = str(exc_info.value)
    assert f"- Found my_solution at {solution_root_dir_a}" in error_message
    assert f"- Found my_solution at {solution_root_dir_b}" in error_message
    assert "Hint: You can specify the correct one by using the full path" in error_message


def test_find_solution_dir_with_duplicated_solution_name_and_one_invalid(tmp_path: Path):
    # Register a couple of solution in the database with the same name, only one of them is valid
    solution_root_dir_a = tmp_path / "a"
    solution_root_dir_a.mkdir()
    solution_root_dir_b = tmp_path / "b"
    db = SolutionDatabaseManager()
    db.store_solution(
        SolutionRegistry(
            name="my_solution",
            root_dir=solution_root_dir_a,
            display_name="My Solution",
        ),
    )
    db.store_solution(
        SolutionRegistry(
            name="my_solution",
            root_dir=solution_root_dir_b,
            display_name="My Solution",
        ),
    )

    # Find the solution directory
    assert solution_root_dir_a == find_solution_root_dir(db, "my_solution")


def test_find_solution_dir_with_inexistent_solution_name_and_path():
    # Register a solution in the database
    db = SolutionDatabaseManager()

    # Find the solution directory
    solution_name = str(uuid.uuid4())
    expected_path = Path(solution_name).expanduser().resolve()
    with pytest.raises(NotADirectoryError, match=re.escape(f"Solution not found at {expected_path}")):
        find_solution_root_dir(db, solution_name)


@pytest.mark.usefixtures("tmp_path_as_working_dir")
def test_find_solution_dir_with_solution_name_preferred_over_path(tmp_path: Path):
    # Create a solution dir in the CWD
    solution_name = str(uuid.uuid4())
    solution_dir = Path.cwd() / solution_name
    solution_dir.mkdir(parents=True, exist_ok=True)

    # Register a solution in the database with the same name but a different path
    db = SolutionDatabaseManager()
    (tmp_path / "a").mkdir(parents=True, exist_ok=True)
    db.store_solution(
        SolutionRegistry(
            name=solution_name,
            root_dir=(tmp_path / "a"),
            display_name="My Solution",
        ),
    )

    # Find the solution directory
    assert find_solution_root_dir(db, solution_name) == tmp_path / "a"


@pytest.mark.usefixtures("tmp_path_as_working_dir")
def test_find_solution_dir_with_relative_path():
    # Create a solution dir in the CWD
    solution_name = str(uuid.uuid4())
    solution_dir = Path.cwd() / solution_name
    solution_dir.mkdir(parents=True, exist_ok=True)

    # Empty db
    db = SolutionDatabaseManager()

    # Find the solution directory
    assert find_solution_root_dir(db, solution_name) == solution_dir


def test_find_solution_dir_with_absolute_path(tmp_path: Path):
    # Create a solution dir in the CWD
    solution_name = str(uuid.uuid4())
    solution_dir = tmp_path / solution_name
    solution_dir.mkdir(parents=True, exist_ok=True)

    # Empty db
    db = SolutionDatabaseManager()

    # Find the solution directory
    assert find_solution_root_dir(db, solution_dir.as_posix()) == solution_dir


def test_find_solution_dir_with_no_input_solution():
    # Empty db
    db = SolutionDatabaseManager()

    # Find the solution directory
    assert find_solution_root_dir(db, "") == Path.cwd()


def test_resolve_solution_main_file_with_valid_solution_dir(tmp_path: Path):
    # Create a valid solution directory structure
    solution_dir = tmp_path / "my_solution"
    solution_main_file = solution_dir / "src" / "ansys" / "solutions" / "my_solution" / "main.py"
    solution_main_file.parent.mkdir(parents=True, exist_ok=True)
    solution_main_file.touch()

    # Resolve the solution main file
    assert resolve_solution_main_file(solution_dir) == solution_main_file


def test_resolve_solution_main_file_with_valid_solution_dir_pyc(tmp_path: Path):
    # Create a valid solution directory structure with compiled entrypoint only
    solution_dir = tmp_path / "my_solution"
    solution_main_file = solution_dir / "src" / "ansys" / "solutions" / "my_solution" / "main.pyc"
    solution_main_file.parent.mkdir(parents=True, exist_ok=True)
    solution_main_file.touch()

    # Resolve the solution main file
    assert resolve_solution_main_file(solution_dir) == solution_main_file


def test_resolve_solution_main_file_with_missing_solution_src_dir(tmp_path: Path):
    # Create a solution directory without src directory
    solution_dir = tmp_path / "my_solution"
    solution_dir.mkdir(parents=True, exist_ok=True)

    # Attempt to resolve the solution main file
    with pytest.raises(
        NotADirectoryError,
        match=re.escape(f"Solution source directory not found at {solution_dir / 'src'}"),
    ):
        resolve_solution_main_file(solution_dir)


def test_resolve_solution_main_file_with_missing_solutions_dir(tmp_path: Path):
    # Create a solution directory without any main.py file
    solution_dir = tmp_path / "my_solution"
    (solution_dir / "src" / "ansys").mkdir(parents=True, exist_ok=True)

    # Attempt to resolve the solution main file
    with pytest.raises(
        FileNotFoundError,
        match=re.escape(
            f"Solution main file not found under {solution_dir / 'src'}. "
            f"Expected structure: src/<namespace_path>/<solution_name>/main.py",
        ),
    ):
        resolve_solution_main_file(solution_dir)


def test_resolve_solution_main_file_with_multiple_solutions(tmp_path: Path):
    # Create a solution directory with multiple main.py files
    solution_dir = tmp_path / "my_solution"
    solutions_dir = solution_dir / "src" / "ansys" / "solutions"
    solution_main_file = solutions_dir / "my_solution" / "main.py"
    solution_main_file.parent.mkdir(parents=True, exist_ok=True)
    solution_main_file.touch()
    solution_second_main_file = solutions_dir / "my_solution_twice" / "main.py"
    solution_second_main_file.parent.mkdir(parents=True, exist_ok=True)
    solution_second_main_file.touch()

    # Attempt to resolve the solution main file
    with pytest.raises(ValueError, match="Multiple main files found:"):
        resolve_solution_main_file(solution_dir)


def test_resolve_solution_main_file_with_no_solutions(tmp_path: Path):
    # Create a solution directory without any main.py file
    solution_dir = tmp_path / "my_solution"
    (solution_dir / "src" / "ansys" / "solutions").mkdir(parents=True, exist_ok=True)

    # Attempt to resolve the solution main file
    with pytest.raises(
        FileNotFoundError,
        match=re.escape(
            f"Solution main file not found under {solution_dir / 'src'}. "
            f"Expected structure: src/<namespace_path>/<solution_name>/main.py",
        ),
    ):
        resolve_solution_main_file(solution_dir)


def test_resolve_solution_main_file_with_missing_main_file(tmp_path: Path):
    # Create a solution directory without the main file
    solution_dir = tmp_path / "my_solution"
    (solution_dir / "src" / "ansys" / "solutions" / "my_solution").mkdir(parents=True, exist_ok=True)

    # Attempt to resolve the solution main file
    with pytest.raises(
        FileNotFoundError,
        match=re.escape(
            f"Solution main file not found under {solution_dir / 'src'}. "
            f"Expected structure: src/<namespace_path>/<solution_name>/main.py",
        ),
    ):
        resolve_solution_main_file(solution_dir)


def test_get_main_module_with_valid_solution_main_file():
    solution_main_file = Path("/tmp/my_solution/src/saf/solutions/my_solution/main.py")
    expected_module_str = "saf.solutions.my_solution.main"
    assert get_main_module(solution_main_file) == expected_module_str


def test_get_main_module_with_invalid_solution_main_file():
    solution_main_file = Path("/tmp/my_solution/src/saf/solutions/my_solution/main.pyc")
    expected_module_str = "saf.solutions.my_solution.main"
    assert get_main_module(solution_main_file) == expected_module_str


def test_get_main_module_with_invalid_solution_folder():
    solution_main_file = Path("/invalid/solutions/my_solution/main.py")
    with pytest.raises(RuntimeError):
        get_main_module(solution_main_file)


def test_get_exec_from_solution_venv(mocker: pytest_mock.MockFixture, tmp_path: Path):
    mocker.patch("platform.system", return_value="Windows")

    # Create a solution directory with a virtual environment
    solution_dir = tmp_path / "my_solution"
    executables_dir = solution_dir / ".venv" / "Scripts"
    executables_dir.mkdir(parents=True, exist_ok=True)
    python_exec = executables_dir / "python.exe"
    python_exec.touch()

    # Get the Python executable
    assert get_exec_from_solution_venv(solution_dir, "python") == python_exec


def test_get_exec_from_solution_venv_on_linux(mocker: pytest_mock.MockFixture, tmp_path: Path):
    mocker.patch("platform.system", return_value="Linux")

    # Create a solution directory with a virtual environment
    solution_dir = tmp_path / "my_solution"
    executables_dir = solution_dir / ".venv" / "bin"
    executables_dir.mkdir(parents=True, exist_ok=True)
    python_exec = executables_dir / "python"
    python_exec.touch()

    # Get the Python executable
    assert get_exec_from_solution_venv(solution_dir, "python") == python_exec


def test_get_exec_from_solution_venv_on_unsupported_os(mocker: pytest_mock.MockFixture, tmp_path: Path):
    mocker.patch("platform.system", return_value="Unsupported")

    # Attempt to get the Python executable
    with pytest.raises(ValueError, match="Unsupported operating system"):
        get_exec_from_solution_venv(tmp_path / "my_solution", "python")


def test_get_exec_from_solution_venv_with_missing_python_exec(tmp_path: Path):
    # Create a solution directory with a virtual environment
    solution_dir = tmp_path / "my_solution"
    venv_dir = solution_dir / ".venv"
    venv_dir.mkdir(parents=True, exist_ok=True)

    # Attempt to get the Python executable
    with pytest.raises(FileNotFoundError, match="Executable not found"):
        get_exec_from_solution_venv(solution_dir, "python")


def test_find_solution_display_name_no_definition_file(tmp_path: Path):
    main_file = tmp_path / "main.py"
    assert not find_solution_display_name(main_file)


def test_find_solution_display_name_compiled_definition_file(tmp_path: Path):
    main_file = tmp_path / "main.pyc"
    definition_file = tmp_path / "solution" / "definition.py"
    definition_file.parent.mkdir()
    definition_file.write_text(
        """
from ansys.saf.glow.solution import Solution

class MySolution(Solution):
    display_name: str = "My Test Name"
    """,
    )
    compiled_definition_file = definition_file.with_suffix(".pyc")
    import py_compile

    py_compile.compile(str(definition_file), str(compiled_definition_file))
    assert compiled_definition_file.is_file()
    definition_file.unlink()
    assert not find_solution_display_name(main_file)


def test_find_solution_display_name(tmp_path: Path):
    main_file = tmp_path / "main.py"
    definition_file = tmp_path / "solution" / "definition.py"
    definition_file.parent.mkdir()
    definition_file.write_text(
        """
from ansys.saf.glow.solution import Solution

class MySolution(Solution):
    display_name: str = "My Test Name"
    """,
    )
    solution_display_name = find_solution_display_name(main_file)
    assert solution_display_name == "My Test Name"


def test_find_solution_display_name_wrong_assignment(tmp_path: Path):
    main_file = tmp_path / "main.py"
    definition_file = tmp_path / "solution" / "definition.py"
    definition_file.parent.mkdir()
    definition_file.write_text(
        """
from ansys.saf.glow.solution import Solution

class MySolution(Solution):
    display_name = "My Test Name"
    """,
    )
    assert not find_solution_display_name(main_file)


def test_find_solution_display_name_no_assignment(tmp_path: Path):
    main_file = tmp_path / "main.py"
    definition_file = tmp_path / "solution" / "definition.py"
    definition_file.parent.mkdir()
    definition_file.write_text(
        """
from ansys.saf.glow.solution import Solution

class MySolution(Solution):
    my_other_field: str = "My Test Name"
    """,
    )
    assert not find_solution_display_name(main_file)
