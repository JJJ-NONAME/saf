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

from collections.abc import AsyncGenerator, Callable, Generator, Iterator
import json
import os
from pathlib import Path
from types import ModuleType
from typing import Any, TypeVar, cast
import zipfile

from asgi_lifespan import LifespanManager
from fastapi.testclient import TestClient
from httpx2 import ASGITransport, AsyncClient, Response
import pytest
from pytest_mock.plugin import MockerFixture
from tenacity import TryAgain, retry, stop_after_delay, wait_fixed

from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._core.method_status import MethodStatus
from ansys.saf.glow._core.solution import Solution
from ansys.saf.glow._server.dependencies import (
    get_graphql_client,
    get_http_client,
    get_settings,
    get_solution_service,
)
from ansys.saf.glow._server.hidden_project_directories import product_instance_state_dir_name
from ansys.saf.glow._server.solution import SolutionService
from tests.unit.conftest import MOCK_APP_STARTUP_TIMEOUT, build_mock_app
from tests.unit.routes.gql_mock_client import TestClientGqlMock

F = TypeVar("F")
YieldAsyncFixture = AsyncGenerator[F, None]
T = TypeVar("T", bound=Solution)


class ProjectFixture:
    def __init__(
        self,
        client: TestClient,
        create_project: Callable[[str], Response],
        projects_path: Path,
        project_display_name: str = "project",
    ):
        self._client = client
        self._project_display_name = project_display_name
        self._project = create_project(project_display_name)
        self._project_files_path = projects_path

    @property
    def properties(self) -> Any:
        return self._project.json()

    @property
    def client(self) -> TestClient:
        return self._client

    @property
    def project_display_name(self) -> str:
        return self._project_display_name

    @property
    def project_name(self) -> str:
        return self.properties["name"]

    @property
    def project_id(self) -> str:
        return self.project_name[len("projects/") :]

    @property
    def project_files_path(self) -> Path:
        return self._project_files_path

    @property
    def project_files_dir(self) -> Path:
        return self._project_files_path / self.project_id

    def project_files(self) -> list[str]:
        return [str(i.relative_to(self._project_files_path)) for i in self.project_files_dir.rglob("*") if i.is_file()]


@pytest.fixture(autouse=True)
def clean_env():
    # All route tests instantiate clients and settings that affect the environment. Clean it up afterwards.
    yield
    for env_var in os.environ:
        if env_var.startswith("GLOW_"):
            del os.environ[env_var]


@pytest.fixture(autouse=True)
def patch_http_client(mocker: MockerFixture, method_client_module: TestClient):
    """TestClient is using a special server (http://testserver) which needs to be used wherever httpx is used."""
    mocked_http_client = mocker.patch("ansys.saf.glow._hps_auth.hps_authenticator.httpx2.Client")
    mocked_http_client.return_value.__enter__.return_value = method_client_module


@pytest.fixture
def projects_path(settings: Settings) -> Path:
    projects_dir = settings.computed_project_files_directory
    projects_dir.mkdir(parents=True, exist_ok=True)
    return projects_dir


@pytest.fixture
def project_fixture(
    client: TestClient,
    create_project: Callable[[str], Response],
    projects_path: Path,
) -> ProjectFixture:
    return ProjectFixture(client, create_project, projects_path)


@pytest.fixture
def create_project(client: TestClient) -> Callable[[str, str], Response]:
    def _create_project(display_name: str = "project", description: str = "") -> Response:
        create_project_request = {"display_name": display_name}
        if description:
            create_project_request["description"] = description
        response = client.post("/projects", json=create_project_request)
        return response

    return _create_project


@pytest.fixture(scope="module")
def client_module(mock_module_settings: Settings) -> Iterator[TestClient]:  # type: ignore
    # The test must define a solution variable that holds the solution type.
    # With statement needed to fire up the app startup event.
    with TestClient(build_mock_app(mock_module_settings)) as client:
        yield client


@pytest.fixture
def method_client_module(mock_module_settings: Settings) -> Iterator[TestClient]:  # type: ignore
    """TestClient mocking httpx within transaction methods.

    TestClient is using a special server (http://testserver) that is invalid for the httpx client in MethodRunner.
    Therefore we need to mock httpx2.Client with a TestClient, but we cannot use the same TestClient as the one used
    in tests. Indeed the test is making a request to the server which is itself also making a request to the server
    to change the state of the method, creating deadlock...
    """

    with TestClient(build_mock_app(mock_module_settings)) as client:
        client.headers = {"shared-volume": "true"}
        yield client


