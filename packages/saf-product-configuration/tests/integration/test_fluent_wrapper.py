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

from pathlib import Path
import platform
import random
import sys

from fastapi.testclient import TestClient
import pytest

from ansys.saf.product_configuration.wrappers.fluent import (
    FluentInstance,
    TransportMode,
    app,
    get_global_fluent_instance,
)


class MockProcess:
    def __init__(self, pid: int):
        self.pid = pid


class MockFluentInstance(FluentInstance):
    def _find_fluent_bin(self) -> str:
        return sys.executable

    def _launch(self, cmd: list[str], cwd: Path, env: dict[str, str]) -> None:
        if platform.system() == "Windows":
            cmd_txt = f'REM (%KILL_CMD% 22222)\nREM (%KILL_CMD% 3333)\ndel "{(cwd / "cleanup-fluent-test.bat")}"'
            (cwd / "cleanup-fluent-test.bat").write_text(cmd_txt)
        else:
            cmd_txt = f"# kill -9 22222;\n# kill -9 3333;\nrm {(cwd / 'cleanup-fluent-test.sh')}"
            (cwd / "cleanup-fluent-test.sh").write_text(cmd_txt)
        # Find the sifile argument in the command list
        sifile_arg = next(arg for arg in cmd if "-sifile=" in arg)
        Path(sifile_arg.split("-sifile=")[1].strip()).write_text(f"0.0.0.0:{random.randint(0, 10000)}")  # type: ignore
        self._fluent = MockProcess(12345)  # type: ignore


@pytest.fixture(autouse=True)
def mocked_app() -> TestClient:
    mock_fluent_instance = MockFluentInstance("0.0.0.0", "252", "solver", "3d", "double", TransportMode.INSECURE)

    def get_mock_fluent_instance():
        return mock_fluent_instance

    app.dependency_overrides[get_global_fluent_instance] = get_mock_fluent_instance

    client = TestClient(app)

    return client


def test_regular_workflow(tmp_path: Path, mocked_app: TestClient):
    # Test healthy server
    response = mocked_app.get("/health")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.json() == "healthy"  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    # Test getting instance port when fluent has not been launched yet
    response = mocked_app.get("/")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 500  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    # Test starting instance specifying working_dir
    response = mocked_app.post("/start", json={"working_dir": tmp_path.as_posix()})  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    # Test getting instance port after fluent has been launched
    response = mocked_app.get("/")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert "port" in response.json()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert isinstance(response.json()["port"], int)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    # Test shutting down instance
    response = mocked_app.post("/shutdown")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    # Test getting instance port after fluent has been shutdown
    response = mocked_app.get("/")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.status_code == 500  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]


def test_launching_twice(tmp_path: Path, mocked_app: TestClient):
    # GIVEN: Server with Fluent instance launched running in port X
    mocked_app.post("/start", json={"working_dir": tmp_path.as_posix()}).raise_for_status()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    response = mocked_app.get("/")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    response.raise_for_status()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    port = response.json()["port"]  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    # WHEN: Launching the Fluent instance again
    mocked_app.post("/start", json={"working_dir": tmp_path.as_posix()}).raise_for_status()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    # THEN: Port hasn't changed, the instance launch method was not called. We are using the same instance.
    response = mocked_app.get("/")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    response.raise_for_status()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert response.json()["port"] == port  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]


def test_shutdown_twice(tmp_path: Path, mocked_app: TestClient):
    # GIVEN: Server with Fluent instance launched and shutdown
    mocked_app.post("/start", json={"working_dir": tmp_path.as_posix()}).raise_for_status()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    mocked_app.post("/shutdown").raise_for_status()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    # WHEN: Shutting down the Fluent instance again
    # THEN: Nothing happens, request is OK.
    mocked_app.post("/shutdown").raise_for_status()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
