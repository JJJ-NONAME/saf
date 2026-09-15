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

from ansys.saf.glow._events.ievent_manager import EventPayload, EventSourceIdentifier, IEventListener, IEventManager
from ansys.saf.glow._repository.abstract_repository import (
    AbstractRepositorySession,
    AbstractRepositorySessionFactory,
    ProjectLockSpecification,
)


class RepositoryEventManager(IEventManager):
    def __init__(
        self,
        session_factory: AbstractRepositorySessionFactory,
    ) -> None:
        self._session_factory = session_factory

    @asynccontextmanager
    async def project_locked_session(
        self,
        project_id: str,
    ) -> AsyncGenerator[AbstractRepositorySession]:
        async with self._session_factory.get_session(
            project_id=project_id,
            lock_spec=ProjectLockSpecification(),
            modification=True,
            update_modification_date=False,
        ) as session:
            yield session

    async def create_event_listener(self, event_source_identifier: EventSourceIdentifier) -> IEventListener:
        """Creates an event listener for the caller to receive events."""
        async with self.project_locked_session(event_source_identifier.project_id) as session:
            listener_id = await session.create_event_listener(event_source_identifier)
            return RepositoryEventListener(self, event_source_identifier.project_id, listener_id)

    async def store_event(self, event_source_identifier: EventSourceIdentifier, event: EventPayload) -> None:
        """Stores an event for transmission to listeners"""
        async with self.project_locked_session(event_source_identifier.project_id) as session:
            await session.store_event(event_source_identifier, event)


class RepositoryEventListener(IEventListener):
    def __init__(self, event_manager: RepositoryEventManager, project_id: str, listener_id: str) -> None:
        self._event_manager = event_manager
        self._project_id = project_id
        self._listener_id = listener_id

    async def get_new_events_and_purge_queue(self) -> None | list[EventPayload]:
        """fetches all events that have not been processed by this listener"""
        async with self._event_manager.project_locked_session(self._project_id) as session:
            return await session.get_new_events_and_purge_queue(self._listener_id)

    async def destroy(self) -> None:
        """Cleans up any resources used by this listener"""
        async with self._event_manager.project_locked_session(self._project_id) as session:
            await session.destroy_event_listener(self._listener_id)
