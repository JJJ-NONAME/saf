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

import sqlite3

import asyncpg  # pyright: ignore[reportMissingTypeStubs]
from fastapi import status
from httpx2 import AsyncClient
import pytest

from ansys.saf.glow._config.settings import DatabaseType, Settings
from tests.mocks.solutions import extended_solution_configuration_not_used

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = extended_solution_configuration_not_used


async def test_solution_configuration_feature_disabled_if_not_defined(settings: Settings, async_client: AsyncClient):
    """Test that the solution configuration table is not created if Solution does not define solution_configuration
    field."""
    response = await async_client.get("/projects")
    response.raise_for_status()

    # Solution configurations routes are not available
    response = await async_client.get("/solution-configuration")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"

    response = await async_client.put("/solution-configuration")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"

    # Solution configuration table is not created
    if settings.glow_database_type == DatabaseType.Sqlite:
        with sqlite3.connect(str(settings.computed_database_location)) as conn:  # noqa: SIM117
            with pytest.raises(sqlite3.OperationalError, match="no such table: solution_configuration"):
                conn.execute("SELECT * FROM solution_configuration")
    else:
        conn = await asyncpg.connect(settings.computed_database_location.unicode_string())  # type: ignore
        try:
            with pytest.raises(
                asyncpg.exceptions.UndefinedTableError,
                match='relation "solution_configuration" does not exist',
            ):
                await conn.fetch("SELECT * FROM solution_configuration")  # type: ignore
        finally:
            conn.close()  # type: ignore
