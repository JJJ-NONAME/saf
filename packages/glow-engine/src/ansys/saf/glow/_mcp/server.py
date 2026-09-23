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
from types import ModuleType
from typing import Any

from fastmcp import FastMCP

from ansys.saf.glow._mcp._data_tools import register_data_tools
from ansys.saf.glow._mcp._guidance_tools import register_guidance_tools
from ansys.saf.glow._mcp._project_tools import register_project_tools
from ansys.saf.glow._mcp._resolution import (
    SOLUTION_API_URL_ATTR,
    SOLUTION_CLASS_ATTR,
    SOLUTION_WORKFLOW_ATTR,
)
from ansys.saf.glow._mcp._transaction_tools import register_transaction_tools
from ansys.saf.glow._mcp.solution_doc import SolutionDoc
from ansys.saf.glow.client import Client
from ansys.saf.glow.solution import Solution


def build_app(definition_module: ModuleType, solution_class: type[Solution], solution_api_url: str) -> FastMCP:
    doc = SolutionDoc.from_solution_md(definition_module, solution_class)
    app = FastMCP(name=solution_class.model_construct().display_name, instructions=doc.instructions)
    setattr(app, SOLUTION_CLASS_ATTR, solution_class)
    setattr(app, SOLUTION_API_URL_ATTR, solution_api_url)
    setattr(app, SOLUTION_WORKFLOW_ATTR, doc.workflow)

    register_guidance_tools(app, doc.workflow)

    def client_factory(solution_class: type[Solution], solution_api_url: str) -> Client[Any]:
        return Client(solution_class, solution_api_url)

    register_project_tools(app, client_factory)
    register_data_tools(app, client_factory)
    register_transaction_tools(app, solution_class, client_factory)

    return app
