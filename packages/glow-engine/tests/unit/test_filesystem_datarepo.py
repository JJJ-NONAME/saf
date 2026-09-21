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

import pytest

from ansys.saf.glow._bdm.filesystem import FileSystemMinervaMockClient


@pytest.fixture
def project_files(tmp_path: Path) -> Path:
    project_files = tmp_path / "appdata" / "ansys" / "glow" / "DataRepositorySolution" / "project_files"
    project_files.mkdir(exist_ok=True, parents=True)
    return project_files


@pytest.fixture
def data_repository_path(project_files: Path) -> Path:
    filesystemdir = project_files / "filesystem"
    filesystemdir.mkdir(exist_ok=True)
    return filesystemdir


@pytest.fixture
def minerva_local_repository_path(project_files: Path) -> Path:
    minervadir = project_files / "123456789" / "minerva"
    minervadir.mkdir(exist_ok=True, parents=True)
    return minervadir


@pytest.fixture
def fs_client(data_repository_path: Path, minerva_local_repository_path: Path) -> FileSystemMinervaMockClient:
    return FileSystemMinervaMockClient(data_repo_path=data_repository_path, working_dir=minerva_local_repository_path)


def test_client_upload_remote_file_move_file_from_local_minerva_to_filesystem_dir(
    fs_client: FileSystemMinervaMockClient,
    minerva_local_repository_path: Path,
    data_repository_path: Path,
):
    # GIVEN: a file within the local minerva dir
    my_file = minerva_local_repository_path / "Data" / "123456789" / "dir" / "my_file.txt"
    target_path = data_repository_path / "Data" / "123456789" / "dir" / "my_file.txt" / "001_default"
    my_file.parent.mkdir(exist_ok=True, parents=True)
    my_file.write_text("hello world!")
    assert not target_path.exists()
    # WHEN: upload is called
    fs_client.upload(remote_root="/Data")
    # THEN: the file is moved from local minerva dir to the filesystem dir
    assert target_path.read_text() == "hello world!"
    assert not my_file.exists()


def test_client_download_file_copy_file_from_filesystem_to_local_minerva_dir(
    fs_client: FileSystemMinervaMockClient,
    minerva_local_repository_path: Path,
    data_repository_path: Path,
):
    data_repo_file = data_repository_path / "Data" / "my_file.txt" / "001_default"
    data_repo_file.parent.mkdir(exist_ok=True, parents=True)
    data_repo_file.write_text("hello world!")
    data_repo_file.with_name(".metadata").touch()
    assert not (minerva_local_repository_path / "Data" / "my_file.txt").exists()
    fs_client.download(remote_path="/Data/my_file.txt")
    assert (minerva_local_repository_path / "Data" / "my_file.txt").read_text() == "hello world!"
    assert data_repo_file.exists()


def test_client_download_directory_copy_directory_from_filesystem_to_local_minerva_dir(
    fs_client: FileSystemMinervaMockClient,
    minerva_local_repository_path: Path,
    data_repository_path: Path,
):
    data_repo_folder = data_repository_path / "Data" / "folder"
    my_file = data_repo_folder / "my_file.txt" / "001_default"
    my_file.parent.mkdir(exist_ok=True, parents=True)
    my_file.write_text("hello world!")
    my_file.with_name(".metadata").touch()
    assert not (minerva_local_repository_path / "Data" / "folder").exists()
    fs_client.download(remote_path="/Data/folder")
    assert (minerva_local_repository_path / "Data" / "folder").exists()
    assert (minerva_local_repository_path / "Data" / "folder" / "my_file.txt").read_text() == "hello world!"
    assert my_file.exists()


def test_client_upload_multiple_versions(
    fs_client: FileSystemMinervaMockClient,
    minerva_local_repository_path: Path,
    data_repository_path: Path,
):
    # GIVEN: a file within the local minerva dir
    my_file = minerva_local_repository_path / "Data" / "123456789" / "dir" / "my_file.txt"
    target_path = data_repository_path / "Data" / "123456789" / "dir" / "my_file.txt" / "001_default"
    my_file.parent.mkdir(exist_ok=True, parents=True)
    assert not target_path.exists()
    # WHEN: upload is called
    my_file.write_text("v1")
    fs_client.upload(remote_root="/Data")
    # THEN: the file is moved from local minerva dir to the filesystem dir
    expected_filenames = {"001.001", "001_default"}
    assert target_path.read_text() == "v1"
    filenames = set({p.name for p in target_path.parent.rglob("001*")})
    assert filenames == expected_filenames
    assert (target_path.parent / "001.001").read_text() == "v1"

    my_file.write_text("v2")
    fs_client.upload(remote_root="/Data")
    expected_filenames.add("001.002")
    assert target_path.read_text() == "v2"
    filenames = set({p.name for p in target_path.parent.rglob("001*")})
    assert filenames == expected_filenames
    assert (target_path.parent / "001.001").read_text() == "v1"
    assert (target_path.parent / "001.002").read_text() == "v2"

    my_file.write_text("v3")
    fs_client.upload(remote_root="/Data")
    expected_filenames.add("001.003")
    assert target_path.read_text() == "v3"
    filenames = set({p.name for p in target_path.parent.rglob("001*")})
    assert filenames == expected_filenames
    assert (target_path.parent / "001.001").read_text() == "v1"
    assert (target_path.parent / "001.002").read_text() == "v2"
    assert (target_path.parent / "001.003").read_text() == "v3"
