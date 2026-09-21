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

from collections.abc import Generator
from pathlib import Path
import shutil
import tempfile

from fastapi.testclient import TestClient
import pytest

from ansys.saf.product_configuration.wrappers.optislang import (
    CONNECTION_MODE_LOCAL_DOMAIN,
    CONNECTION_MODE_TCP,
    OptislangInstance,
    app,
    get_global_optislang_instance,
)


class MockOptislangInstance(OptislangInstance):
    """Mock optiSLang instance for API-level integration testing."""

    def __init__(self) -> None:
        super().__init__()
        self.start_call_count = 0
        self.effective_start_count = 0
        self.last_start_call: dict[str, object] | None = None
        self.raise_on_start: type[Exception] | None = None

    def start(
        self,
        project_path: Path,
        project_properties_file: Path,
        input_files: list[Path],
        osl_version: int,
        loglevel: str,
        connection_mode: str,
        log_file_path: Path | None,
    ) -> None:
        self.start_call_count += 1
        self.last_start_call = {
            "project_path": project_path,
            "project_properties_file": project_properties_file,
            "input_files": input_files,
            "osl_version": osl_version,
            "loglevel": loglevel,
            "connection_mode": connection_mode,
            "log_file_path": log_file_path,
        }

        if self.raise_on_start:
            raise self.raise_on_start

        # Keep start idempotent when already running.
        if self._connection_mode is not None:
            return

        self.effective_start_count += 1
        self._osl_working_directory = tempfile.mkdtemp()
        self._connection_mode = connection_mode

        self.osl_log_path = log_file_path or Path(self._osl_working_directory) / "optiSLang.log"
        self.osl_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.osl_log_path.write_text(f"mock logs for {connection_mode}")

        if connection_mode == CONNECTION_MODE_TCP:
            self._osl_host = "0.0.0.0"
            self._osl_port = 5678
            self._local_server_id = None
        else:
            self._local_server_id = "localhost:12345#0"
            self._osl_host = None
            self._osl_port = None

    def close_optislang(self) -> None:
        self._connection_mode = None
        self._local_server_id = None
        self._osl_port = None
        self._osl_host = None

    def shutdown(self) -> None:
        self.close_optislang()
        if self._osl_working_directory:
            shutil.rmtree(self._osl_working_directory, ignore_errors=True)
        self._osl_working_directory = None


@pytest.fixture(autouse=True)
def mocked_app() -> Generator[TestClient, None, None]:
    mock_instance = MockOptislangInstance()

    def get_mock_instance() -> MockOptislangInstance:
        return mock_instance

    app.dependency_overrides[get_global_optislang_instance] = get_mock_instance

    yield TestClient(app)

    app.dependency_overrides.clear()


def get_mock_instance_from_override() -> MockOptislangInstance:
    instance_provider = app.dependency_overrides[get_global_optislang_instance]
    instance = instance_provider()
    assert isinstance(instance, MockOptislangInstance)
    return instance


def test_local_domain_workflow(tmp_path: Path, mocked_app: TestClient):
    request_body: dict[str, str | int | list[str]] = {
        "project_path": str(tmp_path / "project.opf"),
        "project_properties_file": str(tmp_path / "props.json"),
        "osl_version": 251,
        "input_files": [],
        "loglevel": "INFO",
    }
    response = mocked_app.post("/start", json=request_body)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType]
    body = response.json()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert body["connection_mode"] == CONNECTION_MODE_LOCAL_DOMAIN
    assert body["local_server_id"] == "localhost:12345#0"

    response = mocked_app.get("/connection")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType]
    assert response.json() == body  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    mocked_app.post("/close-optislang").raise_for_status()  # pyright: ignore[reportUnknownMemberType]

    response = mocked_app.get("/connection")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 500  # pyright: ignore[reportUnknownMemberType]


