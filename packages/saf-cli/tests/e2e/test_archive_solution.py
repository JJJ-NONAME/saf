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
import shutil

import pytest

from ansys.saf.cli._config.const import DEFAULT_SOLUTION_NAME
from ansys.saf.cli._database.models import SolutionRegistry
from tests.e2e.conftest import (
    ArchiveSolution,
    ListSolutions,
    NewSolution,
    RunArchivedSolution,
    is_solution_registered,
)


@pytest.mark.use_session_solution
@pytest.mark.parametrize("session_solution_ui_framework", ["dash"], indirect=True)
def test_archiving_a_registered_solution(
    session_solution: SolutionRegistry,
    archive_solution: ArchiveSolution,
    tmp_path: Path,
    run_solution_app_starter: RunArchivedSolution,
):
    """Test that ``saf archive`` of a registered solution creates an archive file in the current directory.
    That file can then be used to launch the solution using the solution-app-starter.
    """
    expected_archive_path = tmp_path / f"{session_solution.name}.saf"

    assert not expected_archive_path.is_file()
    archive_solution([session_solution.name], cwd=tmp_path)
    assert expected_archive_path.is_file()

    p = run_solution_app_starter(session_solution.root_dir, expected_archive_path)
    # User gets expected messages
    assert p.find_msg_in_output(f"Solution: {session_solution.display_name}")
    assert p.find_msg_in_output(
        r"- display name: [0-9-a-f]+",
        regex=True,
    )  # display name is a UUID set by the solution-app-starter
    assert p.find_msg_in_output(r"- name: projects/[0-9a-f]+", regex=True)
    assert p.find_msg_in_output(r"Solution API: http://127\.0\.0\.1:\d+/docs", regex=True)
    assert p.find_msg_in_output(r"Solution UI: http://127\.0\.0\.1:\d+/projects/[0-9a-f]+", regex=True)
    assert p.find_msg_in_output("SAF Portal: not launched")
    assert p.find_msg_in_output("PIM Light Server: not launched")
    assert p.find_msg_in_output("Additional services: not launched")


def test_archiving_a_solution_with_custom_parameters(
    new_solution: NewSolution,
    archive_solution: ArchiveSolution,
    tmp_path: Path,
):
    """Test that parameters of ``saf archive`` can be used to specify file name, destination path and extension of the
    archive.
    """
    solution_name = f"my-solution-{random.randint(0, 1000)}"
    new_solution(["--solution-name", solution_name], input_str="\n\n\n", cwd=tmp_path)

    dest_dir = tmp_path / "new_subdir"
    dest_dir.mkdir()
    archive_name = f"my-archive-{random.randint(0, 1000)}.my_ext"
    expected_archive_path = dest_dir / archive_name

    assert not expected_archive_path.is_file()
    archive_solution(
        [
            solution_name,
            "--filename",
            expected_archive_path.stem,
            "--path",
            str(dest_dir),
            "--extension",
            expected_archive_path.suffix,
        ],
        cwd=tmp_path,
    )
    assert expected_archive_path.is_file()


@pytest.mark.parametrize("namespace", [None, "ansys.solutions", "myorg.apps"])
@pytest.mark.parametrize("solution_param_type", [None, "relative", "absolute"])
def test_archiving_non_registered_solutions(
    namespace: str | None,
    solution_param_type: str | None,
    database_path: Path,
    new_solution: NewSolution,
    list_solutions: ListSolutions,
    archive_solution: ArchiveSolution,
    tmp_path: Path,
):
    """
    Test that is possible to archive a solution that is not registered in the CLI's database. The solution should
    be added to DB and the process should work as expected.
    """
    solution_root_dir = tmp_path / DEFAULT_SOLUTION_NAME
    # Construct input string: name (empty) + display_name (empty) + framework (empty) + namespace
    namespace_input = f"{namespace}\n" if namespace is not None else "\n"
    new_solution(input_str=f"\n\n\n{namespace_input}", cwd=tmp_path)
    database_path.unlink()
    assert not is_solution_registered(list_solutions(), solution_root_dir)

    cwd_dir = (
        tmp_path
        if solution_param_type == "absolute"
        else solution_root_dir.parent
        if solution_param_type == "relative"
        else solution_root_dir
    )
    expected_archive_path = cwd_dir / f"{solution_root_dir.name}.saf"
    assert not expected_archive_path.is_file()

    if solution_param_type == "absolute":
        archive_solution([solution_root_dir.absolute().as_posix()], cwd=cwd_dir)
    elif solution_param_type == "relative":
        archive_solution([f"./{solution_root_dir.name}"], cwd=cwd_dir)
    elif not solution_param_type:
        archive_solution([], cwd=cwd_dir)
    assert expected_archive_path.is_file()
    assert is_solution_registered(list_solutions(), solution_root_dir)


