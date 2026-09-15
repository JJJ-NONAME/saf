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
from zipfile import ZipFile

import pytest

from ansys.saf.cli._utilities.archiver import DEFAULT_EXCLUDED_DIRS, SOLUTION_EXT, archive_solution


def _verify_archive_content(archive_path: Path, expected_files: list[str]):
    with ZipFile(archive_path, "r") as archive:
        assert sorted(expected_files) == sorted(archive.namelist())


@pytest.fixture
def expected_files_in_archive(root_solution_dir: Path) -> list[str]:
    return [p.relative_to(root_solution_dir).as_posix() for p in root_solution_dir.rglob("*") if p.is_file()]


@pytest.mark.usefixtures("tmp_path_as_working_dir")
@pytest.mark.parametrize("solution_name", ["solution_with_dash_ui"], indirect=True)
def test_archive_solution(root_solution_dir: Path, tmp_path: Path, expected_files_in_archive: list[str]):
    archive_name = "archived_solution"
    # Solution archive is created on current directory if --path is not specified
    expected_archive_path = tmp_path / f"{archive_name}{SOLUTION_EXT}"
    assert not expected_archive_path.is_file()
    archive_solution(root_solution_dir, archive_name)
    assert expected_archive_path.is_file()
    _verify_archive_content(expected_archive_path, expected_files_in_archive)


@pytest.mark.usefixtures("tmp_path_as_working_dir")
@pytest.mark.parametrize("solution_name", ["solution_with_dash_ui"], indirect=True)
def test_archive_solution_with_input_path(
    root_solution_dir: Path,
    tmp_path: Path,
    expected_files_in_archive: list[str],
):
    archive_name = "archived_solution"
    dest_path = tmp_path / "archived"
    dest_path.mkdir()
    expected_archive_path = dest_path / f"{archive_name}{SOLUTION_EXT}"
    assert not expected_archive_path.is_file()
    archive_solution(root_solution_dir, archive_name, archive_path=dest_path)
    assert expected_archive_path.is_file()
    _verify_archive_content(expected_archive_path, expected_files_in_archive)


@pytest.mark.usefixtures("tmp_path_as_working_dir")
@pytest.mark.parametrize("solution_name", ["solution_with_dash_ui"], indirect=True)
def test_archive_solution_with_input_extension(
    root_solution_dir: Path,
    tmp_path: Path,
    expected_files_in_archive: list[str],
):
    archive_name = "archived_solution"
    custom_extension = ".extension"
    expected_archive_path = tmp_path / f"{archive_name}{custom_extension}"
    assert not expected_archive_path.is_file()
    archive_solution(root_solution_dir, archive_name, archive_extension=custom_extension)
    assert expected_archive_path.is_file()
    _verify_archive_content(expected_archive_path, expected_files_in_archive)


@pytest.mark.usefixtures("tmp_path_as_working_dir")
@pytest.mark.parametrize("solution_name", ["solution_with_dash_ui"], indirect=True)
def test_archive_solution_wrong_path_raises_invalid_dir(root_solution_dir: Path, tmp_path: Path):
    archive_name = "archived_solution"
    dest_path = tmp_path / "archived"
    expected_archive_path = dest_path / f"{archive_name}{SOLUTION_EXT}"
    assert not expected_archive_path.is_file()
    with pytest.raises(NotADirectoryError, match=re.escape(f"{dest_path} is not a valid directory.")):
        archive_solution(root_solution_dir, archive_name, archive_path=dest_path)
    assert not expected_archive_path.is_file()


@pytest.mark.usefixtures("tmp_path_as_working_dir")
@pytest.mark.parametrize("solution_name", ["solution_with_dash_ui"], indirect=True)
def test_archive_solution_excludes_invalid_directories(
    root_solution_dir: Path,
    tmp_path: Path,
    expected_files_in_archive: list[str],
):
    for dir_name in DEFAULT_EXCLUDED_DIRS:
        (root_solution_dir / dir_name).mkdir()
        (root_solution_dir / dir_name / "file.txt").touch()
        # also works if invalid directory is nested
        (root_solution_dir / "subdir" / dir_name).mkdir(parents=True, exist_ok=True)
        (root_solution_dir / "subdir" / dir_name / "file.txt").touch()

    archive_name = "archived_solution"
    expected_archive_path = tmp_path / f"{archive_name}{SOLUTION_EXT}"
    assert not expected_archive_path.is_file()
    archive_solution(root_solution_dir, archive_name)
    assert expected_archive_path.is_file()
    _verify_archive_content(expected_archive_path, expected_files_in_archive)
