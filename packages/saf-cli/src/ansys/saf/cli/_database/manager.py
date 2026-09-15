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
import os
from pathlib import Path
import platform

import click
from pydantic import ValidationError

from ansys.saf.cli._database.models import SolutionDatabase, SolutionRegistry


class SolutionDatabaseManager:
    def __init__(self) -> None:
        self._db_path = self.get_solution_database_path()
        self._db = self._load_solution_database()

    @classmethod
    def get_solution_database_path(cls) -> Path:
        if platform.system() == "Windows":
            directory = Path(os.environ["APPDATA"])
        elif platform.system() == "Linux":
            directory = Path(os.getenv("XDG_DATA_HOME", "~/.local/share")).expanduser()
        else:
            raise ValueError("Unsupported operating system")
        return directory / "ansys" / "saf" / "cli" / "solution_db.json"

    def _load_solution_database(self) -> SolutionDatabase:
        db_raw = self._db_path.read_text() if self._db_path.is_file() else ""
        try:
            return SolutionDatabase.model_validate_json(db_raw or json.dumps({}))
        except ValidationError:
            click.secho(
                "The solution database is invalid.",
                err=True,
                fg="red",
            )
            click.secho(
                f"You may need to delete it from '{SolutionDatabaseManager.get_solution_database_path()}'",
                err=True,
                fg="red",
            )
            raise

    def _save_solution_database(self):
        if not self._db_path.is_file():
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_path.write_text(self._db.model_dump_json())

    def store_solution(self, solution: SolutionRegistry) -> None:
        if solution not in self._db.solutions:
            self._db.solutions.append(solution)
            self._save_solution_database()
        else:
            solution_in_db = next(db_solution for db_solution in self._db.solutions if db_solution == solution)
            if solution_in_db.display_name != solution.display_name:
                solution_in_db.display_name = solution.display_name
                self._save_solution_database()

    def get_solutions_grouped_by_name(self) -> dict[str, list[SolutionRegistry]]:
        solutions_by_name: dict[str, list[SolutionRegistry]] = {}
        for solution in self._db.solutions:
            if not solution.is_valid:
                continue
            if solution.name not in solutions_by_name:
                solutions_by_name[solution.name] = []
            solutions_by_name[solution.name].append(solution)
        return solutions_by_name

    def get_solutions_by_name(self, solution_name: str) -> list[SolutionRegistry]:
        return [solution for solution in self._db.solutions if solution.name == solution_name and solution.is_valid]

    def get_solution_by_root_dir(self, solution_root_dir: Path) -> SolutionRegistry | None:
        solutions = [
            solution for solution in self._db.solutions if solution.root_dir == solution_root_dir and solution.is_valid
        ]
        if len(solutions) > 1:
            raise ValueError(f"Multiple solutions found with the root directory {solution_root_dir}")
        return solutions[0] if solutions else None
