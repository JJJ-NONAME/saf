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

import json
import logging
from pathlib import Path
import shutil
from typing import Any, TypeVar
import zipfile

from fastapi import UploadFile
from pydantic import ValidationError

from ansys.saf.glow._bdm.multiplexor import SafMultiplexorStorageScopeFactory
from ansys.saf.glow._bdm.storage_contexts import RESTAPI_CONTEXT
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._core.migrations import MigrationContext
from ansys.saf.glow._core.solution import Solution
from ansys.saf.glow._crud.bdm_helper import update_opaque_identifier_in_project_text
from ansys.saf.glow._server.exceptions import BadRequestError, UnprocessableEntityError
from ansys.saf.glow._server.models import ProjectModel
from ansys.saf.glow._server.project_files_manager import ProjectFilesManager
from ansys.saf.glow._server.schemas import ProjectInfo

T = TypeVar("T", bound=Solution)
logger = logging.getLogger(__name__)


def create_project_info(display_name: str, project_id: str | None = None) -> ProjectInfo:
    # use __to_be_created__ as a placeholder only (it no longer triggers id generation anywhere)
    return ProjectInfo(name=f"projects/{project_id or '__to_be_created__'}", display_name=display_name)


async def unzip_archive(
    file_manager: ProjectFilesManager,
    upload_file: UploadFile,
    tmp_path: Path,
    project_directory: Path,
    new_display_name: str,
) -> Path:
    if upload_file.filename is None or not upload_file.filename.endswith(".safx"):
        raise BadRequestError(f"Expected a .safx file, but received: '{upload_file.filename}'.")

    logger.info(f"Unzipping {upload_file.filename}...")

    # Saving uploaded file into a tmp directory so that we can use ZipFile.
    # (UploadFile.file cannot be used directly in ZipFile...)
    safx_tmp_path = tmp_path / upload_file.filename
    target_project_file = tmp_path / f"{new_display_name}.sap"
    # the staging directory is a place where the archive extracted to that can be moved into a project directory
    staging_project_directory = project_directory.parent / f"STAGING_{project_directory.name}"
    logger.debug(f"Copying: {upload_file.filename} to {safx_tmp_path}...")
    await file_manager.write_file_to(upload_file, str(safx_tmp_path))
    with zipfile.ZipFile(safx_tmp_path, mode="r") as archive:
        archive.extractall(staging_project_directory)

    try:
        # expecting one sap file and an optional directory
        archive_project_file: Path | None = None
        archive_project_directory: Path | None = None
        number_of_items = 0

        for item in staging_project_directory.iterdir():
            if item.is_file():
                archive_project_file = item
            else:
                archive_project_directory = item
            number_of_items += 1

        if number_of_items == 0:
            raise BadRequestError(
                f"'{upload_file.filename}' is not a valid project archive. It does not contain anything.",
            )
        if number_of_items > 2:
            raise BadRequestError(
                f"'{upload_file.filename}' is not a valid project archive. "
                f"It contains more than two top level items: {number_of_items} items found.",
            )
        if archive_project_file is None:
            raise BadRequestError(
                f"'{upload_file.filename}' is not a valid project archive. It does not contain a top level file.",
            )
        if not archive_project_file.name.endswith(".sap"):
            raise BadRequestError(
                f"'{upload_file.filename}' is not a valid project archive. "
                f"The top level sap file is missing or has an invalid name: {archive_project_file.name}.",
            )

        shutil.move(archive_project_file, target_project_file)

        if archive_project_directory is None:
            project_directory.mkdir()  # noqa: ASYNC240
        else:
            shutil.move(archive_project_directory, project_directory)
    finally:
        shutil.rmtree(staging_project_directory, ignore_errors=True)

    return target_project_file


async def parse_and_migrate_imported_project(
    project_file: Path,
    solution_type: type[T],
    default_instance: T,
    display_name: str,
    project_file_manager: ProjectFilesManager,
    project_id: str,
    storage_scope_factory: SafMultiplexorStorageScopeFactory,
    settings: Settings,
) -> ProjectModel[T]:
    # Create new project with imported data from project_file.
    new_project_info = create_project_info(display_name, project_id)
    project_storage_scope = storage_scope_factory.create_storage_scope(RESTAPI_CONTEXT)
    try:
        project_text = update_opaque_identifier_in_project_text(project_file.read_text(), project_id)  # noqa: ASYNC240
        project_model_dict = json.loads(project_text)
        # this is complete hack but I don't understand how the old ever worked sorry
        project_model_dict["display_name"] = display_name
        project_model_dict["name"] = new_project_info.name

        def construct_migration_context(values: dict[str, Any]) -> MigrationContext:
            return MigrationContext(
                values,
                project_storage_scope,
                project_file_manager,
                project_id,
                settings,
            )

        context = {
            "mode": "import",
            "default_solution": default_instance,
            "migration_context_constructor": construct_migration_context,
            "automatic_project_migration": settings.glow_enable_automatic_project_migration,
        }
        project = ProjectModel[solution_type].model_validate(project_model_dict, context=context)
    except ValidationError as ex:
        raise UnprocessableEntityError(str(ex)) from None

    return project
