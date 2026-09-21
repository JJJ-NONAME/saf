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

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
import tempfile
from typing import cast

from ansys.hps.client.jms import (  # pyright: ignore[reportMissingTypeStubs]
    File,
    JmsApi,
    ProjectApi,
)

from ansys.saf.glow._hps_auth.ihps_authenticator import IHpsAuthenticator
from ansys.saf.glow._hps_parametric_studies.base import HpsProject
from ansys.saf.glow._hps_parametric_studies.system import HpsParametricStudySystem


class ProjectNotFoundError(RuntimeError):
    """Raised when an HPS project is not found."""


class HpsProjectWrapper:
    def __init__(self, persisted_project: HpsProject, hps_authenticator: IHpsAuthenticator) -> None:
        self._pickled_parameters = persisted_project.pickled_parameters
        self._hps_project_identifier = persisted_project.hps_project_identifier
        self._hps_server_url = persisted_project.hps_server_url
        self._client_id = persisted_project.client_id
        self._hps_authenticator = hps_authenticator

    @contextmanager
    def _get_project_api(self) -> Generator[ProjectApi]:
        with HpsParametricStudySystem.get_hps_client(
            hps_authenticator=self._hps_authenticator,
            hps_server_url=self._hps_server_url,
            client_id=self._client_id,
        ) as hps_client:
            projects = JmsApi(hps_client).get_projects(  # pyright: ignore[reportUnknownMemberType]
                id=self._hps_project_identifier,
            )
            if not projects:
                raise ProjectNotFoundError(f"Project not found for ID: {self._hps_project_identifier}")
            yield ProjectApi(hps_client, self._hps_project_identifier)

    @property
    def exists(self) -> bool:
        if self._hps_project_identifier == "":
            return False
        try:
            with self._get_project_api():
                ...
        except ProjectNotFoundError:
            return False
        return True

    def get_project_file(self, file_id: str) -> File:
        with self._get_project_api() as project_api:
            files = project_api.get_files(content=False, id=[file_id])  # pyright: ignore[reportUnknownMemberType]
        if not files:
            raise RuntimeError(f"Unable to find file with id {file_id} in HPS")
        file = files[0]
        size = cast("None | int", file.size)
        if size is None:
            raise RuntimeError(f"File '{file.name}' ({file_id}) does not exist in HPS.")
        return file

    def _download_project_file(self, file: File, directory: Path) -> Path:
        with self._get_project_api() as project_api:
            file_path_str = project_api.download_file(  # pyright: ignore[reportUnknownMemberType]
                file,
                directory.absolute().as_posix(),
            )
        file_path = Path(file_path_str)
        if not file_path.is_file():
            raise RuntimeError(
                f"HPS download claims to have created {file_path_str} but it doesn't appear to exist",
            )
        return file_path

    @contextmanager
    def _get_temp_file(self, file_id: str):
        file = self.get_project_file(file_id)
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            file_path = self._download_project_file(file, directory)
            yield file_path

    def copy_file(self, file_id: str, destination_dir: Path) -> Path:
        file = self.get_project_file(file_id)
        return self._download_project_file(file, destination_dir)
