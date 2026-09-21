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

from collections.abc import Callable, Generator, Iterator
import contextlib
import contextvars
import importlib
import inspect
import json
import logging
from pathlib import Path
import random
from typing import Any, TypeVar

from anyio.abc import BlockingPortal
from anyio.from_thread import start_blocking_portal
from fastapi.testclient import TestClient
from httpx2 import Response
import pytest
import pytest_mock
from starlette.types import ASGIApp

from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._core.client_exceptions import raise_for_graphql_status
from ansys.saf.glow._server.dependencies import get_graphql_client, get_http_client, get_settings
from ansys.saf.glow._server.server import create_app
from ansys.saf.glow.client import Client, callback
from ansys.saf.glow.solution import ProductInstanceManager, Solution

T = TypeVar("T", bound=Solution)

is_within_dash_callback_context = contextvars.ContextVar("dash_callback_context", default=False)
original_callback_call = callback.__call__


class NotVersionArgFoundError(Exception): ...


class NotServiceNameAttrFoundError(Exception): ...


def patched_call(*args: Any, **kwargs: Any) -> Callable[..., Any]:
    decorated = original_callback_call(*args, **kwargs)

    def context_wrapper(*args: Any, **kwargs: Any) -> Any:
        token = is_within_dash_callback_context.set(True)
        try:
            return decorated(*args, **kwargs)
        finally:
            is_within_dash_callback_context.reset(token)

    return context_wrapper


callback.__call__ = patched_call


class GraphQLClientMock:
    """Testing GraphQl with FastAPI's TestClient setup
    does not work. Instead, the /graphql endpoint is called
    directly, as it is done on Ariadne's tests
    (e.g. https://github.com/mirumee/ariadne/blob/main/tests/asgi/test_query_execution.py).
    """

    def __init__(self, client: TestClient):
        self._client = client

    def _execute(
        self,
        request_string: str,
        variable_values: dict[str, Any],
        access_token: str | None = None,
    ) -> Response:
        headers: dict[str, str] = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        response = self._client.post(
            "/graphql",
            json={"query": request_string, "variables": variable_values},
            headers=headers,
        )
        return response

    def run_query(
        self,
        request_string: str,
        payload: dict[str, Any],
        access_token: str | None = None,
    ) -> None:
        variable_values = {name: json.dumps(value) for name, value in payload.items()}
        result = self._execute(request_string, access_token=access_token, variable_values=variable_values)
        method = list(result.json()["data"].keys())[0]
        raise_for_graphql_status(result.json()["data"][method])


@pytest.fixture(scope="module")
def configure_solution(request: pytest.FixtureRequest) -> dict[str, str]:
    # everything is configured through environment variables, as done in a real solution deployment. In this way, we
    # also avoid having to patch Settings everywhere and mock calls to os.getenv and similar.
    mpatch = pytest.MonkeyPatch()
    env_vars = getattr(request, "param", {})
    for env_var_name, env_var_value in env_vars.items():
        mpatch.setenv(env_var_name, env_var_value)
    # This finalizer is executed after the last test within the requesting test context, so it automatically adapts
    # to if this fixture was parametrized in a test, class or module. The change caused by undo() will trigger again
    # the nested fixtures such as solutions_settings, _solution_api_client and _glow_client.
    request.addfinalizer(lambda: mpatch.undo())  # noqa: PT021
    return env_vars


@pytest.fixture(scope="module")
def _temporary_app_data(tmp_path_factory: pytest.TempPathFactory) -> Path:  # pyright: ignore[reportUnusedFunction]
    tmp_appdata_path_obj = tmp_path_factory.getbasetemp()
    appdata = tmp_appdata_path_obj / "appdata"
    appdata.mkdir(exist_ok=True, parents=True)
    return appdata


@pytest.fixture(scope="module")
def _solution_settings(  # pyright: ignore[reportUnusedFunction]
    _temporary_app_data: Path,
    configure_solution: dict[str, str],
) -> Iterator[Settings]:
    mpatch = pytest.MonkeyPatch()
    # Set a temporary APPDATA for solution files and database
    mpatch.setenv("APPDATA", _temporary_app_data.as_posix())
    mpatch.setenv("XDG_DATA_HOME", _temporary_app_data.as_posix())
    # Force to run long-running methods in same process, so they can reach the TestClient.
    mpatch.setenv("GLOW_LONG_RUNNING_EXECUTOR_TYPE", "Thread")
    mpatch.setenv("GLOW_PRODUCT_INSTANCE_SYSTEM", "_MOCK")
    yield Settings.model_validate({})
    mpatch.undo()


