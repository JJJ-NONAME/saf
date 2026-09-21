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

import asyncio
from collections.abc import AsyncGenerator
import json
from pathlib import Path
import uuid
import zipfile

from fastapi import UploadFile
import pytest
from stream_zip import AsyncMemberFile, async_stream_zip

from ansys.saf.glow._server.project_files_manager import ProjectFilesManager
from ansys.saf.glow._server.schemas import ProjectInfo


@pytest.fixture
def tmp_project_files_dir(tmp_path: Path) -> Path:
    return tmp_path / "project_files"


@pytest.fixture
def project_files_manager(tmp_project_files_dir: Path) -> ProjectFilesManager:
    return ProjectFilesManager(tmp_project_files_dir)


@pytest.fixture
def random_project_id() -> str:
    return str(uuid.uuid4())


def test_init(tmp_project_files_dir: Path, project_files_manager: ProjectFilesManager):
    assert (
        project_files_manager._project_files_directory == tmp_project_files_dir  # pyright: ignore[reportPrivateUsage]
    )


def test_create_project_files_dir(
    tmp_project_files_dir: Path,
    project_files_manager: ProjectFilesManager,
    random_project_id: str,
):
    assert not (tmp_project_files_dir / random_project_id).exists()
    result = project_files_manager.create_project_files_dir(random_project_id)
    assert result == tmp_project_files_dir / random_project_id
    assert (tmp_project_files_dir / random_project_id).is_dir()


def test_create_project_files_dir_twice(
    tmp_project_files_dir: Path,
    project_files_manager: ProjectFilesManager,
    random_project_id: str,
):
    result = project_files_manager.create_project_files_dir(random_project_id)
    assert result == tmp_project_files_dir / random_project_id
    assert (tmp_project_files_dir / random_project_id).is_dir()
    result = project_files_manager.create_project_files_dir(random_project_id)
    assert result == tmp_project_files_dir / random_project_id
    assert (tmp_project_files_dir / random_project_id).is_dir()


def test_import_project_files_dir(
    tmp_path: Path,
    tmp_project_files_dir: Path,
    project_files_manager: ProjectFilesManager,
    random_project_id: str,
):
    dir_to_import = tmp_path / f"dir_to_import_{str(uuid.uuid4())}"
    dir_to_import.mkdir()
    (dir_to_import / "my_file.txt").touch()
    # creates project_dir if necessary
    assert not (tmp_project_files_dir / random_project_id).exists()
    result = project_files_manager.import_project_files_dir(random_project_id, dir_to_import)
    assert result == tmp_project_files_dir / random_project_id
    assert (tmp_project_files_dir / random_project_id / "my_file.txt").is_file()
    assert not dir_to_import.exists()


def test_import_project_files_dir_inexistent_dir(project_files_manager: ProjectFilesManager, random_project_id: str):
    # it create project_files dir so that it can be used during migrations
    result = project_files_manager.import_project_files_dir(random_project_id, Path("fake_dir"))
    assert result.exists()


def test_import_project_files_dir_twice(
    tmp_path: Path,
    tmp_project_files_dir: Path,
    project_files_manager: ProjectFilesManager,
    random_project_id: str,
):
    dir_to_import = tmp_path / f"dir_to_import_{str(uuid.uuid4())}"
    dir_to_import.mkdir()
    (dir_to_import / "my_file.txt").touch()
    result = project_files_manager.import_project_files_dir(random_project_id, dir_to_import)
    assert result == tmp_project_files_dir / random_project_id
    assert (tmp_project_files_dir / random_project_id / "my_file.txt").is_file()

    second_dir_to_import = tmp_path / f"dir_to_import_{str(uuid.uuid4())}"
    second_dir_to_import.mkdir()
    (second_dir_to_import / "my_second_file.txt").touch()
    result = project_files_manager.import_project_files_dir(random_project_id, second_dir_to_import)
    assert result == tmp_project_files_dir / random_project_id
    assert (tmp_project_files_dir / random_project_id / "my_file.txt").is_file()
    # WHY????
    assert (tmp_project_files_dir / random_project_id / second_dir_to_import.name / "my_second_file.txt").is_file()


