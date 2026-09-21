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

import os
import sys

from click.testing import CliRunner
import pytest
from pytest_mock import MockerFixture

from ansys.saf.product_configuration.wrappers import aedt


def test_cli_custom_valid_options(mocker: MockerFixture):
    host = "127.0.0.1"
    port = 46547
    version = "251"
    transport_mode = "uds"

    uvicorn_mocked = mocker.patch("uvicorn.run")
    runner = CliRunner()
    result = runner.invoke(
        aedt.main,
        [
            "--host",
            host,
            "--port",
            str(port),
            "--version",
            version,
            "--transport-mode",
            transport_mode,
        ],
    )
    assert result.exit_code == 0

    uvicorn_mocked.assert_called_once()
    assert uvicorn_mocked.call_args_list[0][1] == {"host": host, "port": port}
    assert aedt._selected_version == version  # pyright: ignore[reportPrivateUsage]
    assert aedt._product_host == host  # pyright: ignore[reportPrivateUsage]


def test_run_service_manager(mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch):
    host = "172.16.0.5"
    port = 50505
    version = "251"
    transport_mode = "insecure"

    mock_common_rpc = mocker.MagicMock()
    monkeypatch.setitem(sys.modules, "ansys.aedt.core.common_rpc", mock_common_rpc)
    service_manager_mock = mock_common_rpc.pyaedt_service_manager

    monkeypatch.delenv("AEDT_HOST", raising=False)

    # Call run_service_manager
    aedt._run_service_manager(host, port, version, transport_mode)  # type: ignore

    # Host is set
    assert os.environ.get("AEDT_HOST") == host
    # Pyaedt is called with correct port and version
    service_manager_mock.assert_called_once_with(port=port, aedt_version=version)
