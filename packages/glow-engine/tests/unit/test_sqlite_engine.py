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

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from ansys.saf.glow._config.const import DatabaseType, Deployment
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._crud.solution_configuration_models import (
    SolutionConfiguration,
    get_default_solution_configuration,
)
from ansys.saf.glow._crud.solution_configuration_relational import RelationalSolutionConfigurationCRUD
from ansys.saf.glow._repository.engine import SQLITE_BUSY_TIMEOUT_SECONDS
import ansys.saf.glow._repository.relational as relational_module
from ansys.saf.glow._repository.relational import RelationalSessionFactory
from ansys.saf.glow._repository.sqlite_factory import SqliteSessionFactory
from ansys.saf.glow._server.dependencies import _get_repository  # pyright: ignore[reportPrivateUsage]
from ansys.saf.glow._server.solution import SolutionService
import tests.mocks.solutions.minimal_solution as minimal_solution_module


def _make_sqlite_settings(database_location: Path) -> Settings:
    return Settings(
        glow_solution_definition=minimal_solution_module.__name__,
        glow_deployment=Deployment.Desktop,
        glow_database_location=database_location,
    )


@pytest.fixture(autouse=True)
def _reset_schema_initialization_guard() -> Generator[None]:  # pyright: ignore[reportUnusedFunction]
    RelationalSessionFactory._the_url_of_the_last_database_that_was_initialized = None  # pyright: ignore[reportPrivateUsage]
    yield
    RelationalSessionFactory._the_url_of_the_last_database_that_was_initialized = None  # pyright: ignore[reportPrivateUsage]


@pytest.mark.parametrize("solution_service", [minimal_solution_module], indirect=True)
async def test_schema_initialization_runs_once_across_requests(
    tmp_path: Path,
    solution_service: SolutionService,
    mocker: MockerFixture,
) -> None:
    database_location = tmp_path / "shared.sqlite"
    settings = _make_sqlite_settings(database_location)

    populate_lock_tables_spy = mocker.spy(RelationalSessionFactory, "_populate_lock_tables")
    debug_spy = mocker.spy(relational_module.logger, "debug")

    async with _get_repository(settings, solution_service).get_session():
        pass
    async with _get_repository(settings, solution_service).get_session():
        pass

    assert populate_lock_tables_spy.call_count == 1
    assert sum("Initializing database at" in call.args[0] for call in debug_spy.call_args_list) == 1


@pytest.mark.parametrize("solution_service", [minimal_solution_module], indirect=True)
async def test_second_session_issues_no_schema_sql(
    tmp_path: Path,
    solution_service: SolutionService,
) -> None:
    database_location = tmp_path / "no_repeat_sql.sqlite"
    settings = _make_sqlite_settings(database_location)

    async with _get_repository(settings, solution_service).get_session():
        pass

    statements: list[str] = []

    def _record_statement(_conn: Any, _cursor: Any, statement: str, *_args: Any) -> None:
        statements.append(statement)

    event.listen(Engine, "before_cursor_execute", _record_statement)
    try:
        async with _get_repository(settings, solution_service).get_session():
            pass
    finally:
        event.remove(Engine, "before_cursor_execute", _record_statement)

    schema_statements = [
        s
        for s in statements
        if any(keyword in s.upper() for keyword in ("CREATE TABLE", "ALTER TABLE", "PRAGMA TABLE_INFO"))
    ]
    assert schema_statements == []


@pytest.mark.parametrize("solution_service", [minimal_solution_module], indirect=True)
async def test_unrelated_operational_error_is_not_swallowed(
    tmp_path: Path,
    solution_service: SolutionService,
) -> None:
    settings = _make_sqlite_settings(tmp_path / "placeholder.sqlite")
    factory = SqliteSessionFactory(settings, solution_service)
    # point the factory at a directory that does not exist so SQLite raises a real,
    # unrelated OperationalError ("unable to open database file") instead of "already exists"
    factory._database_url = f"sqlite+aiosqlite:///{(tmp_path / 'missing_dir' / 'db.sqlite').as_posix()}"  # pyright: ignore[reportPrivateUsage]

    with pytest.raises(OperationalError, match="unable to open database file"):
        async with factory.get_session():
            pass


async def test_solution_configuration_engine_receives_sqlite_tuning(tmp_path: Path) -> None:
    database_location = tmp_path / "solution_configuration.sqlite"
    crud = RelationalSolutionConfigurationCRUD(DatabaseType.Sqlite, database_location, SolutionConfiguration)
    await crud.initialize_database(get_default_solution_configuration(SolutionConfiguration))

    async with crud._get_session() as session:  # pyright: ignore[reportPrivateUsage]
        busy_timeout = (await session.execute(text("PRAGMA busy_timeout"))).scalar()

    assert busy_timeout == SQLITE_BUSY_TIMEOUT_SECONDS * 1000
