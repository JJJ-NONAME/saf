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
from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
import pytest
import pytest_mock

from ansys.saf.glow._mcp.server import build_app
from tests.mocks.solution_end_to_end.solution import definition
from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution


@pytest.fixture
async def mcp_unit_client() -> AsyncGenerator[Client[FastMCPTransport], None]:
    mcp = build_app(
        definition_module=definition,
        solution_class=EndToEndSolution,
        solution_api_url="http://localhost:8000",
    )
    async with Client(transport=mcp) as client:
        yield client


@pytest.fixture
def mock_glow_client(mocker: pytest_mock.MockerFixture) -> tuple[MagicMock, MagicMock]:
    mock_class = mocker.MagicMock()
    mock_instance = mock_class.return_value.__enter__.return_value
    mocker.patch("ansys.saf.glow._mcp.server.Client", mock_class)
    return mock_class, mock_instance
