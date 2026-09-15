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
from unittest.mock import MagicMock

import pytest
import pytest_mock

from ansys.saf.glow._core.instance.healthcheck import GrpcHealthClient

_HOST = "127.0.0.1"
_PORT = 50000
_HEALTH_ROUTE = ""


class TestGrpcHealthClient:
    @pytest.fixture
    def mock_health_request(self, mocker: pytest_mock.MockerFixture) -> tuple[MagicMock, MagicMock]:
        mock_stub_cls = mocker.patch("ansys.saf.glow._core.instance.healthcheck.health_pb2_grpc.HealthStub")
        mock_stub = MagicMock()
        mock_stub_cls.return_value = mock_stub
        mock_response = MagicMock()
        mock_response.status = 1  # SERVING
        mock_stub.Check.return_value = mock_response
        mock_resp_cls = mocker.patch("ansys.saf.glow._core.instance.healthcheck.health_pb2.HealthCheckResponse")
        mock_resp_cls.SERVING = 1
        return mock_stub_cls, mock_stub

    def test_channel_and_stub_created_on_first_healthy_call(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_health_request: tuple[MagicMock, MagicMock],
    ) -> None:
        client = GrpcHealthClient(host=_HOST, port=_PORT, health_route=_HEALTH_ROUTE)
        assert client._channel is None  # type: ignore[reportPrivateUsage]
        assert client._health_stub is None  # type: ignore[reportPrivateUsage]

        mock_create_channel = mocker.spy(client, "_create_channel")
        mock_stub_cls, mock_stub = mock_health_request

        assert client.is_healthy() is True

        mock_create_channel.assert_called_once_with(_HOST, _PORT, _HEALTH_ROUTE)
        mock_stub_cls.assert_called_once()
        assert client._channel  # type: ignore[reportPrivateUsage]
        assert client._health_stub is mock_stub  # type: ignore[reportPrivateUsage]

    def test_channel_and_stub_reused_on_subsequent_calls(
        self,
        mocker: pytest_mock.MockerFixture,
        mock_health_request: tuple[MagicMock, MagicMock],
    ) -> None:
        client = GrpcHealthClient(host=_HOST, port=_PORT, health_route=_HEALTH_ROUTE)

        mock_create_channel = mocker.spy(client, "_create_channel")
        mock_stub_cls, _ = mock_health_request

        assert client.is_healthy() is True
        assert client.is_healthy() is True

        mock_create_channel.assert_called_once()
        mock_stub_cls.assert_called_once()

    def test_uds_socket_missing_returns_false_and_does_not_cache_channel(self, tmp_path: Path) -> None:
        uds_dir = tmp_path / "sockets"
        uds_dir.mkdir()
        client = GrpcHealthClient(
            host=_HOST,
            port=_PORT,
            health_route=_HEALTH_ROUTE,
            uds_dir=str(uds_dir),
            uds_id="test-id",
            secure_flags="--transport-mode=UDS",
        )

        assert client.is_healthy() is False

        assert client._channel is None  # type: ignore[reportPrivateUsage]
        assert client._health_stub is None  # type: ignore[reportPrivateUsage]

    def test_uds_socket_appears_on_retry(
        self,
        tmp_path: Path,
        mocker: pytest_mock.MockerFixture,
        mock_health_request: tuple[MagicMock, MagicMock],
    ) -> None:
        uds_dir = tmp_path / "sockets"
        uds_dir.mkdir()
        client = GrpcHealthClient(
            host=_HOST,
            port=_PORT,
            health_route=_HEALTH_ROUTE,
            uds_dir=str(uds_dir),
            uds_id="test-id",
            secure_flags="--transport-mode=UDS",
        )

        assert client.is_healthy() is False
        assert client._channel is None  # type: ignore[reportPrivateUsage]
        assert client._health_stub is None  # type: ignore[reportPrivateUsage]

        socket_file = uds_dir / "mockproduct-test-id.sock"
        socket_file.touch()

        mock_create_channel = mocker.spy(client, "_create_channel")
        mock_stub_cls, mock_stub = mock_health_request

        assert client.is_healthy() is True

        mock_create_channel.assert_called_once()
        mock_stub_cls.assert_called_once()
        assert client._channel  # type: ignore[reportPrivateUsage]
        assert client._health_stub is mock_stub  # type: ignore[reportPrivateUsage]

    @pytest.mark.usefixtures("mock_health_request")
    def test_close_resets_channel_and_stub(self, mocker: pytest_mock.MockerFixture) -> None:
        client = GrpcHealthClient(host=_HOST, port=_PORT, health_route=_HEALTH_ROUTE)

        assert client.is_healthy() is True
        assert client._channel  # type: ignore[reportPrivateUsage]
        assert client._health_stub  # type: ignore[reportPrivateUsage]

        mock_channel = mocker.spy(client._channel, "close")  # type: ignore[reportPrivateUsage]
        client.close()

        assert client._channel is None  # type: ignore[reportPrivateUsage]
        assert client._health_stub is None  # type: ignore[reportPrivateUsage]
        mock_channel.assert_called_once()