@pytest.fixture(scope="module")
def _shared_test_client_portal() -> Iterator[BlockingPortal]:  # pyright: ignore[reportUnusedFunction]
    # A TestClient that is not used as a context manager starts a fresh event loop for every request.
    # GLOW guards SQLite with process-wide asyncio.Locks, which bind to the first event loop that
    # contends them and then reject any other one, so every TestClient must share a single loop, as
    # they do behind a single-worker server.
    mpatch = pytest.MonkeyPatch()
    with start_blocking_portal(backend="asyncio") as portal:

        @contextlib.contextmanager
        def reuse_shared_portal(**_: Any) -> Generator[BlockingPortal]:
            yield portal

        mpatch.setattr("anyio.from_thread.start_blocking_portal", reuse_shared_portal)
        try:
            yield portal
        finally:
            mpatch.undo()


@pytest.fixture(scope="module")
def _api_testclient(  # pyright: ignore[reportUnusedFunction]
    _solution_settings: Settings,
    _shared_test_client_portal: BlockingPortal,
) -> Iterator[TestClient]:
    with TestClient(create_app(_solution_settings)) as client:
        yield client


@pytest.fixture(scope="module")
def _created_method_clients() -> list[TestClient]:  # pyright: ignore[reportUnusedFunction]
    return []


@pytest.fixture(scope="module")
def _method_client_factory(  # pyright: ignore[reportUnusedFunction]
    _solution_settings: Settings,
    _created_method_clients: list[TestClient],
    _shared_test_client_portal: BlockingPortal,
) -> Callable[[], TestClient]:
    def create_method_client() -> TestClient:
        client = TestClient(create_app(_solution_settings))
        _created_method_clients.append(client)
        return client

    return create_method_client


def _validate_product_manager_class(product_manager_class: type[ProductInstanceManager[Any, Any]]) -> None:
    internal_product_manager = product_manager_class._instance_manager_impl_type  # type: ignore

    initialize_signature = inspect.signature(internal_product_manager.initialize)  # type: ignore
    if "version" not in initialize_signature.parameters:
        raise NotVersionArgFoundError("The 'version' argument is required in the product manager's initialize method.")

    service_name = getattr(internal_product_manager, "SERVICE_NAME", None)
    if service_name is None:
        raise NotServiceNameAttrFoundError("The internal product manager must have a SERVICE_NAME attribute.")


@pytest.fixture
def mock_product_instance(mocker: pytest_mock.MockerFixture, request: pytest.FixtureRequest) -> None:
    if not hasattr(request, "param"):
        raise ValueError("The 'mock_product_instance' fixture requires being parametrized.")

    def patched_initialize(self: Any, *args: Any, **kwargs: Any) -> None:
        self.initialize_service(self.SERVICE_NAME, kwargs.get("version"))
        self.recovery_state_info = self.recovery_state_info_type()

    for product_manager_class, product_client_class in request.param.items():
        if isinstance(product_manager_class, str):
            product_manager_module_str, product_manager_class_name = product_manager_class.rsplit(".", 1)
            product_manager_module = importlib.import_module(product_manager_module_str)
            product_manager_class = getattr(product_manager_module, product_manager_class_name)

        _validate_product_manager_class(product_manager_class)

        internal_product_manager = product_manager_class._instance_manager_impl_type
        mocker.patch.object(internal_product_manager, "initialize", patched_initialize)
        mocker.patch.object(
            internal_product_manager,
            "get_client_object_implement",
            return_value=product_client_class(),
        )
        for method_name in (
            "close_client_object_implement",
            "save_state_implement",
            "load_state_implement",
            "shutdown_implement",
        ):
            mocker.patch.object(internal_product_manager, method_name)


def _apply_dependency_overrides(
    app: ASGIApp,
    _solution_settings: Settings,
    _method_client_factory: Callable[[], TestClient],
    graphql_client: TestClient | None = None,
) -> None:
    method_client = _method_client_factory()
    method_client.app.dependency_overrides[get_settings] = lambda: _solution_settings  # type: ignore
    app.dependency_overrides[get_settings] = lambda: _solution_settings  # type: ignore
    app.dependency_overrides[get_http_client] = lambda: method_client  # type: ignore
    graphql_client = graphql_client or method_client
    app.dependency_overrides[get_graphql_client] = lambda: GraphQLClientMock(  # type: ignore
        client=graphql_client,
    )


@pytest.fixture(scope="module")
def _solution_api_client(  # pyright: ignore[reportUnusedFunction]
    _solution_settings: Settings,
    _api_testclient: TestClient,
    _method_client_factory: Callable[[], TestClient],
) -> TestClient:
    method_client = _method_client_factory()
    _apply_dependency_overrides(
        app=_api_testclient.app,
        _solution_settings=_solution_settings,
        _method_client_factory=_method_client_factory,
        graphql_client=method_client,
    )
    return _api_testclient


@pytest.fixture(scope="module")
def _created_dash_callback_clients() -> list[TestClient]:  # pyright: ignore[reportUnusedFunction]
    return []


