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

# SQLite's default busy timeout of 5s is easily exceeded on high-latency storage such as a network
# share, where lock contention then surfaces as "database is locked" or "unable to open database file".
# This module provides a helper function to create an async SQLAlchemy engine with an increased
# busy timeout for SQLite, mitigating lock contention issues on high-latency storage.

from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

SQLITE_BUSY_TIMEOUT_SECONDS = 60


def create_glow_async_engine(database_url: str, **kwargs: Any) -> AsyncEngine:
    """Create an async engine, applying the SQLite busy-timeout tuning when relevant."""
    if not database_url.startswith("sqlite"):
        return create_async_engine(database_url, **kwargs)

    return create_async_engine(
        database_url,
        connect_args={"timeout": SQLITE_BUSY_TIMEOUT_SECONDS},
        **kwargs,
    )
