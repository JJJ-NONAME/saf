# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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

from collections.abc import Callable
import platform
import random
import subprocess

from pydantic import PostgresDsn
import pytest

from ansys.saf.testing._common.common import YieldFixture
from ansys.saf.testing._database.psql_container_manager import PostgresqlContainer, PostgresqlServerInfo


@pytest.fixture(scope="session")
def postgresql_server(
    request: pytest.FixtureRequest,
    tmp_path_factory: pytest.TempPathFactory,
    worker_id: str,
    # start of custom fixtures
    is_docker_enabled: bool,
) -> YieldFixture[PostgresqlServerInfo | None]:
    # Don't skip or fail tests here. This fixture is used in other fixtures that are parametrized and not all
    # options end up using this fixture. For example: fixture used for sqlite and postgresql. If we skip here
    # because docker is not enabled, it will also skip sqlite tests.
    if not is_docker_enabled:
        yield
    else:
        session_unique_id = str(getattr(request.config, "session_unique_id", ""))  # type: ignore
        if not session_unique_id:
            raise RuntimeError("session_unique_id is required to generate unique docker container names.")
        tmp_dir = tmp_path_factory.mktemp(basename=f"saf-testing-psql-{session_unique_id}-{worker_id}")
        with PostgresqlContainer(tmp_dir) as psql_info:
            yield psql_info


def create_postgres_database_url(postgresql_url: PostgresDsn, db_name: str) -> PostgresDsn:
    psql_attr = postgresql_url.hosts()[0]
    return PostgresDsn.build(
        scheme="postgresql",
        username=psql_attr["username"],
        password=psql_attr["password"],
        host=psql_attr["host"],
        port=psql_attr["port"],
        path=db_name,
    )


def create_postgres_database(postgresql_server: PostgresqlServerInfo):
    db_name = f"saf_testing_{str(random.randint(0, 100000)).zfill(6)}"
    subprocess.run(
        [
            "docker",
            "exec",
            postgresql_server.container_name,
            "psql",
            "-U",
            "saf-testing",
            "-p",
            "5432",  # internal port within postgresql container
            "-c",
            f"CREATE DATABASE {db_name};",
        ],
        capture_output=True,
        check=True,
    )

    return PostgresqlServerInfo(
        create_postgres_database_url(postgresql_server.url, db_name),
        postgresql_server.container_name,
    )


@pytest.fixture
def get_temp_postgresql_database(
    is_docker_installed: bool,
    is_docker_requested: bool,
    postgresql_server: PostgresqlServerInfo | None,
) -> Callable[[], PostgresqlServerInfo]:
    # this method does not clean up the database that it creates
    # instead it assumes that the postgresql container containing
    # the database will be destroyed at the end of the test
    # in which case the database will be destroyed as well

    def _get_temp_postgresql_database() -> PostgresqlServerInfo:
        if not is_docker_requested:
            pytest.skip("Use --docker to enable PostgreSQL test.")
        if platform.system() != "Linux":
            pytest.skip("PostgreSQL test only available on Linux.")
        if not is_docker_installed:
            pytest.fail("Install docker to enable PostgreSQL test.")
        if not postgresql_server:
            pytest.fail("PostgreSQL server not available. Make sure your docker daemon is running.")

        return create_postgres_database(postgresql_server)

    return _get_temp_postgresql_database


@pytest.fixture(scope="module")
def get_temp_postgresql_database_module(
    is_docker_installed: bool,
    is_docker_requested: bool,
    postgresql_server: PostgresqlServerInfo | None,
) -> Callable[[], PostgresqlServerInfo]:
    # this method does not clean up the database that it creates
    # instead it assumes that the postgresql container containing
    # the database will be destroyed at the end of the test
    # in which case the database will be destroyed as well

    def _get_temp_postgresql_database() -> PostgresqlServerInfo:
        if not is_docker_requested:
            pytest.skip("Use --docker to enable PostgreSQL test.")
        if platform.system() != "Linux":
            pytest.skip("PostgreSQL test only available on Linux.")
        if not is_docker_installed:
            pytest.fail("Install docker to enable PostgreSQL test.")
        if not postgresql_server:
            pytest.fail("PostgreSQL server not available. Make sure your docker daemon is running.")

        return create_postgres_database(postgresql_server)

    return _get_temp_postgresql_database