def test_tcp_mode_workflow(tmp_path: Path, mocked_app: TestClient):
    request_body: dict[str, str | int | list[str]] = {
        "project_path": str(tmp_path / "project.opf"),
        "project_properties_file": str(tmp_path / "props.json"),
        "osl_version": 251,
        "input_files": [],
        "loglevel": "INFO",
        "connection_mode": CONNECTION_MODE_TCP,
    }
    response = mocked_app.post("/start", json=request_body)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType]
    body = response.json()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert body["connection_mode"] == CONNECTION_MODE_TCP
    assert body["host"] == "0.0.0.0"
    assert isinstance(body["port"], int)

    response = mocked_app.get("/connection")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType]
    assert response.json() == body  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    mocked_app.post("/shutdown").raise_for_status()  # pyright: ignore[reportUnknownMemberType]

    response = mocked_app.get("/connection")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 500  # pyright: ignore[reportUnknownMemberType]


def test_starting_twice_reuses_running_instance(tmp_path: Path, mocked_app: TestClient):
    request_local: dict[str, str | int | list[str]] = {
        "project_path": str(tmp_path / "project.opf"),
        "project_properties_file": str(tmp_path / "props.json"),
        "osl_version": 251,
        "input_files": [],
        "loglevel": "INFO",
    }
    first_start = mocked_app.post("/start", json=request_local)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    first_start.raise_for_status()  # pyright: ignore[reportUnknownMemberType]
    first_body = first_start.json()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert first_body["connection_mode"] == CONNECTION_MODE_LOCAL_DOMAIN

    request_tcp = {**request_local, "connection_mode": CONNECTION_MODE_TCP}
    second_start = mocked_app.post("/start", json=request_tcp)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    assert second_start.status_code == 200  # pyright: ignore[reportUnknownMemberType]
    assert second_start.json() == first_body  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    instance = get_mock_instance_from_override()
    assert instance.start_call_count == 2
    assert instance.effective_start_count == 1


def test_close_twice_is_safe(tmp_path: Path, mocked_app: TestClient):
    request_body: dict[str, str | int | list[str]] = {
        "project_path": str(tmp_path / "project.opf"),
        "project_properties_file": str(tmp_path / "props.json"),
        "osl_version": 251,
        "input_files": [],
        "loglevel": "INFO",
    }
    mocked_app.post("/start", json=request_body).raise_for_status()  # pyright: ignore[reportUnknownMemberType]

    mocked_app.post("/close-optislang").raise_for_status()  # pyright: ignore[reportUnknownMemberType]
    mocked_app.post("/close-optislang").raise_for_status()  # pyright: ignore[reportUnknownMemberType]

    response = mocked_app.get("/connection")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 500  # pyright: ignore[reportUnknownMemberType]


def test_shutdown_twice_is_safe(tmp_path: Path, mocked_app: TestClient):
    request_body: dict[str, str | int | list[str]] = {
        "project_path": str(tmp_path / "project.opf"),
        "project_properties_file": str(tmp_path / "props.json"),
        "osl_version": 251,
        "input_files": [],
        "loglevel": "INFO",
    }
    mocked_app.post("/start", json=request_body).raise_for_status()  # pyright: ignore[reportUnknownMemberType]

    mocked_app.post("/shutdown").raise_for_status()  # pyright: ignore[reportUnknownMemberType]
    mocked_app.post("/shutdown").raise_for_status()  # pyright: ignore[reportUnknownMemberType]

    response = mocked_app.get("/connection")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 500  # pyright: ignore[reportUnknownMemberType]


def test_logs_after_start(tmp_path: Path, mocked_app: TestClient):
    request_body: dict[str, str | int | list[str]] = {
        "project_path": str(tmp_path / "project.opf"),
        "project_properties_file": str(tmp_path / "props.json"),
        "osl_version": 251,
        "input_files": [],
        "loglevel": "INFO",
    }
    mocked_app.post("/start", json=request_body).raise_for_status()  # pyright: ignore[reportUnknownMemberType]

    response = mocked_app.get("/logs")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType]
    assert response.text == "mock logs for LOCAL_DOMAIN"  # pyright: ignore[reportUnknownMemberType]
