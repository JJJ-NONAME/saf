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
import zipfile

SOLUTION_EXT = ".saf"
DEFAULT_EXCLUDED_DIRS = [".venv", ".poetry", ".git", "glow", "portal", ".github"]


def archive_solution(
    solution_root_dir: Path,
    archive_name: str,
    archive_path: Path | None = None,
    archive_extension: str | None = None,
) -> None:
    """Archive a solution directory into a zip file.

    This function takes a solution directory, compresses its contents into a zip file, and saves
    it to the specified archive path or the current working directory if no path is provided.

    Parameters
    ----------
    solution_root_dir : Path
        The path to the solution's root directory (which contains src/) to be archived.
    archive_name : str
        The name of the archive file (without extension).
    archive_path : Path, optional
        The path where the archive file will be saved. Default path: current working directory.
    archive_extension : str, optional
        The extension for the archive file, including the initial dot. Default extension: ".saf".
    """
    if archive_path and not archive_path.is_dir():
        raise NotADirectoryError(f"{archive_path} is not a valid directory.")

    extension = f"{archive_extension}" if archive_extension is not None else SOLUTION_EXT

    archive_path = (archive_path if archive_path else Path.cwd()) / f"{archive_name}{extension}"

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        stack = [solution_root_dir]
        while stack:
            current_path = stack.pop()
            with os.scandir(current_path) as entries:
                for entry in entries:
                    entry_path = current_path / entry.name
                    # Makes sure that the created .saf file is not part of the archive itself!
                    # (This typically happens when running "saf archive .").
                    if entry.is_file() and str(entry_path.resolve()) != zip_file.filename:
                        parent_path = os.path.relpath(entry_path, solution_root_dir)
                        zip_file.write(entry_path, parent_path)
                    elif entry.is_dir() and entry.name not in DEFAULT_EXCLUDED_DIRS:
                        stack.append(entry_path)