@pytest.fixture(scope="module")
def _dash_callback_client_factory(  # pyright: ignore[reportUnusedFunction]
    _solution_settings: Settings,
    _method_client_factory: Callable[[], TestClient],
    _created_dash_callback_clients: list[TestClient],
    _shared_test_client_portal: BlockingPortal,
) -> Callable[[], TestClient]:
    def create_callback_client() -> TestClient:
        client = TestClient(create_app(_solution_settings))
        _created_dash_callback_clients.append(client)
        _apply_dependency_overrides(
            app=client.app,
            _solution_settings=_solution_settings,
            _method_client_factory=_method_client_factory,
            graphql_client=client,
        )
        return client

    return create_callback_client


@pytest.fixture
def dash_http_client(
    _solution_settings: Settings,
    _method_client_factory: Callable[[], TestClient],
    _shared_test_client_portal: BlockingPortal,
) -> Iterator[TestClient]:
    with TestClient(create_app(_solution_settings)) as client:
        _apply_dependency_overrides(
            app=client.app,
            _solution_settings=_solution_settings,
            _method_client_factory=_method_client_factory,
        )
        yield client


@pytest.fixture(scope="module")
def _mock_glow_client_internal_clients(  # pyright: ignore[reportUnusedFunction]
    _solution_api_client: TestClient,
    _dash_callback_client_factory: Callable[[], TestClient],
    module_mocker: pytest_mock.MockerFixture,
) -> None:
    # Any GLOW Client created from now on will have the right internal clients.
    original_client_init = Client.__init__  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

    def patched_client_init(self: Any, *args: Any, **kwargs: Any) -> None:
        original_client_init(self, *args, **kwargs)

        # We need to patch the clients here since patching a GLOW Client within a test
        # affects all Client instances in different contexts. In here we know in which
        # context is the Client being initialized, so we can use the right TestClient.
        is_from_dash_callback = is_within_dash_callback_context.get()

        client = None
        client = _dash_callback_client_factory() if is_from_dash_callback else _solution_api_client

        object.__setattr__(self, "_http_client", client)
        object.__setattr__(self, "_graphql_client", GraphQLClientMock(client=client))

    module_mocker.patch.object(Client, "__init__", patched_client_init)


@pytest.fixture(scope="module")
def init_dashclient(
    _solution_settings: Settings,
    _mock_glow_client_internal_clients: None,
    module_mocker: pytest_mock.MockerFixture,
):
    mpatch = pytest.MonkeyPatch()
    mpatch.setenv("GLOW_SOLUTION_DEFINITION", _solution_settings.glow_solution_definition)
    mpatch.setenv("GLOW_API_URL", "http://testserver")
    mpatch.setenv("GLOW_EXTERNAL_API_URL", "http://testserver")
    mpatch.setenv("GLOW_WS_EVENTS_ADDR", "ws://testserver")
    module_mocker.patch("ansys.saf.glow._client.dashclient.DashClient._auth_header_from_ctx", return_value=None)
    yield
    mpatch.undo()


@pytest.fixture(scope="module")
def _glow_client(  # pyright: ignore[reportUnusedFunction]
    _solution_settings: Settings,
    _solution_api_client: TestClient,
    _mock_glow_client_internal_clients: None,
) -> Iterator[Client[Solution]]:
    with Client[_solution_settings.computed_solution_type](
        _solution_settings.computed_solution_type,
        str(_solution_api_client.base_url),
    ) as _glow_client:
        yield _glow_client


@pytest.fixture
def project_display_name() -> str:
    return f"My Project {random.randint(0, 10000)}"  # noqa: S311


@pytest.fixture
def client_project(_glow_client: Client[T], project_display_name: str) -> Iterator[T]:
    project = _glow_client.create_project(project_display_name)
    yield project
    project.delete()


@pytest.fixture
def project_id(client_project: Solution) -> str:
    return client_project.url.split("/projects/")[1]


@pytest.fixture
def project_name(project_id: str) -> str:
    return f"projects/{project_id}"


@pytest.fixture
def project_files_dir(_solution_settings: Settings, project_id: str) -> Path:
    return _solution_settings.computed_project_files_directory / project_id


@pytest.fixture
def solution_logs(tmp_path: Path, request: pytest.FixtureRequest) -> Iterator[Path]:
    logging_level = str(getattr(request, "param", "DEBUG")).upper()

    temp_log_path = tmp_path / "solution.log"

    # To capture logs from solutions, which can be be in any namespace
    root_logger = logging.getLogger()
    # To capture logs from GLOW. By default, it configures two different loggers and logs from ansys
    # are not propagated to root logger.
    ansys_logger = logging.getLogger("ansys")
    root_logger.setLevel(logging_level)
    ansys_logger.setLevel(logging_level)
    file_handler = logging.FileHandler(temp_log_path)
    file_handler.setLevel(logging_level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    ansys_logger.addHandler(file_handler)

    yield temp_log_path

    root_logger.removeHandler(file_handler)
    ansys_logger.removeHandler(file_handler)


@pytest.fixture
def is_msg_in_logs(solution_logs: Path) -> Callable[[str], bool]:
    def _msg_in_logs(msg: str) -> bool:
        return msg in solution_logs.read_text()

    return _msg_in_logs