def test_export_project_files_dir(
    tmp_path: Path,
    project_files_manager: ProjectFilesManager,
    random_project_id: str,
):
    async def get_safx_stream_bytes(project_file_members: AsyncGenerator[AsyncMemberFile, None]) -> bytes:
        return b"".join([chunk async for chunk in async_stream_zip(project_file_members)])

    result = project_files_manager.create_project_files_dir(random_project_id)
    (result / "my_file.txt").write_text("hello")

    dir_to_export = tmp_path / f"dir_to_export_{str(uuid.uuid4())}"
    dir_to_export.mkdir()
    exported_project_safx_path = dir_to_export / "test.safx"
    assert not exported_project_safx_path.is_file()
    project_info = ProjectInfo(display_name="test", name=f"projects/{random_project_id}")
    async_project_files_generator = project_files_manager.create_async_project_files_generator(
        project_info,
        {"display_name": "test"},
    )
    assert async_project_files_generator is not None
    # stream the exported data and save it as a .safx file
    safx_stream_bytes = asyncio.run(get_safx_stream_bytes(async_project_files_generator()))
    exported_project_safx_path.write_bytes(safx_stream_bytes)
    # check that the .safx file is created after the streaming and contains the right data
    with zipfile.ZipFile(exported_project_safx_path, mode="r", compression=zipfile.ZIP_DEFLATED) as archive:
        assert archive.namelist() == ["test/my_file.txt", "test.sap"]
        archive.extractall(dir_to_export)
    assert (dir_to_export / "test" / "my_file.txt").read_text() == "hello"
    assert json.loads((dir_to_export / "test.sap").read_text()) == {
        "display_name": "test",
    }


def test_remove_project_files_dir(
    tmp_project_files_dir: Path,
    project_files_manager: ProjectFilesManager,
    random_project_id: str,
):
    project_files_manager.create_project_files_dir(random_project_id)
    project_files_manager.remove_project_files_dir(random_project_id)
    assert not (tmp_project_files_dir / random_project_id).is_dir()


def test_remove_project_files_dir_inexistent_project(
    tmp_project_files_dir: Path,
    project_files_manager: ProjectFilesManager,
    random_project_id: str,
):
    assert not (tmp_project_files_dir / random_project_id).is_dir()
    project_files_manager.remove_project_files_dir(random_project_id)
    assert not (tmp_project_files_dir / random_project_id).is_dir()


async def test_write_file_from_compressed_file(
    tmp_path: Path,
    tmp_project_files_dir: Path,
    project_files_manager: ProjectFilesManager,
    random_project_id: str,
):
    dir_to_zip = tmp_path / f"dir_with_compressed_file_{str(uuid.uuid4())}"
    dir_to_zip.mkdir()
    compressed_file = dir_to_zip / "my_file.glwzp"
    with zipfile.ZipFile(compressed_file, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("my_file.txt", "hello")

    upload_file = UploadFile(file=compressed_file.open("rb"))
    try:
        # it creates the directory even if the project doesn't exist!
        # it uses the parent of the destination
        assert not (tmp_project_files_dir / random_project_id).exists()
        await project_files_manager.write_file_to(
            upload_file,
            str(tmp_project_files_dir / random_project_id / "my_fake_dest_file"),
        )
        assert list((tmp_project_files_dir / random_project_id).iterdir()) == [
            (tmp_project_files_dir / random_project_id / "my_file.txt"),
        ]
    finally:
        await upload_file.close()


def test_get_project_files_dir(
    tmp_project_files_dir: Path,
    project_files_manager: ProjectFilesManager,
    random_project_id: str,
):
    assert project_files_manager.get_project_files_dir(random_project_id) == tmp_project_files_dir / random_project_id
    assert not (tmp_project_files_dir / random_project_id).exists()


def get_project_files_root(tmp_project_files_dir: Path, project_files_manager: ProjectFilesManager):
    assert project_files_manager.get_project_files_root() == tmp_project_files_dir
