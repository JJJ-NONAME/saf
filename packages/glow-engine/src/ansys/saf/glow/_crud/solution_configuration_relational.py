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

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
import platform
from typing import Any, TypeVar

from pydantic import BaseModel, PostgresDsn, ValidationError
from pydantic_core import MultiHostUrl
from sqlalchemy import update
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ansys.saf.glow._config.const import GLOW_OVERWRITE_SOLUTION_CONFIG, DatabaseType
from ansys.saf.glow._crud.solution_configuration_abstract import AbstractSolutionConfigurationCRUD
from ansys.saf.glow._crud.solution_configuration_models import (
    SOLUTION_CONFIGURATION_INDEX,
    Base,
    SolutionConfiguration,
    SolutionConfigurationSQL,
)
from ansys.saf.glow._repository.engine import create_glow_async_engine
from ansys.saf.glow._server.exceptions import MalformedDatabaseError, NotFoundError, UnprocessableEntityError

logger = logging.getLogger(__name__)
TModel = TypeVar("TModel", bound=BaseModel)
TSolutionConfig = TypeVar("TSolutionConfig", bound=SolutionConfiguration)


# Utility functions to convert SQLAlchemy objects <-> Pydantic models.
def _to_pydantic(
    db_object: SolutionConfigurationSQL,
    solution_configuration_type: type[TSolutionConfig],
) -> TSolutionConfig:
    return solution_configuration_type.model_validate(db_object.configuration)


def _to_db(pydantic_object: TSolutionConfig) -> SolutionConfigurationSQL:  # pyright: ignore[reportInvalidTypeVarUse]
    return SolutionConfigurationSQL(configuration=pydantic_object.model_dump())


class RelationalSolutionConfigurationCRUD(AbstractSolutionConfigurationCRUD[TSolutionConfig]):
    def __init__(
        self,
        db_type: DatabaseType,
        db_location: Path | PostgresDsn,
        solution_configuration_type: type[TSolutionConfig],
    ) -> None:
        self._db_type = db_type
        self._database_url = ""
        if db_type == DatabaseType.Sqlite and isinstance(db_location, Path):
            db_location.parent.mkdir(parents=True, exist_ok=True)
            if platform.system() == "Linux":
                self._database_url = db_location.as_uri().replace("file:", "sqlite+aiosqlite:/", 1)
            else:
                self._database_url = f"sqlite+aiosqlite:///{db_location.as_posix()}"
            logger.info(f"Using SQLite database at {self._database_url}")
        elif db_type == DatabaseType.PostgreSql and isinstance(db_location, MultiHostUrl | PostgresDsn):
            self._database_url = str(db_location).replace("postgresql:", "postgresql+asyncpg:", 1)
            logger.info(f"Using PostgreSQL database at {self._database_url}")
        else:
            raise ValueError(f"Invalid database configuration {db_type=} and {db_location=}.")
        self._solution_configuration_type = solution_configuration_type

    @asynccontextmanager
    async def _get_session(self) -> AsyncGenerator[AsyncSession, None]:
        engine = create_glow_async_engine(self._database_url)

        # Run all the transactions on the solution configuration as EXCLUSIVE / SERIALIZABLE.
        # (This means that each transaction has exclusive access to the database for its duration.)
        # We do this to avoid having to worry about any locking mechanisms for the solution configuration.
        if self._db_type == DatabaseType.Sqlite:
            engine = engine.execution_options(begin="EXCLUSIVE")
        elif self._db_type == DatabaseType.PostgreSql:
            engine = engine.execution_options(isolation_level="SERIALIZABLE")
        else:
            raise ValueError(f"Unsupported database type: {self._db_type}")
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session.begin() as session:
            # begin() internally manages commit()/rollback()
            try:
                yield session
            except (OperationalError, ProgrammingError) as e:
                # exception type depends on DB backend (SQLite -> OperationalError, PostgreSQL -> ProgrammingError)
                raise MalformedDatabaseError(str(e)) from None
            except ValidationError as e:
                raise UnprocessableEntityError(str(e)) from None

    async def initialize_database(self, default_solution_configuration: TSolutionConfig) -> None:
        engine = create_glow_async_engine(self._database_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with self._get_session() as session:
            solution_configuration_db = await session.get(SolutionConfigurationSQL, SOLUTION_CONFIGURATION_INDEX)
            if solution_configuration_db:
                try:
                    # convert to pydantic for validation
                    _to_pydantic(solution_configuration_db, self._solution_configuration_type)
                    return
                except ValidationError as exc:
                    if os.environ.get(GLOW_OVERWRITE_SOLUTION_CONFIG):
                        await session.delete(solution_configuration_db)
                        await session.flush()
                    else:
                        raise UnprocessableEntityError(str(exc)) from None

            default_solution_configuration_db = _to_db(default_solution_configuration)
            session.add(default_solution_configuration_db)

    async def get_solution_configuration(self) -> TSolutionConfig:
        async with self._get_session() as session:
            solution_configuration_db = await session.get(SolutionConfigurationSQL, SOLUTION_CONFIGURATION_INDEX)
            if not solution_configuration_db:
                raise NotFoundError("Solution configuration not found.")
            solution_configuration = _to_pydantic(solution_configuration_db, self._solution_configuration_type)
            return solution_configuration

    async def modify_solution_configuration(self, solution_configuration_modification: dict[str, Any]) -> None:
        async with self._get_session() as session:
            solution_configuration_db = await session.get(SolutionConfigurationSQL, SOLUTION_CONFIGURATION_INDEX)
            if not solution_configuration_db:
                raise NotFoundError("Solution configuration not found.")
            solution_configuration_dict = solution_configuration_db.configuration.copy()
            solution_configuration_dict.update(solution_configuration_modification)
            updated_solution_configuration = self._solution_configuration_type.model_validate(
                solution_configuration_dict,
            )
            # TODO: skip if nothing has changed.
            updated_solution_configuration_db = _to_db(updated_solution_configuration)
            statement = (
                update(SolutionConfigurationSQL)
                .where(SolutionConfigurationSQL.id == SOLUTION_CONFIGURATION_INDEX)
                .values(configuration=updated_solution_configuration_db.configuration)
            )
            await session.execute(statement)