def test_archiving_solution_with_invalid_destination_path(
    new_solution: NewSolution,
    archive_solution: ArchiveSolution,
    tmp_path: Path,
):
    """
    Test that, when archive a solution, the --path parameter must point to a valid directory,
    otherwise it raises an error and nothing is created.
    """
    solution_root_dir = tmp_path / DEFAULT_SOLUTION_NAME
    new_solution(input_str="\n\n\n\n", cwd=tmp_path)

    p = archive_solution(["--path", str(tmp_path / "my_new_subdir")], cwd=solution_root_dir, expected_return_code=1)
    assert f"NotADirectoryError: {str(tmp_path / 'my_new_subdir')} is not a valid directory." in p.output
    assert not (tmp_path / "my_new_subdir").exists()


def test_archive_invalid_solution(tmp_path: Path, new_solution: NewSolution, archive_solution: ArchiveSolution):
    """
    Test archiving an existing solution that is invalid raises an error.
    """
    new_solution(input_str="\n\n\n\n", cwd=tmp_path)
    shutil.rmtree(tmp_path / DEFAULT_SOLUTION_NAME)

    p = archive_solution([DEFAULT_SOLUTION_NAME], cwd=tmp_path, expected_return_code=1)
    assert p.find_msg_in_output(f"NotADirectoryError: Solution not found at {str(tmp_path / DEFAULT_SOLUTION_NAME)}")


def test_archive_multiple_solutions_same_name_invalid_solution(
    tmp_path: Path,
    new_solution: NewSolution,
    archive_solution: ArchiveSolution,
):
    """
    Test archiving an existing solution that has the same name as other that is invalid.
    """
    new_solution(input_str="\n\n\n\n", cwd=tmp_path)
    (tmp_path / "another_solution").mkdir()
    new_solution(input_str="\n\n\n\n", cwd=(tmp_path / "another_solution"))
    shutil.rmtree(tmp_path / "another_solution")

    expected_archive_path = tmp_path / f"{DEFAULT_SOLUTION_NAME}.saf"
    archive_solution([DEFAULT_SOLUTION_NAME], cwd=tmp_path)
    assert expected_archive_path.is_file()


def test_archive_multiple_solutions_same_name(
    tmp_path: Path,
    new_solution: NewSolution,
    archive_solution: ArchiveSolution,
):
    """
    Test archiving an existing solution that has the same name as other raises an error.
    """
    new_solution(input_str="\n\n\n\n", cwd=tmp_path)
    (tmp_path / "another_solution").mkdir()
    new_solution(input_str="\n\n\n\n", cwd=(tmp_path / "another_solution"))

    p = archive_solution([DEFAULT_SOLUTION_NAME], expected_return_code=1)

    assert p.find_msg_in_output(f"ValueError: Multiple solutions found with the name {DEFAULT_SOLUTION_NAME}.")
    assert p.find_msg_in_output(str(tmp_path / DEFAULT_SOLUTION_NAME))
    assert p.find_msg_in_output(str(tmp_path / "another_solution" / DEFAULT_SOLUTION_NAME))
    assert p.find_msg_in_output("Hint: You can specify the correct one by using the full path")
