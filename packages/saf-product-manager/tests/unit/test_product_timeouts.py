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
from pathlib import PurePath
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ansys.saf.product_manager._utilities.const import (
    DEFAULT_SAF_OPTISLANG_TIMEOUT,
    DEFAULT_SAF_VISOR_TIMEOUT,
    SAF_OPTISLANG_TIMEOUT,
    SAF_VISOR_TIMEOUT,
)
from ansys.saf.product_manager.optislang_wrapper._optislang_wrapper_manager import (
    CONNECTION_MODE_LOCAL_DOMAIN,
    InternalOptislangManagerImpl,
    OslClient,
)
from ansys.saf.product_manager.visor._visor_manager import InternalVisorManager

OPTISLANG_MANAGER_MODULE = "ansys.saf.product_manager.optislang_wrapper._optislang_wrapper_manager"
VISOR_MANAGER_MODULE = "ansys.saf.product_manager.visor._visor_manager"


class TestOptislangClientTimeout:
    """Ensures every OslClient HTTP call resolves its timeout from SAF_OPTISLANG_TIMEOUT."""

    @pytest.fixture(params=[None, "42"], ids=["default", "from_env"])
    def expected_timeout(self, request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> int:
        env_value: str | None = request.param
        if env_value is None:
            monkeypatch.delenv(SAF_OPTISLANG_TIMEOUT, raising=False)
            return DEFAULT_SAF_OPTISLANG_TIMEOUT
        monkeypatch.setenv(SAF_OPTISLANG_TIMEOUT, env_value)
        return int(env_value)

    @pytest.fixture
    def osl_client(self, expected_timeout: int) -> OslClient:
        manager = object.__new__(InternalOptislangManagerImpl)
        manager._get_service = MagicMock(return_value=SimpleNamespace(secure_flags="uds"))  # type: ignore[method-assign]
        return manager.get_client_object_implement("localhost", 1234)

    def test_optislang_client_connection_uses_env_timeout(
        self,
        mocker: MockerFixture,
        osl_client: OslClient,
        expected_timeout: int,
    ):
        connection_response = MagicMock()
        connection_response.json.return_value = {
            "connection_mode": CONNECTION_MODE_LOCAL_DOMAIN,
            "local_server_id": "localhost:1234#0",
        }
        get_mock = mocker.patch(f"{OPTISLANG_MANAGER_MODULE}.httpx2.get", return_value=connection_response)
        mocker.patch(f"{OPTISLANG_MANAGER_MODULE}.Optislang")

        with osl_client.optislang_client():
            pass

        assert get_mock.call_args.kwargs["timeout"] == expected_timeout

    def test_start_uses_env_timeout(self, mocker: MockerFixture, osl_client: OslClient, expected_timeout: int):
        post_mock = mocker.patch(f"{OPTISLANG_MANAGER_MODULE}.httpx2.post", return_value=MagicMock())

        osl_client.start(
            project_path=PurePath("project.opf"),
            project_properties_file=PurePath("working_properties_file.json"),
            input_files=[],
            osl_version="241",
            loglevel="INFO",
        )

        assert post_mock.call_args.kwargs["timeout"] == expected_timeout

    def test_get_logs_uses_env_timeout(self, mocker: MockerFixture, osl_client: OslClient, expected_timeout: int):
        get_response = MagicMock()
        get_response.content.decode.return_value = "logs"
        get_mock = mocker.patch(f"{OPTISLANG_MANAGER_MODULE}.httpx2.get", return_value=get_response)

        osl_client.get_logs()

        assert get_mock.call_args.kwargs["timeout"] == expected_timeout

    def test_shutdown_uses_env_timeout(self, mocker: MockerFixture, osl_client: OslClient, expected_timeout: int):
        post_mock = mocker.patch(f"{OPTISLANG_MANAGER_MODULE}.httpx2.post", return_value=MagicMock())

        osl_client.shutdown()

        assert post_mock.call_args.kwargs["timeout"] == expected_timeout

    def test_close_optislang_uses_env_timeout(
        self,
        mocker: MockerFixture,
        osl_client: OslClient,
        expected_timeout: int,
    ):
        post_mock = mocker.patch(f"{OPTISLANG_MANAGER_MODULE}.httpx2.post", return_value=MagicMock())

        osl_client.close_optislang()

        assert post_mock.call_args.kwargs["timeout"] == expected_timeout


class TestVisorManagerTimeout:
    """Ensures Visor manager HTTP calls resolve their timeout from SAF_VISOR_TIMEOUT."""

    @pytest.fixture(params=[None, "77"], ids=["default", "from_env"])
    def expected_timeout(self, request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> int:
        env_value: str | None = request.param
        if env_value is None:
            monkeypatch.delenv(SAF_VISOR_TIMEOUT, raising=False)
            return DEFAULT_SAF_VISOR_TIMEOUT
        monkeypatch.setenv(SAF_VISOR_TIMEOUT, env_value)
        return int(env_value)

    @pytest.fixture
    def visor_manager(self, tmp_path: PurePath, expected_timeout: int) -> InternalVisorManager:
        manager = object.__new__(InternalVisorManager)
        manager._state_dirname = ""  # pyright: ignore[reportPrivateUsage]
        manager._project_directory_path_on_solution = tmp_path  # pyright: ignore[reportPrivateUsage, reportAttributeAccessIssue]
        manager._get_service = MagicMock(return_value=SimpleNamespace(host="a-host", port=1111))  # pyright: ignore[reportPrivateUsage]
        return manager

    def test_client_update_uses_env_timeout(
        self,
        mocker: MockerFixture,
        visor_manager: InternalVisorManager,
        expected_timeout: int,
    ):
        info_response = MagicMock()
        info_response.raise_for_status.return_value = info_response
        info_response.json.return_value = {"host": "resolved-host", "port": 4321}
        get_mock = mocker.patch(f"{VISOR_MANAGER_MODULE}.httpx2.get", return_value=info_response)
        client = visor_manager.get_client_object_implement("localhost", 1234)

        post_mock = mocker.patch(f"{VISOR_MANAGER_MODULE}.httpx2.post", return_value=MagicMock())
        client.update("file_path", MagicMock(model_dump=MagicMock(return_value={})))  # pyright: ignore[reportUnknownMemberType]

        assert get_mock.call_args.kwargs["timeout"] == expected_timeout
        assert post_mock.call_args.kwargs["timeout"] == expected_timeout

    def test_initialize_passes_env_timeout_to_visor_service(
        self,
        mocker: MockerFixture,
        visor_manager: InternalVisorManager,
        expected_timeout: int,
    ):
        visor_manager.initialize_service = MagicMock()  # type: ignore[method-assign]
        initialize_visor_mock = mocker.patch.object(visor_manager, "_initialize_visor")

        visor_manager.initialize()

        assert initialize_visor_mock.call_args.kwargs["timeout"] == expected_timeout

    def test_load_state_passes_env_timeout_to_visor_service(
        self,
        mocker: MockerFixture,
        visor_manager: InternalVisorManager,
        expected_timeout: int,
    ):
        initialize_visor_mock = mocker.patch.object(visor_manager, "_initialize_visor")

        visor_manager.load_state_implement()

        assert initialize_visor_mock.call_args.kwargs["timeout"] == expected_timeout

    def test_shutdown_uses_env_timeout(
        self,
        mocker: MockerFixture,
        visor_manager: InternalVisorManager,
        expected_timeout: int,
    ):
        post_mock = mocker.patch(f"{VISOR_MANAGER_MODULE}.httpx2.post", return_value=MagicMock())

        visor_manager.shutdown_implement()

        assert post_mock.call_args.kwargs["timeout"] == expected_timeout


@pytest.mark.parametrize("invalid_timeout", ["", "0", "-1", "not-an-integer"])
def test_optislang_client_rejects_invalid_timeout(
    monkeypatch: pytest.MonkeyPatch,
    invalid_timeout: str,
):
    monkeypatch.setenv(SAF_OPTISLANG_TIMEOUT, invalid_timeout)
    manager = object.__new__(InternalOptislangManagerImpl)
    manager._get_service = MagicMock(return_value=SimpleNamespace(secure_flags="uds"))  # type: ignore[method-assign]

    with pytest.raises(ValueError, match=f"{SAF_OPTISLANG_TIMEOUT} must be a positive integer"):
        manager.get_client_object_implement("localhost", 1234)


@pytest.mark.parametrize("invalid_timeout", ["", "0", "-1", "not-an-integer"])
def test_visor_client_rejects_invalid_timeout(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    invalid_timeout: str,
):
    monkeypatch.setenv(SAF_VISOR_TIMEOUT, invalid_timeout)
    mocker.patch(f"{VISOR_MANAGER_MODULE}.httpx2.get")
    manager = object.__new__(InternalVisorManager)

    with pytest.raises(ValueError, match=f"{SAF_VISOR_TIMEOUT} must be a positive integer"):
        manager.get_client_object_implement("localhost", 1234)
