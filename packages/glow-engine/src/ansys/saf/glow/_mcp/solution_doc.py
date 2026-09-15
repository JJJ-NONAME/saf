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
import re
from types import ModuleType
from typing import Self

from pydantic import BaseModel

from ansys.saf.glow._config.const import DEFAULT_SOLUTION_MD_FILENAME
from ansys.saf.glow._core.solution import Solution


class SolutionDoc(BaseModel):
    instructions: str = ""
    workflow: str = ""

    @staticmethod
    def _find_solution_md(definition_module: ModuleType) -> Path | None:
        if not definition_module.__file__:
            return None
        solution_md_file = Path(definition_module.__file__).parent / DEFAULT_SOLUTION_MD_FILENAME
        if solution_md_file.is_file():
            return solution_md_file
        return None

    @staticmethod
    def _parse_section(text: str, heading: str) -> str:
        # look for sections identified by heading level 2
        match = re.search(r"^## " + re.escape(heading) + r"\s*$", text, re.MULTILINE)
        if match is None:
            return ""
        start = match.end()
        next_heading = re.search(r"^## ", text[start:], re.MULTILINE)
        content = text[start : start + next_heading.start()] if next_heading else text[start:]
        return content.strip()

    @staticmethod
    def _default_instructions(solution_class: type[Solution]) -> str:
        return f"Instructions for using the solution {solution_class.model_construct().display_name}."

    @staticmethod
    def _default_workflow(solution_class: type[Solution]) -> str:
        return f"Step-by-step workflow for using the solution {solution_class.model_construct().display_name}."

    @classmethod
    def from_solution_md(cls, definition_module: ModuleType, solution_class: type[Solution]) -> Self:
        path = cls._find_solution_md(definition_module)
        if path is None:
            return cls(
                instructions=cls._default_instructions(solution_class),
                workflow=cls._default_workflow(solution_class),
            )
        text = path.read_text(encoding="utf-8")
        instructions = cls._parse_section(text, "Instructions") or cls._default_instructions(solution_class)
        workflow = cls._parse_section(text, "Workflow") or cls._default_workflow(solution_class)
        return cls(instructions=instructions, workflow=workflow)
