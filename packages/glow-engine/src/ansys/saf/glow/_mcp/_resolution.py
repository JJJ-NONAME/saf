# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Any

from fastmcp.server import Context

from ansys.saf.glow.solution import Solution

SOLUTION_CLASS_ATTR = "_solution_class"
SOLUTION_API_URL_ATTR = "_solution_api_url"
SOLUTION_WORKFLOW_ATTR = "_solution_workflow"


def get_solution_config(ctx: Context) -> tuple[type[Solution], str]:
    app = ctx.fastmcp
    solution_class = getattr(app, SOLUTION_CLASS_ATTR, None)
    solution_api_url = getattr(app, SOLUTION_API_URL_ATTR, None)
    if solution_class is None or solution_api_url is None:
        raise RuntimeError("Solution class or API URL not configured.")
    return solution_class, solution_api_url


def get_step(project: Any, step_name: str) -> Any:
    step = getattr(project.steps, step_name, None)
    if not step:
        raise ValueError(f"Step '{step_name}' not found.")
    return step