@pytest.fixture
def client(
    client_module: TestClient,
    method_client_module: TestClient,
    settings: Settings,
):
    method_client_module.app.dependency_overrides[get_settings] = lambda: settings  # type: ignore
    client_module.app.dependency_overrides[get_http_client] = lambda: method_client_module  # type: ignore
    client_module.app.dependency_overrides[get_settings] = lambda: settings  # type: ignore
    client_module.app.dependency_overrides[get_graphql_client] = lambda: TestClientGqlMock(  # type: ignore
        client=method_client_module,
    )
    return client_module


@pytest.fixture
async def async_client(
    request: pytest.FixtureRequest,
    method_client_module: TestClient,
    settings: Settings,
) -> YieldAsyncFixture[AsyncClient]:
    method_client_module.app.dependency_overrides[get_settings] = lambda: settings  # type: ignore
    app = build_mock_app(settings, request.module.solution)  # type: ignore
    app.dependency_overrides[get_http_client] = lambda: method_client_module
    async with (
        LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
        AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://test",
        ) as client,
    ):
        yield client


def build_client(
    definition_module: ModuleType,
    method_client_module: TestClient,
    settings: Settings,
) -> Iterator[TestClient]:
    with TestClient(build_mock_app(settings, definition_module)) as client:
        client.app.dependency_overrides[get_http_client] = lambda: method_client_module  # type: ignore
        client.app.dependency_overrides[get_graphql_client] = lambda: TestClientGqlMock(  # type: ignore
            client=method_client_module,
        )
        yield client


@pytest.fixture
def client_func(
    request: pytest.FixtureRequest,
    method_client_module: TestClient,
    settings: Settings,
) -> Iterator[TestClient]:
    yield from build_client(request.param, method_client_module, settings)


@pytest.fixture
def client_func_and_extra(
    request: pytest.FixtureRequest,
    method_client_module: TestClient,
    settings: Settings,
) -> Iterator[tuple[TestClient, Any]]:
    definition_module, extra = request.param
    for client in build_client(definition_module, method_client_module, settings):
        yield (client, extra)


@pytest.fixture
def get_client_func(
    method_client_module: TestClient,
    settings: Settings,
) -> Callable[[ModuleType], TestClient]:
    def _client_func(solution_module_str: ModuleType) -> TestClient:
        with TestClient(build_mock_app(settings, solution_module_str)) as client:
            client.app.dependency_overrides[get_http_client] = lambda: method_client_module  # type: ignore
            client.app.dependency_overrides[get_graphql_client] = lambda: TestClientGqlMock(  # type: ignore
                client=method_client_module,
            )
            return client

    return _client_func


@pytest.fixture(scope="module")
def module_client_for_app_built_with_modified_solution(
    request: pytest.FixtureRequest,
    mock_module_settings: Settings,
) -> Iterator[TestClient]:
    # the test must define two solution variables that hold the solution types.
    modified_solution_module = cast("ModuleType", request.module.modified_solution)  # type: ignore
    original_solution_module = cast("ModuleType", request.module.solution)  # type: ignore

    # build the app around the modified solution
    app = build_mock_app(mock_module_settings, modified_solution_module)

    # get the name of the old solution
    solution_name = SolutionService(original_solution_module).name

    # override the modified solution service name to be the same as the original solution
    # so that the modified solution server refers to the same database as the original solution
    class MockSolutionService(SolutionService):
        @property
        def name(self) -> str:
            return solution_name

    def build_mock_solution_service() -> SolutionService:
        service = MockSolutionService(modified_solution_module)
        service.build_and_validate()
        return service

    app.dependency_overrides[get_solution_service] = build_mock_solution_service

    with TestClient(app) as client:
        yield client


@pytest.fixture
def client_for_app_built_with_modified_solution(
    module_client_for_app_built_with_modified_solution: TestClient,
    settings: Settings,
) -> TestClient:
    module_client_for_app_built_with_modified_solution.app.dependency_overrides[get_settings] = lambda: settings  # type: ignore
    return module_client_for_app_built_with_modified_solution


@pytest.fixture
def incompatible_minimal_project(safx_path: Path, tmp_path: Path) -> Path:
    """Return a .safx project file that is not compatible with the minimal solution"""
    target = tmp_path / "archive"
    assert not target.exists()
    with zipfile.ZipFile(safx_path) as archive:
        archive.extractall(target)

    sap_file = [file_path for file_path in target.iterdir() if file_path.suffix == ".sap"][0]
    project_schema = json.loads(sap_file.read_bytes())
    project_schema["solution"]["steps"]["minimal_step"]["name"] = 100

    incompatible_safx_path = tmp_path / "incompatible_import.safx"
    with zipfile.ZipFile(incompatible_safx_path, "w") as archive:
        archive.writestr(sap_file.name, json.dumps(project_schema))

    return incompatible_safx_path


