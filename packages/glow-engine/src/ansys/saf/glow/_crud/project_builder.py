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

from datetime import datetime
import logging
from typing import TypeVar

from ansys.saf.glow._core.solution import Solution
from ansys.saf.glow._server.models import ProjectModel, ProjectSchema
from ansys.saf.glow._server.schemas import ProjectInfo
from ansys.saf.glow._server.solution import SolutionService

T = TypeVar("T", bound=Solution)
logger = logging.getLogger(__name__)


class ProjectBuilder:
    @classmethod
    def _create_project_from_info_and_solution_data(
        cls,
        project_info: ProjectInfo,
        project_solution_data: ProjectSchema[T],
        solution_service: SolutionService,
    ) -> ProjectModel[T]:
        project_dict = project_info.model_dump()
        project_dict.update(project_solution_data.model_dump())
        project = ProjectModel[solution_service.solution_type].model_validate(project_dict)
        return project

    @classmethod
    def build_project_model(
        cls,
        display_name: str,
        solution_service: SolutionService,
        description: str = "",
    ) -> ProjectModel[Solution]:
        now = datetime.now()
        project_info = ProjectInfo(
            name="projects/__to_be_created__",
            display_name=display_name,
            description=description,
            date_created=now,
            date_modified=now,
        )
        project_solution_data = ProjectSchema[solution_service.solution_type](
            solution=solution_service.default_instance,
            solution_name=solution_service.solution_type.__name__,
            method_states={},
            instances={},
        )
        logger.debug(f"Solution data to be saved: {project_solution_data}")
        project = cls._create_project_from_info_and_solution_data(project_info, project_solution_data, solution_service)
        return project
