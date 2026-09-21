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

"""Proves `create_glow_async_engine`'s busy_timeout lets a write survive real, sustained SQLite
contention (e.g. an anti-virus scan or a slow network share) that a plain engine's default 5s
SQLite timeout does not.
"""

import asyncio
from pathlib import Path
import sqlite3
import threading
import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ansys.saf.glow._repository.engine import create_glow_async_engine

LOCK_HOLD_SECONDS = 8.0


def _create_schema(database_path: Path) -> None:
    conn = sqlite3.connect(str(database_path))
    try:
        conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, value INTEGER)")
        conn.commit()
    finally:
        conn.close()


def _hold_exclusive_lock(database_path: Path, lock_acquired: threading.Event) -> None:
    # isolation_level=None puts the connection in autocommit mode so our own explicit
    # BEGIN/COMMIT are the only transaction boundaries in play here
    conn = sqlite3.connect(str(database_path), isolation_level=None)
    try:
        conn.execute("BEGIN EXCLUSIVE")
        lock_acquired.set()
        time.sleep(LOCK_HOLD_SECONDS)
        conn.commit()
    finally:
        conn.close()


async def _insert_without_preceding_select(engine: AsyncEngine, value: int) -> None:
    # a SELECT before the INSERT would take a SHARED lock and promote straight to RESERVED,
    # which bypasses SQLite's busy handler; the write must be the first statement of the
    # transaction for the busy_timeout to actually be exercised
    async with engine.connect() as conn:
        await conn.execute(text("INSERT INTO t (value) VALUES (:value)"), {"value": value})
        await conn.commit()


async def test_write_waits_for_lock_held_longer_than_default_timeout(tmp_path: Path) -> None:
    database_path = tmp_path / "contention.sqlite"
    _create_schema(database_path)
    database_url = f"sqlite+aiosqlite:///{database_path.as_posix()}"

    lock_acquired = threading.Event()
    holder_thread = threading.Thread(target=_hold_exclusive_lock, args=(database_path, lock_acquired), daemon=True)
    holder_thread.start()
    assert lock_acquired.wait(timeout=5), "background thread failed to acquire the exclusive lock"

    glow_engine = create_glow_async_engine(database_url)
    control_engine = create_async_engine(database_url)  # plain engine, SQLite's default 5s timeout

    try:
        glow_result, control_result = await asyncio.wait_for(
            asyncio.gather(
                _insert_without_preceding_select(glow_engine, 1),
                _insert_without_preceding_select(control_engine, 2),
                return_exceptions=True,
            ),
            timeout=LOCK_HOLD_SECONDS + 20,
        )
    finally:
        holder_thread.join(timeout=LOCK_HOLD_SECONDS + 5)
        await glow_engine.dispose()
        await control_engine.dispose()

    # the glow-tuned engine's 60s busy_timeout outlasts the 8s lock, so its write succeeds
    assert glow_result is None
    # the untuned engine's default 5s timeout expires before the lock is released
    assert isinstance(control_result, OperationalError)
    assert "database is locked" in str(control_result)
