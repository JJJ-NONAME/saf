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
from pathlib import Path
from typing import Any

from ansys.saf.cli._database.manager import SolutionDatabaseManager
from ansys.saf.cli._database.models import SolutionDatabase, SolutionRegistry


def test_context_manager_with_non_existent_database(database_path: Path):
    # if no  database exists
    assert not database_path.is_file()
    # and we instantiate the database manager
    db_manager = SolutionDatabaseManager()
    # the database file is not created
    assert not database_path.is_file()
    # and the database object remains empty
    expected_db: dict[str, Any] = {}
    assert db_manager._db == SolutionDatabase.model_validate(expected_db)  # pyright: ignore[reportPrivateUsage]


def test_context_manager_with_existing_database(tmp_path_as_working_dir: Path, database_path: Path):
    # if a database file exists
    expected_db: dict[str, Any] = {
        "solutions": [
            {
                "name": "my_solution",
                "root_dir": (tmp_path_as_working_dir / "my/path" / "my_solution").as_posix(),
                "display_name": "My Solution",
            },
        ],
    }
    database_path.write_text(json.dumps(expected_db))
    # the database object contains the expected solution
    db_manager = SolutionDatabaseManager()
    assert db_manager._db == SolutionDatabase.model_validate(expected_db)  # pyright: ignore[reportPrivateUsage]


def test_store_solution(tmp_path_as_working_dir: Path, database_path: Path):
    # when no database exists
    assert not database_path.exists()
    solution_path = tmp_path_as_working_dir / "my/path" / "my_solution"
    solution_path.mkdir(parents=True, exist_ok=True)
    solution = SolutionRegistry(name="my_solution", root_dir=solution_path, display_name="My Solution")
    db_manager = SolutionDatabaseManager()
    # and we store a solution
    db_manager.store_solution(solution)
    expected_db: dict[str, Any] = {
        "solutions": [
            {
                "name": "my_solution",
                "root_dir": solution_path,
                "display_name": "My Solution",
            },
        ],
    }
    # the database file is created
    assert database_path.is_file()
    # and the database object contains the expected solution
    db_manager = SolutionDatabaseManager()
    assert db_manager._db == SolutionDatabase.model_validate(expected_db)  # pyright: ignore[reportPrivateUsage]


def test_store_two_different_solutions(tmp_path_as_working_dir: Path, database_path: Path):
    # when no database exists
    assert not database_path.exists()
    solution_path_1 = tmp_path_as_working_dir / "my/path" / "my_solution"
    solution_path_1.mkdir(parents=True, exist_ok=True)
    solution_path_2 = tmp_path_as_working_dir / "my/path" / "my_solution_2"
    solution_path_2.mkdir(parents=True, exist_ok=True)
    expected_db: dict[str, Any] = {
        "solutions": [
            {
                "name": "my_solution",
                "root_dir": solution_path_1,
                "display_name": "My Solution",
            },
            {
                "name": "my_solution_2",
                "root_dir": solution_path_2,
                "display_name": "My Solution",
            },
        ],
    }
    solution_1 = SolutionRegistry(name="my_solution", root_dir=solution_path_1, display_name="My Solution")
    solution_2 = SolutionRegistry(name="my_solution_2", root_dir=solution_path_2, display_name="My Solution")
    db_manager = SolutionDatabaseManager()
    # and we store two different solutions
    db_manager.store_solution(solution_1)
    db_manager.store_solution(solution_2)
    # the database file is created
    assert database_path.is_file()
    # and the database object contains the expected two solutions
    db_manager = SolutionDatabaseManager()
    assert db_manager._db == SolutionDatabase.model_validate(expected_db)  # pyright: ignore[reportPrivateUsage]


def test_store_two_identical_solutions(tmp_path_as_working_dir: Path, database_path: Path):
    # when no database exists
    assert not database_path.exists()
    solution_path = tmp_path_as_working_dir / "my/path" / "my_solution"
    solution_path.mkdir(parents=True, exist_ok=True)
    expected_db: dict[str, Any] = {
        "solutions": [
            {
                "name": "my_solution",
                "root_dir": solution_path,
                "display_name": "My Solution",
            },
        ],
    }
    solution = SolutionRegistry(name="my_solution", root_dir=solution_path, display_name="My Solution")
    db_manager = SolutionDatabaseManager()
    # and we store two identical solutions
    db_manager.store_solution(solution)
    db_manager.store_solution(solution)
    # the database file is created
    assert database_path.is_file()
    # and the database object contains a single solution
    db_manager = SolutionDatabaseManager()
    assert db_manager._db == SolutionDatabase.model_validate(expected_db)  # pyright: ignore[reportPrivateUsage]


