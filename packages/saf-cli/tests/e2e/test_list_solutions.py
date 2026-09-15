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
import shutil

from ansys.saf.cli._config.const import DEFAULT_SOLUTION_DISPLAY_NAME, DEFAULT_SOLUTION_NAME
from tests.e2e.conftest import ListSolutions, NewSolution


def test_saf_solutions_not_existing_database(database_path: Path, list_solutions: ListSolutions):
    """
    Test ``saf solutions`` does not list any solution nor creates the database if the database does not exist.
    """
    database_path.unlink(missing_ok=True)
    assert "\n".join(list_solutions()) == "No solutions found."
    assert not database_path.is_file()


def test_saf_solutions_empty_database(database_path: Path, list_solutions: ListSolutions):
    """
    Test ``saf solutions`` does not list any solution if the database is empty.
    """
    database_path.touch()
    assert "\n".join(list_solutions()) == "No solutions found."


def test_saf_solutions_wrong_content_database(database_path: Path, list_solutions: ListSolutions):
    """
    Test ``saf solutions`` raises an exception if the database file contains invalid data.
    """
    database_path.write_text("hello")
    assert "Invalid JSON: expected value at line 1 column 1" in "\n".join(list_solutions(expected_return_code=1))


def test_saf_solutions_multiple_solutions(tmp_path: Path, list_solutions: ListSolutions, new_solution: NewSolution):
    """
    Test ``saf solutions`` shows multiple solutions, grouped by solution name.
    """
    first_subdir = tmp_path / "subdir_a"
    first_subdir.mkdir()
    second_subdir = tmp_path / "subdir_b"
    second_subdir.mkdir()
    # two solutions with the same name but different path
    new_solution(cwd=first_subdir, input_str="\nMy First Solution\n\n\n")
    new_solution(cwd=second_subdir, input_str="\nMy Second Solution\n\n\n")
    # another solution alongside the first one with a different name
    new_solution(cwd=second_subdir, input_str="my_third_solution\nMy Third Solution\n\n\n")
    expected_output = f"""{DEFAULT_SOLUTION_NAME}
    Root directory: {str(first_subdir / DEFAULT_SOLUTION_NAME)}
    Display Name: My First Solution

    Root directory: {str(second_subdir / DEFAULT_SOLUTION_NAME)}
    Display Name: My Second Solution

my_third_solution
    Root directory: {str(second_subdir / "my_third_solution")}
    Display Name: My Third Solution
"""
    assert "\n".join(list_solutions()) == expected_output


def test_saf_solutions_deleted_solution(
    tmp_path: Path,
    database_path: Path,
    list_solutions: ListSolutions,
    new_solution: NewSolution,
):
    """
    Test ``saf solutions`` does not show solutions that do not exist in directory even if they are listed in the
    database.
    """
    # Create a solution and show that its information is in the database file and listed by solutions cmd
    assert not database_path.is_file()
    new_solution(input_str="\n\n\n\n", cwd=tmp_path)
    database_content = database_path.read_text()
    assert DEFAULT_SOLUTION_NAME in database_content
    expected_output = f"""{DEFAULT_SOLUTION_NAME}
    Root directory: {str(tmp_path / DEFAULT_SOLUTION_NAME)}
    Display Name: {DEFAULT_SOLUTION_DISPLAY_NAME}
"""
    assert "\n".join(list_solutions()) == expected_output

    # If the solution does not exist in disk, it's not listed by the cmd but not removed from the database
    shutil.rmtree(tmp_path / DEFAULT_SOLUTION_NAME)
    assert "\n".join(list_solutions()) == "No solutions found."
    assert database_content == database_path.read_text()

    # If the solution again exists (e.g., was moved back by the user), it's again listed
    (tmp_path / DEFAULT_SOLUTION_NAME).mkdir()
    assert "\n".join(list_solutions()) == expected_output
    assert database_content == database_path.read_text()
