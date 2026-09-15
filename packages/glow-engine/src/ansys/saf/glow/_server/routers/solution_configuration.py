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

# pyright complains about some of the functions associated with routes because nothing calls them
# so switch that error off
# pyright: reportUnusedFunction=false, reportUnknownMemberType=false, reportUnknownParameterType=false

import logging
from typing import Any

from fastapi import APIRouter

from ansys.saf.glow._server.dependencies import SolutionConfigurationCrudDep
from ansys.saf.glow._server.solution import SolutionService

logger = logging.getLogger(__name__)


def make_routes(solution_service: SolutionService) -> APIRouter:
    if not solution_service.solution_configuration_type:
        raise RuntimeError("The solution does not have solution_configuration field defined.")

    router = APIRouter(
        prefix="/solution-configuration",
        tags=["solution-configuration"],
    )

    @router.get(
        "",
        responses={
            404: {"description": "Unable to find Solution configuration."},
            422: {"description": "Invalid Solution configuration."},
        },
        response_model=solution_service.solution_configuration_type,
    )
    async def get_solution_configuration(
        solution_configuration_crud: SolutionConfigurationCrudDep[
            solution_service.solution_configuration_type  # pyright: ignore[reportInvalidTypeForm]
        ],
    ) -> solution_service.solution_configuration_type:  # pyright: ignore[reportInvalidTypeForm]
        return await solution_configuration_crud.get_solution_configuration()  # pyright: ignore[reportUnknownVariableType]

    @router.get(
        "/schema",
        responses={
            404: {"description": "Unable to find a typed 'solution_configuration' field in the Solution definition."},
        },
    )
    async def get_solution_configuration_schema() -> dict[str, Any]:
        solution_configuration_type = solution_service.solution_configuration_type
        return solution_configuration_type.model_json_schema()  # pyright: ignore[reportOptionalMemberAccess]

    @router.put(
        "",
        responses={
            404: {"description": "Unable to find Solution configuration."},
            422: {"description": "Invalid Solution configuration."},
        },
    )
    async def modify_solution_configuration(
        request: dict[str, Any],
        solution_configuration_crud: SolutionConfigurationCrudDep[
            solution_service.solution_configuration_type  # pyright: ignore[reportInvalidTypeForm]
        ],
    ):
        # TODO: refactor so request is already typed as a class derived in somw way from solution_configuration_type,
        # so we get some validation and stuff without having to even connect to the DB or read what is stored there.
        # Note that we still want to support: (i) partial modifications, (ii) modifications to default values, (iii)
        # validators that operate over multiple fields, and (iv) all of this also for the extended classes defined by
        # the solution developer.
        await solution_configuration_crud.modify_solution_configuration(request)

    return router