def test_store_a_solution_and_recreate_it_with_different_display_name_changes_display_name(
    tmp_path_as_working_dir: Path,
    database_path: Path,
):
    # when no database exists
    assert not database_path.exists()
    solution_path = tmp_path_as_working_dir / "my/path" / "my_solution"
    solution_path.mkdir(parents=True, exist_ok=True)
    solution_display_name_1 = "My Solution"
    solution_display_name_2 = "Corrected My Solution"
    solution_1 = SolutionRegistry(name="my_solution", root_dir=solution_path, display_name=solution_display_name_1)
    solution_2 = SolutionRegistry(name="my_solution", root_dir=solution_path, display_name=solution_display_name_2)
    db_manager = SolutionDatabaseManager()
    # we store a solution
    db_manager.store_solution(solution_1)
    # and we store it again with a different display name
    db_manager.store_solution(solution_2)
    # the database file is created
    assert database_path.is_file()
    # and the database object contains a single solution with the updated display name
    db_manager = SolutionDatabaseManager()
    assert db_manager._db.solutions[0].display_name == solution_display_name_2  # pyright: ignore[reportPrivateUsage]


def test_non_existent_solutions_are_marked_as_invalid(tmp_path_as_working_dir: Path, database_path: Path):
    # when no database exists
    assert not database_path.exists()
    solution_path = tmp_path_as_working_dir / "my/path" / "my_solution"
    expected_db: dict[str, Any] = {
        "solutions": [
            {
                "name": "my_solution",
                "root_dir": solution_path,
                "display_name": "My Solution",
            },
        ],
    }
    # we store a solution without creating the corresponding directory
    solution = SolutionRegistry(name="my_solution", root_dir=solution_path, display_name="My Solution")
    db_manager = SolutionDatabaseManager()
    # and we store a solution without creating its directory
    db_manager.store_solution(solution)
    # the database file is created
    assert database_path.is_file()
    # and the database object contains a single invalid solution
    db_manager = SolutionDatabaseManager()
    assert db_manager._db == SolutionDatabase.model_validate(expected_db)  # pyright: ignore[reportPrivateUsage]
    assert not db_manager._db.solutions[0].is_valid  # pyright: ignore[reportPrivateUsage]


def test_get_solutions_grouped_by_name_with_no_repeated_name(tmp_path_as_working_dir: Path, database_path: Path):
    # when the database contains 3 solutions with different names
    solution_path_1 = tmp_path_as_working_dir / "my/path" / "my_solution"
    solution_path_1.mkdir(parents=True)
    solution_path_2 = tmp_path_as_working_dir / "my/path" / "my_solution_2"
    solution_path_2.mkdir(parents=True)
    solution_path_3 = tmp_path_as_working_dir / "my/path" / "my_solution_3"
    solution_path_3.mkdir(parents=True)
    expected_db = {
        "solutions": [
            {
                "name": "my_solution",
                "root_dir": solution_path_1.as_posix(),
                "display_name": "My Solution",
            },
            {
                "name": "my_solution_2",
                "root_dir": solution_path_2.as_posix(),
                "display_name": "My Solution",
            },
            {
                "name": "my_solution_3",
                "root_dir": solution_path_3.as_posix(),
                "display_name": "My Solution",
            },
        ],
    }
    database_path.write_text(json.dumps(expected_db))
    expected_dict = {
        "my_solution": [
            SolutionRegistry(name="my_solution", root_dir=solution_path_1, display_name="My Solution"),
        ],
        "my_solution_2": [
            SolutionRegistry(name="my_solution_2", root_dir=solution_path_2, display_name="My Solution"),
        ],
        "my_solution_3": [
            SolutionRegistry(name="my_solution_3", root_dir=solution_path_3, display_name="My Solution"),
        ],
    }
    # and we sort them by solution name
    db_manager = SolutionDatabaseManager()
    solution_by_name = db_manager.get_solutions_grouped_by_name()
    # every solution is listed under its corresponding name
    assert solution_by_name == expected_dict


def test_get_solutions_grouped_by_name_with_repeated_name(tmp_path_as_working_dir: Path, database_path: Path):
    # when the database contains 3 solutions 2 of which share the same name
    solution_path_1 = tmp_path_as_working_dir / "my/path" / "my_solution"
    solution_path_1.mkdir(parents=True)
    solution_path_2 = tmp_path_as_working_dir / "my/second/path" / "my_solution"
    solution_path_2.mkdir(parents=True)
    solution_path_3 = tmp_path_as_working_dir / "my/path" / "my_solution_3"
    solution_path_3.mkdir(parents=True)
    expected_db = {
        "solutions": [
            {
                "name": "my_solution",
                "root_dir": solution_path_1.as_posix(),
                "display_name": "My Solution",
            },
            {
                "name": "my_solution",
                "root_dir": solution_path_2.as_posix(),
                "display_name": "My Solution",
            },
            {
                "name": "my_solution_3",
                "root_dir": solution_path_3.as_posix(),
                "display_name": "My Solution",
            },
        ],
    }
    database_path.write_text(json.dumps(expected_db))
    expected_dict = {
        "my_solution": [
            SolutionRegistry(name="my_solution", root_dir=solution_path_1, display_name="My Solution"),
            SolutionRegistry(name="my_solution", root_dir=solution_path_2, display_name="My Solution"),
        ],
        "my_solution_3": [
            SolutionRegistry(name="my_solution_3", root_dir=solution_path_3, display_name="My Solution"),
        ],
    }
    # and we sort them by solution name
    db_manager = SolutionDatabaseManager()
    solution_by_name = db_manager.get_solutions_grouped_by_name()
    # every solution is listed under its corresponding name
    assert solution_by_name == expected_dict


