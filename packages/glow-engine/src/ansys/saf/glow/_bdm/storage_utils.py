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

from ansys.saf.glow._bdm.storage_factory import random_shortid
from ansys.saf.glow._bdm.storage_variable_names import ACCESS_TOKEN, PROJECT_ID, PROJECT_NAME, ROOT, SHORTID
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._core.project_files_locator import ProjectFilesLocator
from ansys.saf.glow._server.schemas import ProjectInfo


def get_template_vars_helper(
    project_info: ProjectInfo,
    settings: Settings,
    access_token: str | None,
) -> dict[str, str]:
    project_files_directory = ProjectFilesLocator.get_project_files_root(settings)
    return {
        ROOT: str(project_files_directory),
        PROJECT_ID: project_info.project_id,
        PROJECT_NAME: project_info.display_name,
        SHORTID: random_shortid(),
        ACCESS_TOKEN: access_token or "",
    }
