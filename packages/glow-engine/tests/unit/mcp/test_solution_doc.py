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
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from ansys.saf.glow._core.solution import Solution
from ansys.saf.glow._mcp.solution_doc import SolutionDoc

TEST_SOLUTION_DISPLAY_NAME = "MySolution"
DEFAULT_INSTRUCTIONS = f"Instructions for using the solution {TEST_SOLUTION_DISPLAY_NAME}."
DEFAULT_WORKFLOW = f"Step-by-step workflow for using the solution {TEST_SOLUTION_DISPLAY_NAME}."


class TestSolution(Solution):
    display_name: str = TEST_SOLUTION_DISPLAY_NAME


def test_returns_default_doc_when_no_module_file():
    module = MagicMock(spec=ModuleType)
    module.__file__ = None

    doc = SolutionDoc.from_solution_md(module, TestSolution)
    assert doc.instructions == DEFAULT_INSTRUCTIONS
    assert doc.workflow == DEFAULT_WORKFLOW


def test_returns_default_doc_when_no_solution_md(tmp_path: Path):
    module = MagicMock(spec=ModuleType)
    module.__file__ = str(tmp_path / "definition.py")

    doc = SolutionDoc.from_solution_md(module, TestSolution)
    assert doc.instructions == DEFAULT_INSTRUCTIONS
    assert doc.workflow == DEFAULT_WORKFLOW


def test_parses_instructions_and_workflow(tmp_path: Path):
    module = MagicMock(spec=ModuleType)
    module.__file__ = str(tmp_path / "definition.py")

    content = (
        "# My initial Header\n## Instructions\nFollow these steps.\n## Workflow\nRun the solver.\n"
        "## Other Section\nThis should be ignored."
    )
    (tmp_path / "SOLUTION.md").write_text(content, encoding="utf-8")

    doc = SolutionDoc.from_solution_md(module, TestSolution)
    assert doc.instructions == "Follow these steps."
    assert doc.workflow == "Run the solver."


@pytest.mark.parametrize(
    ("solution_md_content", "expected_instructions", "expected_workflow"),
    [
        (
            "## Instructions\nOnly instructions here.",
            "Only instructions here.",
            DEFAULT_WORKFLOW,
        ),
        (
            "## Workflow\nOnly workflow here.",
            DEFAULT_INSTRUCTIONS,
            "Only workflow here.",
        ),
    ],
)
def test_missing_section_defaults_to_default_doc(
    tmp_path: Path,
    solution_md_content: str,
    expected_instructions: str,
    expected_workflow: str,
):
    module = MagicMock(spec=ModuleType)
    module.__file__ = str(tmp_path / "definition.py")

    (tmp_path / "SOLUTION.md").write_text(solution_md_content, encoding="utf-8")

    doc = SolutionDoc.from_solution_md(module, TestSolution)
    assert doc.instructions == expected_instructions
    assert doc.workflow == expected_workflow


def test_empty_solution_md_returns_default_doc(tmp_path: Path):
    module = MagicMock(spec=ModuleType)
    module.__file__ = str(tmp_path / "definition.py")

    (tmp_path / "SOLUTION.md").write_text("", encoding="utf-8")

    doc = SolutionDoc.from_solution_md(module, TestSolution)
    assert doc.instructions == DEFAULT_INSTRUCTIONS
    assert doc.workflow == DEFAULT_WORKFLOW