def test_get_solutions_grouped_by_name_with_invalid_paths(tmp_path_as_working_dir: Path, database_path: Path):
    # when the database contains 2 solutions, 1 of which is invalid
    solution_path_1 = tmp_path_as_working_dir / "my/path" / "my_solution"
    solution_path_1.mkdir(parents=True)
    solution_path_2 = tmp_path_as_working_dir / "my/second/path" / "my_solution"
    expected_db = {
        "solutions": [
            {
                "name": "my_solution",
                "root_dir": solution_path_1.as_posix(),
                "display_name": "My Solution",
            },
            {
                "name": "my_solution",
                "root_dir": solution_path_2.as_posix(),
                "display_name": "My Solution",
            },
        ],
    }
    database_path.write_text(json.dumps(expected_db))
    expected_dict = {
        "my_solution": [
            SolutionRegistry(name="my_solution", root_dir=solution_path_1, display_name="My Solution"),
        ],
    }
    # and we sort them by solution name
    db_manager = SolutionDatabaseManager()
    solution_by_name = db_manager.get_solutions_grouped_by_name()
    # only solutions that are valid are returned
    assert solution_by_name == expected_dict


def test_get_solutions_by_name_for_inexistent_name():
    # when the database does not contain any solution
    # and we find them by solution name
    db_manager = SolutionDatabaseManager()
    solutions = db_manager.get_solutions_by_name("my_solution")
    # returns empty list
    assert not solutions


def test_get_solutions_by_name_including_invalid_solutions(tmp_path_as_working_dir: Path, database_path: Path):
    # when the database contains 2 solutions, 1 of which is invalid
    solution_path_1 = tmp_path_as_working_dir / "my/path" / "my_solution"
    solution_path_1.mkdir(parents=True)
    solution_path_2 = tmp_path_as_working_dir / "my/second/path" / "my_solution"
    expected_db = {
        "solutions": [
            {
                "name": "my_solution",
                "root_dir": solution_path_1.as_posix(),
                "display_name": "My Solution",
            },
            {
                "name": "my_solution",
                "root_dir": solution_path_2.as_posix(),
                "display_name": "My Solution",
            },
        ],
    }
    database_path.write_text(json.dumps(expected_db))

    # and we find them by solution name
    db_manager = SolutionDatabaseManager()
    solutions = db_manager.get_solutions_by_name("my_solution")
    # only solutions that are valid are returned
    assert solutions == [
        SolutionRegistry(name="my_solution", root_dir=solution_path_1, display_name="My Solution"),
    ]


def test_get_solution_by_root_dir_for_inexistent_path(tmp_path: Path):
    # when the database does not contain any solution
    # and we find them by root dir
    db_manager = SolutionDatabaseManager()
    solution = db_manager.get_solution_by_root_dir(tmp_path / "a")
    # returns None
    assert not solution


def test_get_solution_by_root_dir(tmp_path: Path, database_path: Path):
    # when the database contains one solution
    expected_db = {
        "solutions": [
            {
                "name": "my_solution",
                "root_dir": tmp_path.as_posix(),
                "display_name": "My Solution",
            },
        ],
    }
    database_path.write_text(json.dumps(expected_db))

    # and we find them by root dir
    db_manager = SolutionDatabaseManager()
    solution = db_manager.get_solution_by_root_dir(tmp_path)
    # only one solution is returned
    assert solution == SolutionRegistry(name="my_solution", root_dir=tmp_path, display_name="My Solution")


def test_get_solution_by_root_dir_for_invalid_solution(tmp_path: Path, database_path: Path):
    # when the database contains one solution that is invalid
    expected_db = {
        "solutions": [
            {
                "name": "my_solution",
                "root_dir": (tmp_path / "a").as_posix(),
                "display_name": "My Solution",
            },
        ],
    }
    database_path.write_text(json.dumps(expected_db))

    # and we find them by root dir
    db_manager = SolutionDatabaseManager()
    solution = db_manager.get_solution_by_root_dir(tmp_path)
    # returns None
    assert not solution
