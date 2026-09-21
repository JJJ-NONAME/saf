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
from sqlalchemy.ext.asyncio import create_async_engine

from ansys.saf.glow._config.const import GLOW_OVERWRITE_SOLUTION_CONFIG, DatabaseType
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._crud.solution_configuration_models import (
    Base,
    SolutionConfiguration,
    SolutionConfigurationSQL,
    get_default_solution_configuration,
)
from ansys.saf.glow._crud.solution_configuration_relational import RelationalSolutionConfigurationCRUD
from ansys.saf.glow._server.dependencies import SettingsDep, get_solution_configuration_crud
from tests.mocks.solutions import extended_solution_configuration
from tests.mocks.solutions.extended_solution_configuration import ExtendedSolutionConfiguration
from tests.unit.conftest import MOCK_APP_STARTUP_TIMEOUT, build_mock_app

# These tests assume that the DB is brand new every time, thus we parametrize settings to force creating a new DB
# in every test.
pytestmark = pytest.mark.parametrize(
    "settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = extended_solution_configuration


@pytest.fixture
def default_solution_configuration() -> ExtendedSolutionConfiguration:
    return get_default_solution_configuration(ExtendedSolutionConfiguration)


class TestExtendedSolutionConfiguration:
    async def test_get_default_solution_configuration(
        self,
        async_client: AsyncClient,
        default_solution_configuration: ExtendedSolutionConfiguration,
    ):
        """Test that the default solution configuration is loaded when launching the app and it can be retrieved."""
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert ExtendedSolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_get_default_solution_configuration_schema(
        self,
        async_client: AsyncClient,
        default_solution_configuration: ExtendedSolutionConfiguration,
    ):
        """Test that the default solution configuration schema can be retrieved."""
        expected_schema = ExtendedSolutionConfiguration.model_json_schema()
        response = await async_client.get("/solution-configuration/schema")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_schema

    async def test_full_modify_and_retrieve_solution_configuration(
        self,
        async_client: AsyncClient,
    ):
        """Test that the solution configuration can be modified entirely via PUT and future GETs return the modified
        values."""
        solution_configuration = ExtendedSolutionConfiguration(
            my_field=5,
            my_second_field="test",
        )
        response = await async_client.put("/solution-configuration", json=solution_configuration.model_dump())
        assert response.status_code == status.HTTP_200_OK
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert ExtendedSolutionConfiguration.model_validate(response.json()) == solution_configuration

    async def test_partial_modify_and_retrieve_solution_configuration(
        self,
        async_client: AsyncClient,
    ):
        """Test that the solution configuration can be modified partially via PUT and future GETs return the modified
        values."""
        solution_configuration = ExtendedSolutionConfiguration(
            my_field=5,
        )
        response = await async_client.put("/solution-configuration", json=solution_configuration.model_dump())
        assert response.status_code == status.HTTP_200_OK
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert ExtendedSolutionConfiguration.model_validate(response.json()) == solution_configuration

    async def test_modify_invalid_extended_solution_configuration(
        self,
        async_client: AsyncClient,
        default_solution_configuration: ExtendedSolutionConfiguration,
    ):
        """Test that modifying the solution configuration with a wrong value, based on a field_validator defined
        in the extended solution configuration, returns 422, and does not modify the stored config."""
        response = await async_client.put("/solution-configuration", json={"my_validated_field": "b"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert "Value error, Field 'my_validated_field' must start with 'a'." in response.json()["detail"]
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert ExtendedSolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_modify_invalid_multiple_fields_extended_solution_configuration(
        self,
        async_client: AsyncClient,
        default_solution_configuration: ExtendedSolutionConfiguration,
    ):
        """Test that modifying the solution configuration with wrong dependent values, based on a model_validator
        defined in the extended solution configuration, returns 422, and does not modify the stored config."""
        response = await async_client.put("/solution-configuration", json={"my_second_validated_field": "a"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert (
            "Value error, Field 'my_second_validated_field' must be different from 'my_validated_field'."
            in response.json()["detail"]
        )
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert ExtendedSolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_modify_back_to_default_solution_configuration(
        self,
        async_client: AsyncClient,
        default_solution_configuration: ExtendedSolutionConfiguration,
    ):
        """Test that the solution configuration can be modified back to its default values via PUT."""
        response = await async_client.put(
            "/solution-configuration",
            json={"my_field": 5},
        )
        response = await async_client.get("/solution-configuration")
        assert ExtendedSolutionConfiguration.model_validate(response.json()) == ExtendedSolutionConfiguration(
            my_field=5,
        )
        response = await async_client.put("/solution-configuration", json=default_solution_configuration.model_dump())
        assert response.status_code == status.HTTP_200_OK
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert ExtendedSolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_modify_wrong_type_solution_configuration(
        self,
        async_client: AsyncClient,
        default_solution_configuration: ExtendedSolutionConfiguration,
    ):
        """Test that modifying the solution configuration with a wrong value returns 422 and
        does not modify the stored config."""
        response = await async_client.put("/solution-configuration", json={"my_second_field": 1})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert "Input should be a valid string" in response.json()["detail"]
        response = await async_client.get("/solution-configuration")
        assert response.status_code == status.HTTP_200_OK
        assert ExtendedSolutionConfiguration.model_validate(response.json()) == default_solution_configuration

    async def test_launch_with_extended_solution_configuration_from_base_configuration(
        self,
        settings: Settings,
        default_solution_configuration: ExtendedSolutionConfiguration,
    ):
        """Test that you can launch the app with a new extended solution configuration that is different from the
        stored base solution configuration.."""

        async def _get_mocked_solution_configuration_crud(settings: SettingsDep):
            class MockedRelationalSolutionConfigurationCRUD(
                RelationalSolutionConfigurationCRUD[ExtendedSolutionConfiguration],
            ):
                async def initialize_database(
                    self,
                    default_solution_configuration: ExtendedSolutionConfiguration,
                ) -> None:
                    engine = create_async_engine(self._database_url, echo=True)
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)

                    async with self._get_session() as session:
                        session.add(
                            SolutionConfigurationSQL(
                                id=0,
                                configuration=SolutionConfiguration().model_dump(),
                            ),
                        )

            crud = MockedRelationalSolutionConfigurationCRUD(
                settings.glow_database_type,
                settings.computed_database_location,
                ExtendedSolutionConfiguration,
            )
            await crud.initialize_database(default_solution_configuration)
            return crud

        # GIVEN: app initializes DB with a correct base solution configuration
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
            response.raise_for_status()
            # THEN: returns 200 and returned one is the base + defaults of the extended config
            assert ExtendedSolutionConfiguration() == ExtendedSolutionConfiguration.model_validate(response.json())

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
            response.raise_for_status()
            # THEN: returns 200 and returned one is the base + defaults of the extended config
            assert ExtendedSolutionConfiguration() == ExtendedSolutionConfiguration.model_validate(response.json())

    @pytest.mark.parametrize(("glow_schema_version", "solution_schema_version"), [(1, 2), (2, 1)])
    async def test_launch_with_old_extended_solution_configuration(
        self,
        settings: Settings,
        default_solution_configuration: ExtendedSolutionConfiguration,
        glow_schema_version: int,
        solution_schema_version: int,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """Test that trying to launch the app with a solution configuration that is incompatible with the stored one
        due to a version mismatch raises a validation error unless we allow overwriting."""

        async def _get_mocked_solution_configuration_crud(settings: SettingsDep):
            class MockedRelationalSolutionConfigurationCRUD(
                RelationalSolutionConfigurationCRUD[ExtendedSolutionConfiguration],
            ):
                async def initialize_database(
                    self,
                    default_solution_configuration: ExtendedSolutionConfiguration,
                ) -> None:
                    engine = create_async_engine(self._database_url, echo=True)
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)

                    async with self._get_session() as session:
                        session.add(
                            SolutionConfigurationSQL(
                                id=0,
                                configuration={
                                    "glow_schema_version": glow_schema_version,
                                    "solution_schema_version": solution_schema_version,
                                },
                            ),
                        )

            crud = MockedRelationalSolutionConfigurationCRUD(
                settings.glow_database_type,
                settings.computed_database_location,
                ExtendedSolutionConfiguration,
            )
            await crud.initialize_database(default_solution_configuration)
            return crud

        # GIVEN: app initializes DB with a correct base solution configuration
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
            # THEN: returns 422 due to a version mismatch
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            if solution_schema_version == 2:
                assert "Solution schema version mismatch: 2. Expected 1." in response.json()["detail"]
            else:
                assert "GLOW schema version mismatch: 2. Expected 1." in response.json()["detail"]

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
            # THEN: returns 422 due to a version mismatch
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            if solution_schema_version == 2:
                assert "Solution schema version mismatch: 2. Expected 1." in response.json()["detail"]
            else:
                assert "GLOW schema version mismatch: 2. Expected 1." in response.json()["detail"]

        monkeypatch.setenv(GLOW_OVERWRITE_SOLUTION_CONFIG, "1")

        # WHEN: launching the app again with overwrite activated
        app = build_mock_app(settings, solution)
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client_2,
        ):
            # WHEN: trying to get the solution configuration
            response = await async_client_2.get("/solution-configuration")
            # THEN: the persisted solution configuration is replaced by the current one
            assert response.status_code == status.HTTP_200_OK
            assert ExtendedSolutionConfiguration.model_validate(response.json()) == ExtendedSolutionConfiguration(
                solution_schema_version=1,
                glow_schema_version=1,
            )

    async def test_launch_with_modified_solution_configuration(
        self,
        settings: Settings,
        async_client: AsyncClient,
    ):
        """Test that a modified solution config is not overwritten when relaunching the app."""
        # GIVEN: app with a modified solution configuration
        response = await async_client.put(
            "/solution-configuration",
            json={"my_field": 5, "my_second_field": "test"},
        )
        response.raise_for_status()

        # WHEN: launching the app again
        app = build_mock_app(settings, solution)
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client_2,
        ):
            # THEN: the modified solution configuration is preserved
            response = await async_client_2.get("/solution-configuration")
            assert response.status_code == status.HTTP_200_OK
            assert ExtendedSolutionConfiguration.model_validate(response.json()) == ExtendedSolutionConfiguration(
                my_field=5,
                my_second_field="test",
            )

    async def test_solution_configuration_not_found(
        self,
        settings: Settings,
        default_solution_configuration: ExtendedSolutionConfiguration,
    ):
        """Test that trying to get or modify an inexistent solution config returns 404."""

        async def _get_mocked_solution_configuration_crud(settings: SettingsDep):
            class MockedRelationalSolutionConfigurationCRUD(
                RelationalSolutionConfigurationCRUD[ExtendedSolutionConfiguration],
            ):
                async def initialize_database(
                    self,
                    default_solution_configuration: ExtendedSolutionConfiguration,
                ) -> None:
                    engine = create_async_engine(self._database_url, echo=True)
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)

            crud = MockedRelationalSolutionConfigurationCRUD(
                settings.glow_database_type,
                settings.computed_database_location,
                ExtendedSolutionConfiguration,
            )
            await crud.initialize_database(default_solution_configuration)
            return crud

        # GIVEN: app initializes DB with the correct table and schema, but without any entry
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

            # WHEN: trying to modify the solution configuration
            response = await async_client.put(
                "/solution-configuration",
                json={"my_field": 5, "my_second_field": "test"},
            )
            # THEN: returns 404
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Solution configuration not found."

    async def test_launch_with_wrong_solution_configuration(
        self,
        settings: Settings,
        default_solution_configuration: ExtendedSolutionConfiguration,
    ):
        """Test that trying to launch the app with a loaded solution configuration that is wrong raises an Exception."""

        async def _get_mocked_solution_configuration_crud(settings: SettingsDep):
            class MockedRelationalSolutionConfigurationCRUD(
                RelationalSolutionConfigurationCRUD[ExtendedSolutionConfiguration],
            ):
                async def initialize_database(
                    self,
                    default_solution_configuration: ExtendedSolutionConfiguration,
                ) -> None:
                    engine = create_async_engine(self._database_url, echo=True)
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)

                    async with self._get_session() as session:
                        session.add(
                            SolutionConfigurationSQL(
                                id=0,
                                configuration={
                                    "glow_schema_version": 1,
                                    "my_validated_field": "b",
                                },
                            ),
                        )

            crud = MockedRelationalSolutionConfigurationCRUD(
                settings.glow_database_type,
                settings.computed_database_location,
                ExtendedSolutionConfiguration,
            )
            await crud.initialize_database(default_solution_configuration)
            return crud

        # GIVEN: app initializes DB with the correct table and schema, but invalid values
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

    async def test_launch_with_modified_field_default_solution_configuration(
        self,
        settings: Settings,
        default_solution_configuration: ExtendedSolutionConfiguration,
    ):
        """Test that trying to launch the app with a solution configuration that contains a different default
        value with respect to the stored solution configuration ignores the new default value."""

        async def _get_mocked_solution_configuration_crud(settings: SettingsDep):
            class MockedRelationalSolutionConfigurationCRUD(
                RelationalSolutionConfigurationCRUD[ExtendedSolutionConfiguration],
            ):
                async def initialize_database(
                    self,
                    default_solution_configuration: ExtendedSolutionConfiguration,
                ) -> None:
                    engine = create_async_engine(self._database_url, echo=True)
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)

                    async with self._get_session() as session:
                        session.add(
                            SolutionConfigurationSQL(
                                id=0,
                                configuration={
                                    "my_field": 1,
                                },
                            ),
                        )

            crud = MockedRelationalSolutionConfigurationCRUD(
                settings.glow_database_type,
                settings.computed_database_location,
                ExtendedSolutionConfiguration,
            )
            await crud.initialize_database(default_solution_configuration)
            return crud

        # GIVEN: app initializes DB with the correct table and schema, but a modified default
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
            # THEN: returns 200 and the default value of the current solution configuration is ignored
            assert response.status_code == status.HTTP_200_OK
            assert (
                ExtendedSolutionConfiguration.model_validate(
                    response.json(),
                ).my_field
                != ExtendedSolutionConfiguration().my_field
            )

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
            # THEN: returns 200 and the default value of the current solution configuration is ignored
            assert response.status_code == status.HTTP_200_OK
            assert (
                ExtendedSolutionConfiguration.model_validate(
                    response.json(),
                ).my_field
                != ExtendedSolutionConfiguration().my_field
            )

    async def test_launch_with_incompatible_schema_solution_configuration_with_overwrite_env_var(
        self,
        settings: Settings,
        default_solution_configuration: ExtendedSolutionConfiguration,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """Test that trying to launch the app with an incompatible solution configuration due to a type validation
        error raises a validation error unless overwriting is activated."""

        async def _get_mocked_solution_configuration_crud(settings: SettingsDep):
            class MockedRelationalSolutionConfigurationCRUD(
                RelationalSolutionConfigurationCRUD[ExtendedSolutionConfiguration],
            ):
                async def initialize_database(
                    self,
                    default_solution_configuration: ExtendedSolutionConfiguration,
                ) -> None:
                    engine = create_async_engine(self._database_url, echo=True)
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)

                    async with self._get_session() as session:
                        session.add(
                            SolutionConfigurationSQL(
                                id=0,
                                configuration={
                                    "my_field": "hello",
                                },
                            ),
                        )

            crud = MockedRelationalSolutionConfigurationCRUD(
                settings.glow_database_type,
                settings.computed_database_location,
                ExtendedSolutionConfiguration,
            )
            await crud.initialize_database(default_solution_configuration)
            return crud

        # GIVEN: app initializes DB with an incompatible solution configuration
        app = build_mock_app(settings, solution)
        app.dependency_overrides[get_solution_configuration_crud] = _get_mocked_solution_configuration_crud
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client_2,
        ):
            # WHEN: trying to get the solution configuration
            response = await async_client_2.get("/solution-configuration")
            # THEN: the stored solution configuration is preserved and a validation error is raised
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        monkeypatch.setenv(GLOW_OVERWRITE_SOLUTION_CONFIG, "1")

        # WHEN: re-launching the app with the same DB, the proper initialization, and the overwrite env var activated
        app = build_mock_app(settings, solution)
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client_2,
        ):
            # WHEN: trying to get the solution configuration
            response = await async_client_2.get("/solution-configuration")
            # THEN: the incompatible solution configuration replaces the stored one
            assert response.status_code == status.HTTP_200_OK
            assert ExtendedSolutionConfiguration.model_validate(
                response.json(),
            ) == ExtendedSolutionConfiguration(my_field=0)

    async def test_launch_with_incompatible_schema_solution_configuration_and_put_new_config_fails(
        self,
        settings: Settings,
        default_solution_configuration: ExtendedSolutionConfiguration,
    ):
        """Test that trying to launch the app with an incompatible solution configuration due to a type validation
        error raises a validation error, and that trying to change the stored solution configuration with a PUT request
        also raises a validation error."""

        async def _get_mocked_solution_configuration_crud(settings: SettingsDep):
            class MockedRelationalSolutionConfigurationCRUD(
                RelationalSolutionConfigurationCRUD[ExtendedSolutionConfiguration],
            ):
                async def initialize_database(
                    self,
                    default_solution_configuration: ExtendedSolutionConfiguration,
                ) -> None:
                    engine = create_async_engine(self._database_url, echo=True)
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)

                    async with self._get_session() as session:
                        session.add(
                            SolutionConfigurationSQL(
                                id=0,
                                configuration={
                                    "my_field": "hello",
                                },
                            ),
                        )

            crud = MockedRelationalSolutionConfigurationCRUD(
                settings.glow_database_type,
                settings.computed_database_location,
                ExtendedSolutionConfiguration,
            )
            await crud.initialize_database(default_solution_configuration)
            return crud

        # GIVEN: app initializes DB with an incompatible solution configuration
        app = build_mock_app(settings, solution)
        app.dependency_overrides[get_solution_configuration_crud] = _get_mocked_solution_configuration_crud
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client_2,
        ):
            # WHEN: trying to get the solution configuration
            response = await async_client_2.get("/solution-configuration")
            # THEN: the stored solution configuration is preserved and a validation error is raised
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        # WHEN: re-launching the app with the same DB and the proper initialization
        app = build_mock_app(settings, solution)
        async with (
            LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
            ) as async_client_2,
        ):
            # WHEN: trying to get the solution configuration
            response = await async_client_2.get("/solution-configuration")
            # THEN: the stored solution configuration is preserved and a validation error is raised
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            # WHEN: sending a PUT request
            response = await async_client_2.put("/solution-configuration", json={"my_field": 0})
            # THEN: it is not possible to replace the stored solution configuration because it
            # raises a validation error. This happens when the PUT endpoint calls ``initialize_database``,
            # which runs a model validation.
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
