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

import logging
import os
import pathlib
from unittest import mock

import pytest
import uvicorn
import uvicorn.supervisors

from ansys.saf.glow._config.const import (
    DEFAULT_DEBUG_PORT,
    GLOW_API_HOT_RELOAD,
    GLOW_DEBUG,
    GLOW_DEBUG_API_PORT,
    GLOW_DEPLOYMENT,
    Deployment,
)
from ansys.saf.glow.cli._cli_entry_point import run_api
from tests.mocks.solutions import minimal_solution

solution = minimal_solution


@pytest.fixture(autouse=True)
def mock_settings_env_vars(tmp_path: pathlib.Path):
    tmp_path_str = str(tmp_path)
    with mock.patch.dict(
        os.environ,
        {
            "APPDATA": tmp_path_str,
            "XDG_DATA_HOME": tmp_path_str,
            GLOW_DEPLOYMENT: Deployment.Desktop.name,
        },
    ):
        yield


def test_api_server_debug_port_disabled(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(GLOW_DEBUG, str(True))
    monkeypatch.setenv(GLOW_DEBUG_API_PORT, str(-1))

    with (
        mock.patch.object(uvicorn.supervisors.ChangeReload, "run"),
        mock.patch.object(
            logging.Logger,
            "info",
        ) as logging_info_mock,
    ):
        run_api("127.0.0.1", 50000, request.module.solution)  # type: ignore
        assert not any(
            args[0][0].startswith("#### API server listening for debug on port:")
            for args in logging_info_mock.call_args_list
        )


@pytest.mark.parametrize(
    ("configured_port", "port_blocked"),
    [(None, False), (None, True), (56463, False), (56463, True)],
)
def test_api_server_debug_port_enabled(
    request: pytest.FixtureRequest,
    configured_port: int | None,
    port_blocked: bool,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Test four different scenarios for debugpy port configuration:
    - Port configured and free: port is logged and debugpy is called with it.
    - Port configured and not free: port is logged and debugpy is called with it.
    Then, debugpy raises an exception and GLOW crashes.
    - Port not configured and free: default port is logged and debugpy is called with it.
    - Port not configured and not free: next_free_port returns a new port, which is logged
    and then used to call debugpy.
    """

    def free_port_mock(port: int) -> int:
        return port + int(port_blocked)

    def listen_mocked(port: int):
        if configured_port and port_blocked:
            raise Exception(f"Port {port} in use")

    monkeypatch.setenv(GLOW_DEBUG, str(True))
    if configured_port:
        monkeypatch.setenv(GLOW_DEBUG_API_PORT, str(configured_port))
    else:
        monkeypatch.delenv(GLOW_DEBUG_API_PORT, raising=False)

    with (
        mock.patch.object(uvicorn.supervisors.ChangeReload, "run"),
        mock.patch(
            "ansys.saf.glow._server.main.next_free_port",
        ) as next_free_port_mock,
        mock.patch("debugpy.listen") as debugpy_listen_mock,
        mock.patch.object(
            logging.Logger,
            "info",
        ) as logging_info_mock,
    ):
        next_free_port_mock.side_effect = free_port_mock
        debugpy_listen_mock.side_effect = listen_mocked

        if configured_port and port_blocked:
            with pytest.raises(Exception, match=f"Port {configured_port} in use"):
                run_api("127.0.0.1", 50000, request.module.solution)  # type: ignore
        else:
            run_api("127.0.0.1", 50000, request.module.solution)  # type: ignore

        debugpy_port_called = debugpy_listen_mock.call_args[0][0]
        debugpy_port_from_log = None
        for args in logging_info_mock.call_args_list:
            if args[0][0].startswith("#### API server listening for debug on port:"):
                debugpy_port_from_log = int(
                    args[0][0].split("#### API server listening for debug on port:")[1].split(" ####")[0],
                )
        expected_port = configured_port if configured_port is not None else DEFAULT_DEBUG_PORT
        if not configured_port and port_blocked:
            expected_port += 1

        assert expected_port == debugpy_port_called
        assert expected_port == debugpy_port_from_log


@pytest.mark.parametrize("debug", [True, False])
@pytest.mark.parametrize("hot_reload", [True, False])
def test_api_server_hot_reload(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    debug: bool,
    hot_reload: bool,
):
    monkeypatch.setenv(GLOW_DEBUG_API_PORT, str(-1))
    monkeypatch.setenv(GLOW_DEBUG, str(debug))
    monkeypatch.setenv(GLOW_API_HOT_RELOAD, str(hot_reload))

    with (
        mock.patch.object(uvicorn, "run") as run_mock,
        mock.patch.object(
            logging.Logger,
            "info",
        ) as logging_info_mock,
    ):
        run_api("127.0.0.1", 50000, request.module.solution)  # type: ignore
        log_msg_found = any(
            args[0][0] == "#### Uvicorn hot reload enabled. ####" for args in logging_info_mock.call_args_list
        )
        assert log_msg_found == (debug and hot_reload)
        assert run_mock.call_args_list[0].kwargs["reload"] == (debug and hot_reload)
