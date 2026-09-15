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

import traceback
from types import ModuleType

from pydantic import BaseModel

from ansys.saf.glow._server.solution import SolutionService


class AnalysisResultModel(BaseModel):
    """Represents the result of a solution analysis."""

    valid: bool
    error: str = ""
    stack_trace: str = ""
    uses_shared_product_instances: bool = False
    solution_name: str = ""
    ui_module: str = ""
    solution_module: str = ""


def perform_analysis(definition_module: ModuleType, ui_app_module: ModuleType | None = None) -> AnalysisResultModel:
    try:
        solution_service = SolutionService(definition_module)
        solution_service.build_and_validate()
        return AnalysisResultModel(
            valid=True,
            uses_shared_product_instances=solution_service.has_shared_product_instances,
            solution_name=solution_service.name,
            ui_module="" if not ui_app_module else ui_app_module.__name__,
            solution_module=solution_service.solution_module.__name__,
        )
    except Exception as e:
        return AnalysisResultModel(
            valid=False,
            error=str(e),
            stack_trace=traceback.format_exc(),
        )
