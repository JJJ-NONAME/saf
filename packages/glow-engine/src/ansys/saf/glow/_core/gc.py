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

from contextlib import asynccontextmanager
import json
import logging
from pathlib import Path
from typing import Protocol, TypeVar
import uuid

from fastapi import BackgroundTasks
from opentelemetry import trace

from ansys.saf.glow._bdm.multiplexor import SafMultiplexorStorageScopeFactory
from ansys.saf.glow._config.const import DatabaseType
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._core.solution import Solution
from ansys.saf.glow._crud.crud import Crud
from ansys.saf.glow._repository.engine import create_glow_async_engine
from ansys.saf.glow._repository.postgresql import PostgresqlSessionFactory
from ansys.saf.glow._repository.sqlite_factory import SqliteSessionFactory
from ansys.saf.glow._server.models import BdmLockModel
from ansys.saf.glow._server.solution import SolutionService

T = TypeVar("T", bound=Solution)
tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class IBdmLocks(Protocol):
    """A collection of bdm lock which purpose is to prohibit garbage collection as long as it
    contains bdm transaction.

    There are processes in the GLOW system where the entities referenced by handles must remain immutable.
    This implies that garbage collection cannot occur during these processes.
    We do this to ensure that solution developers can assume entity immutability for the duration of processes
    when their code is running.
    Those processes are materialized with those bdm locks.
    """

    async def add(self) -> BdmLockModel:
        """Add a bdm lock."""
        ...

    async def remove(self, lock_id: uuid.UUID) -> None:
        """Remove a bdm lock."""
        ...


class BdmLocksDb(IBdmLocks):
    """An IBdmLocks implementation using the internal database."""

    def __init__(
        self,
        project_id: str,
        crud: Crud,
        storage_factory: SafMultiplexorStorageScopeFactory,
        background_tasks: BackgroundTasks,
    ):
        self._project_id = project_id
        self._crud = crud
        self._storage_factory = storage_factory
        self._background_tasks = background_tasks

    async def add(self) -> BdmLockModel:
        with tracer.start_as_current_span("bdm_locks_db.add"):
            return await self._crud.add_bdm_lock(self._project_id)

    async def remove(self, lock_id: uuid.UUID) -> None:
        with tracer.start_as_current_span("bdm_locks_db.remove"):
            await self._crud.remove_bdm_lock(
                lock_id=lock_id,
                project_id=self._project_id,
                storage_factory=self._storage_factory,
                background_tasks=self._background_tasks,
            )


class BdmLocksNoOp(IBdmLocks):
    """An IBdmLocks not doing anything, used when garbage collection is disabled."""

    async def add(self) -> BdmLockModel:
        return BdmLockModel.model_construct()

    async def remove(self, lock_id: uuid.UUID) -> None:
        return


@asynccontextmanager
async def bdm_garbage_collector(bdm_locks: IBdmLocks):
    """A context manager used to prevent BDM garbage collection during its scope.
    In the end of the scope, the BDM garbage collection may be triggered if there is no other bdm lock.
    """
    bdm_lock = await bdm_locks.add()
    yield
    await bdm_locks.remove(bdm_lock.id)


def create_bdm_db_locks(
    project_id: str,
    settings: Settings,
    storage_factory: SafMultiplexorStorageScopeFactory,
    crud: Crud,
    background_tasks: BackgroundTasks,
):
    return (
        BdmLocksDb(
            project_id=project_id,
            crud=crud,
            storage_factory=storage_factory,
            background_tasks=background_tasks,
        )
        if not settings.glow_bdm_gc_disabled
        else BdmLocksNoOp()
    )


async def cleanup_expired_bdm_locks_on_startup(
    settings: Settings,
    solution_service: SolutionService,
) -> None:
    if settings.glow_bdm_gc_disabled:
        logger.debug("Garbage collection is disabled, skipping cleanup of expired BDM locks.")
        return

    db_location = settings.computed_database_location
    if settings.glow_database_type == DatabaseType.Sqlite:
        if isinstance(db_location, Path) and not db_location.exists():
            logger.debug("Skipping cleanup of expired BDM locks.")
            return
        session_factory = SqliteSessionFactory(settings, solution_service)
    else:
        database_url = str(db_location).replace("postgresql:", "postgresql+asyncpg:", 1)
        engine = create_glow_async_engine(database_url, json_serializer=json.dumps)
        try:
            async with engine.connect():
                # Check whether the PostgreSQL instance exists or not
                ...
        except Exception:
            logger.debug("Skipping cleanup of expired BDM locks.")
            return
        finally:
            await engine.dispose()

        session_factory = PostgresqlSessionFactory(settings, solution_service)

    try:
        async with session_factory.get_session(
            modification=True,
        ) as session:
            await session.remove_expired_bdm_locks()
    except Exception:
        logger.exception("Failed to cleanup expired BDM locks on startup.")