@pytest.fixture
def compatible_minimal_project(safx_path: Path, tmp_path: Path) -> Path:
    """Return a .safx project file that is compatible with the minimal solution"""
    target = tmp_path / "archive"
    assert not target.exists()
    with zipfile.ZipFile(safx_path) as archive:
        archive.extractall(target)

    sap_file = [file_path for file_path in target.iterdir() if file_path.suffix == ".sap"][0]
    project_schema = json.loads(sap_file.read_bytes())
    del project_schema["solution"]["steps"]["minimal_step"]["x"]

    compatible_safx_path = tmp_path / "compatible_import.safx"
    with zipfile.ZipFile(compatible_safx_path, "w") as archive:
        archive.writestr(sap_file.name, json.dumps(project_schema))

    return compatible_safx_path


@pytest.fixture
def get_instance_payload() -> Callable[[ProjectFixture], tuple[str, dict[str, Any]]]:
    def _instance_payload(project_fixture: ProjectFixture):  # type: ignore
        instance_url = f"{project_fixture.properties['name']}/steps/instance-step/instances/x-y"
        payload = {  # type: ignore
            "name": instance_url,
            "pim_name": "instances/XYZ",
            "service_name": "serv",
            "product_version": "1",
            "max_execution_time": "9999",
            "recovery_state_info": {
                "product_instance_state_dirname": "is_mvv5y8ai",
                "project_filename": "project.txt",
                "product_dict_handles": {},
                "product_sub_model": {
                    "sub_handle": {
                        "encoding": None,
                        "entity_id": "00000000-0000-0000-0000-000000000000",
                        "is_blob": True,
                        "mime_type": None,
                        "opaque_identifier": "",
                        "original_name": "",
                        "size": None,
                    },
                },
                "random_value": "string",
                "product_list_handles": [],
            },
        }
        return instance_url, payload  # type: ignore

    return _instance_payload


@pytest.fixture
def project_files() -> list[str]:
    return [
        "myfile.txt",
        "something_else.txt",
        "path with space.py",
        "directory/image.jpg",
        "directory/test.txt",
        "directory/sub/image.jpg",
        "directory/sub/a_test.txt",
        "directory/sub/nested/test.txt",
        f"{product_instance_state_dir_name}/my_step/my_instance/stuff.txt",
    ]


@pytest.fixture
def project_dir(project_fixture: ProjectFixture, project_files: list[str]) -> Path:
    project_dir = project_fixture.project_files_dir
    project_dir.mkdir(exist_ok=True, parents=True)
    for project_file in project_files:
        (project_dir / project_file).parent.mkdir(exist_ok=True, parents=True)
        (project_dir / project_file).touch(exist_ok=True)
    my_file = project_dir / "myfile.txt"
    my_file.write_bytes(b"hello world")
    return project_dir


@pytest.fixture
def safx_path(project_fixture: ProjectFixture, tmp_path: Path) -> Generator[Path, None, None]:
    response = project_fixture.client.get(f"{project_fixture.properties['name']}:export")
    response.raise_for_status()
    safx_path = tmp_path / "project.safx"
    safx_path.write_bytes(response.content)
    yield safx_path
    safx_path.unlink()


def upgrade_or_import_project(
    source: str,
    client_func: TestClient,
    project_name: str,
    safx_path: Path,
    expected_status_code: int = 200,
    expected_error_message: str = "",
) -> dict[str, Any] | None:
    if source == "db":
        response = client_func.post(f"/{project_name}:upgrade")
    else:
        with safx_path.open("rb") as f:
            response = client_func.post(
                "/projects:import",
                files={"safx_file": f},
                data={"display_name": "Unused Display Name"},
            )
    assert response.status_code == expected_status_code
    if response.status_code != 200:
        assert expected_error_message in response.text
    else:
        project_info = response.json()
        return project_info


@retry(stop=stop_after_delay(10), wait=wait_fixed(0.5), reraise=True)
def wait_for_method_completion(client: TestClient, method_url: str) -> None:
    response = client.get(method_url)
    response.raise_for_status()
    if response.json()["status"] in (MethodStatus.Completed, MethodStatus.Failed):
        return
    raise TryAgain
