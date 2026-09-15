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

from asgi_lifespan import LifespanManager
from fastapi import status
from httpx2 import ASGITransport, AsyncClient
import pytest
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from ansys.saf.glow._config.settings import DatabaseType, Settings
from ansys.saf.glow._crud.solution_configuration_models import (
    GLOW_SCHEMA_VERSION,
    Base,
    SolutionConfiguration,
    SolutionConfigurationSQL,
    get_default_solution_configuration,
)
from ansys.saf.glow._crud.solution_configuration_relational import RelationalSolutionConfigurationCRUD
from ansys.saf.glow._server.dependencies import SettingsDep, get_solution_configuration_crud
from tests.mocks.solutions import solution_configuration
from tests.unit.conftest import MOCK_APP_STARTUP_TIMEOUT, build_mock_app

# These tests assume that the DB is brand new every time, thus we parametrize settings to force creating a new DB
# in every test.
pytestmark = pytest.mark.parametrize(
    "settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = solution_configuration


@pytest.fixture
def default_solution_configuration() -> SolutionConfiguration:
    return get_default_solution_configuration(SolutionConfiguration)


class TestSolutionConfiguration:
    async def test_get_default_solution_configuration(
        self,
        async_client: AsyncClient,
        default_solution_configuration: SolutionConfiguration,
    ):
        """Test that the default solution configuration is loaded when launching the app and it can be retrieved."""
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert SolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_get_default_solution_configuration_schema(
        self,
        async_client: AsyncClient,
        default_solution_configuration: SolutionConfiguration,
    ):
        """Test that the default solution configuration schema can be retrieved."""
        expected_schema = SolutionConfiguration.model_json_schema()
        response = await async_client.get("/solution-configuration/schema")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_schema

    async def test_modify_empty_fields_solution_configuration(
        self,
        async_client: AsyncClient,
        default_solution_configuration: SolutionConfiguration,
    ):
        """Test that modifying the solution configuration with empty data returns 200 and
        does not modify the stored config."""
        response = await async_client.put("/solution-configuration", json={})
        assert response.status_code == status.HTTP_200_OK
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert SolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_modify_extra_fields_solution_configuration(
        self,
        async_client: AsyncClient,
        default_solution_configuration: SolutionConfiguration,
    ):
        """Test that modifying the solution configuration with extra fields returns 422 and
        does not modify the stored config."""
        response = await async_client.put("/solution-configuration", json={"my_extra_field": "hello"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert "Extra inputs are not permitted" in response.json()["detail"]
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert SolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_modify_glow_schema_version_raises_error(
        self,
        async_client: AsyncClient,
        default_solution_configuration: SolutionConfiguration,
    ):
        """Test that modifying the glow schema version raises a validation error."""
        response = await async_client.put("/solution-configuration", json={"glow_schema_version": 2})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert "Value error, GLOW schema version mismatch: 2. Expected 1." in response.json()["detail"]
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert SolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_modify_solution_schema_version_raises_error(
        self,
        async_client: AsyncClient,
        default_solution_configuration: SolutionConfiguration,
    ):
        """Test that modifying the solution schema version raises a validation error."""
        response = await async_client.put("/solution-configuration", json={"solution_schema_version": 2})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert "Value error, Solution schema version mismatch: 2. Expected 1." in response.json()["detail"]
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert SolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_launch_without_solution_configuration_table(
        self,
        settings: Settings,
        default_solution_configuration: SolutionConfiguration,
    ):
        """Test that trying to launch the app with an existing DB that doesn't have solution configuration table,
        initializes the table and inserts the default value."""

        async def _get_mocked_solution_configuration_crud(settings: SettingsDep):
            class MockedRelationalSolutionConfigurationCRUD(RelationalSolutionConfigurationCRUD[SolutionConfiguration]):
                async def initialize_database(self, default_solution_configuration: SolutionConfiguration) -> None:
                    return

            crud = MockedRelationalSolutionConfigurationCRUD(
                settings.glow_database_type,
                settings.computed_database_location,
                SolutionConfiguration,
            )
            await crud.initialize_database(default_solution_configuration)
            return crud

        # GIVEN: app initializes DB but doesn't create the table
        app = build_mock_app(settings, solution)
        app.dependency_overrides[get_solution_configuration_crud] = _get_mocked_solution_configuration_crud
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client,
        ):
            response = await async_client.get("/projects")
            assert response.status_code == status.HTTP_200_OK
            # WHEN: trying to get the solution configuration
            response = await async_client.get("/solution-configuration")
            # THEN: request returns 500
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"].startswith("The database schema is invalid")

        # WHEN: re-launching the app with the same DB and the proper initialization
        app = build_mock_app(settings, solution)
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client,
        ):
            # THEN: table is created, default solution configuration is inserted and can be retrieved
            response = await async_client.get("/solution-configuration")
            assert response.status_code == status.HTTP_200_OK
            assert SolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_launch_with_wrong_schema_version(
        self,
        settings: Settings,
        default_solution_configuration: SolutionConfiguration,
    ):
        """Test that trying to launch the app with a loaded solution configuration that has a different schema version,
        raises an Exception."""

        modified_schema_version = GLOW_SCHEMA_VERSION + 1

        async def _get_mocked_solution_configuration_crud(settings: SettingsDep):
            class MockedRelationalSolutionConfigurationCRUD(RelationalSolutionConfigurationCRUD[SolutionConfiguration]):
                async def initialize_database(self, default_solution_configuration: SolutionConfiguration) -> None:
                    engine = create_async_engine(self._database_url, echo=True)
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)

                    async with self._get_session() as session:
                        session.add(
                            SolutionConfigurationSQL(
                                id=0,
                                configuration={
                                    "glow_schema_version": modified_schema_version,
                                },
                            ),
                        )

            crud = MockedRelationalSolutionConfigurationCRUD(
                settings.glow_database_type,
                settings.computed_database_location,
                SolutionConfiguration,
            )
            await crud.initialize_database(default_solution_configuration)
            return crud

        expected_error = (
            "1 validation error for SolutionConfiguration\nglow_schema_version\n  Value error,"
            f" GLOW schema version mismatch: {modified_schema_version}. Expected {GLOW_SCHEMA_VERSION}."
        )

        # GIVEN: app initializes DB with expected table and an entry with wrong glow_schema_version.
        app = build_mock_app(settings, solution)
        app.dependency_overrides[get_solution_configuration_crud] = _get_mocked_solution_configuration_crud
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client,
        ):
            # WHEN: trying to get the solution configuration
            response = await async_client.get("/solution-configuration")
            # THEN: returns 422
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert response.json()["detail"].startswith(expected_error)

        # WHEN: re-launching the app with the same DB and the proper initialization
        app = build_mock_app(settings, solution)
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client,
        ):
            # WHEN: trying to get the solution configuration
            response = await async_client.get("/solution-configuration")
            # THEN: returns 422
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert response.json()["detail"].startswith(expected_error)

    async def test_launch_with_empty_table(
        self,
        settings: Settings,
        default_solution_configuration: SolutionConfiguration,
    ):
        """Test that trying to launch the app with an existing DB that has the solution configuration table but empty,
        inserts the default value when initializing."""

        async def _get_mocked_solution_configuration_crud(settings: SettingsDep):
            class MockedRelationalSolutionConfigurationCRUD(RelationalSolutionConfigurationCRUD[SolutionConfiguration]):
                async def initialize_database(self, default_solution_configuration: SolutionConfiguration) -> None:
                    engine = create_async_engine(self._database_url, echo=True)
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)

            crud = MockedRelationalSolutionConfigurationCRUD(
                settings.glow_database_type,
                settings.computed_database_location,
                SolutionConfiguration,
            )
            await crud.initialize_database(default_solution_configuration)
            return crud

        # GIVEN: app initializes DB with expected table but without any entry.
        app = build_mock_app(settings, solution)
        app.dependency_overrides[get_solution_configuration_crud] = _get_mocked_solution_configuration_crud
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client,
        ):
            # WHEN: trying to get the solution configuration
            response = await async_client.get("/solution-configuration")
            # THEN: returns 404
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Solution configuration not found."

        # WHEN: re-launching the app with the same DB and the proper initialization
        app = build_mock_app(settings, solution)
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client,
        ):
            # THEN: default solution configuration is inserted and can be retrieved
            response = await async_client.get("/solution-configuration")
            assert response.status_code == status.HTTP_200_OK
            assert SolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_launch_with_table_with_wrong_schema(
        self,
        settings: Settings,
        default_solution_configuration: SolutionConfiguration,
    ):
        """Test that trying to launch the app with an existing DB that has a solution configuration table but with
        a wrong schema, raises an Exception."""

        class MockBase(AsyncAttrs, DeclarativeBase):
            pass

        class MockSolutionConfigurationSQL(MockBase):  # pyright: ignore[reportUnusedClass]
            __tablename__ = "solution_configuration"

            id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, default=0)
            my_another_field: Mapped[int] = mapped_column(Integer)
            my_field: Mapped[str] = mapped_column(String)

        async def _get_mocked_solution_configuration_crud(settings: SettingsDep):
            class MockedRelationalSolutionConfigurationCRUD(RelationalSolutionConfigurationCRUD[SolutionConfiguration]):
                async def initialize_database(self, default_solution_configuration: SolutionConfiguration) -> None:
                    engine = create_async_engine(self._database_url, echo=True)
                    async with engine.begin() as conn:
                        await conn.run_sync(MockBase.metadata.create_all)

            crud = MockedRelationalSolutionConfigurationCRUD(
                settings.glow_database_type,
                settings.computed_database_location,
                SolutionConfiguration,
            )
            await crud.initialize_database(default_solution_configuration)
            return crud

        # GIVEN: app initializes DB with expected table but with wrong schema
        app = build_mock_app(settings, solution)
        app.dependency_overrides[get_solution_configuration_crud] = _get_mocked_solution_configuration_crud
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client,
        ):
            # WHEN: trying to get the solution configuration
            response = await async_client.get("/solution-configuration")
            # THEN: request returns 500
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"].startswith("The database schema is invalid")

        # WHEN: re-launching the app with the same DB and the proper initialization
        app = build_mock_app(settings, solution)
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client,
        ):
            # WHEN: trying to get the solution configuration
            response = await async_client.get("/solution-configuration")
            # THEN: request returns 500
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"].startswith("The database schema is invalid")
