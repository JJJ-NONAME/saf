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
import builtins
from unittest.mock import MagicMock

import pytest
import pytest_mock

from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._server.server import mount_mcp_app
from tests.mocks.solution_end_to_end.solution import definition
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution

_SOLUTION_DEF = "tests.mocks.solution_end_to_end.solution.definition"


def test_returns_app_unchanged_when_mcp_disabled(mocker: pytest_mock.MockerFixture, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GLOW_MCP_DISABLED", "true")
    mock_build_app = mocker.patch("ansys.saf.glow._mcp.server.build_app")
    mock_app = MagicMock()

    result = mount_mcp_app(mock_app, Settings(glow_solution_definition=_SOLUTION_DEF))

    assert result is mock_app
    mock_app.mount.assert_not_called()
    mock_build_app.assert_not_called()


def test_returns_app_unchanged_when_auth_enabled(mocker: pytest_mock.MockerFixture, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GLOW_MCP_DISABLED", "false")
    monkeypatch.setenv("GLOW_AUTH_DISABLED", "false")
    mock_build_app = mocker.patch("ansys.saf.glow._mcp.server.build_app")
    mock_app = MagicMock()

    result = mount_mcp_app(mock_app, Settings(glow_solution_definition=_SOLUTION_DEF))

    assert result is mock_app
    mock_app.mount.assert_not_called()
    mock_build_app.assert_not_called()


@pytest.mark.parametrize("missing_dep", ["fastmcp", "mcp"])
def test_returns_app_unchanged_when_missing_modules(
    missing_dep: str,
    mocker: pytest_mock.MockerFixture,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("GLOW_MCP_DISABLED", "false")

    original_import = builtins.__import__

    def _import_with_missing_dep(name, globals=None, locals=None, fromlist=(), level=0):  # noqa: A002 # type: ignore
        if name == missing_dep or name.startswith(f"{missing_dep}."):  # type: ignore
            raise ModuleNotFoundError(f"No module named '{missing_dep}'")
        return original_import(name, globals, locals, fromlist, level)  # type: ignore

    mocker.patch("builtins.__import__", side_effect=_import_with_missing_dep)
    mock_build_app = mocker.patch("ansys.saf.glow._mcp.server.build_app")
    mock_app = MagicMock()

    result = mount_mcp_app(mock_app, Settings(glow_solution_definition=_SOLUTION_DEF))

    assert result is mock_app
    mock_app.mount.assert_not_called()
    mock_build_app.assert_not_called()


def test_mounts_mcp_on_success(mocker: pytest_mock.MockerFixture, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GLOW_MCP_DISABLED", "false")
    mock_build_app = mocker.patch("ansys.saf.glow._mcp.server.build_app")
    mock_combine_lifespans = mocker.patch("fastmcp.utilities.lifespan.combine_lifespans")
    mock_app = MagicMock()
    original_lifespan_context = mock_app.router.lifespan_context
    settings = Settings(glow_solution_definition=_SOLUTION_DEF)

    result = mount_mcp_app(mock_app, settings)

    mock_build_app.assert_called_once_with(
        definition_module=definition,
        solution_class=EndToEndSolution,
        solution_api_url="http://localhost:5432",
    )
    mcp_app = mock_build_app.return_value.http_app.return_value
    mock_build_app.return_value.http_app.assert_called_once_with(path="/", transport="http")
    mock_app.mount.assert_called_once_with("/sse", mcp_app)
    mock_combine_lifespans.assert_called_once_with(original_lifespan_context, mcp_app.lifespan)
    assert mock_app.router.lifespan_context is mock_combine_lifespans.return_value
    assert result is mock_app


def test_mounts_mcp_with_custom_settings(mocker: pytest_mock.MockerFixture, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GLOW_MCP_DISABLED", "false")
    monkeypatch.setenv("GLOW_MCP_TRANSPORT_MODE", "sse")
    monkeypatch.setenv("GLOW_MCP_PATH", "/custom-mcp-path")
    monkeypatch.setenv("GLOW_EXTERNAL_API_URL", "http://example.com")
    monkeypatch.setenv("GLOW_API_PORT", "8000")
    mock_build_app = mocker.patch("ansys.saf.glow._mcp.server.build_app")
    mocker.patch("fastmcp.utilities.lifespan.combine_lifespans")
    mock_app = MagicMock()

    result = mount_mcp_app(mock_app, Settings(glow_solution_definition=_SOLUTION_DEF))

    mock_build_app.assert_called_once_with(
        definition_module=definition,
        solution_class=EndToEndSolution,
        solution_api_url="http://localhost:8000",  # always uses internal host, ignoring external url
    )
    mock_build_app.return_value.http_app.assert_called_once_with(path="/", transport="sse")
    mock_app.mount.assert_called_once_with("/custom-mcp-path", mock_build_app.return_value.http_app.return_value)
    assert result is mock_app
