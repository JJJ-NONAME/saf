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

from unittest.mock import MagicMock

from joserfc.errors import ExpiredTokenError
import pytest
import pytest_mock
import requests_oauthlib

from ansys.saf.glow._hps_auth.interactive_authenticator import HpsConfig, HpsInteractiveAuthenticator


@pytest.mark.parametrize("hps_server_host", ["localhost", "127.0.0.1"])
def test_acquire_token_interactive_flow(mocker: pytest_mock.MockerFixture, hps_server_host: str) -> None:
    mocker.patch.object(
        HpsInteractiveAuthenticator,
        "get_config",
        return_value=(
            HpsConfig(
                base_auth_url="https://localhost:8080/test_auth/realms",
                token_endpoint="https://localhost:8080/test_auth/realms/test_realm/protocol/openid-connect/token",
                client_id="test_client",
                scope="",
                discovery_endpoint="",
                authorization_endpoint="https://localhost:8080/test_auth/realms/test_realm/protocol/openid-connect/auth",
                issuer="",
            )
        ),
    )
    mocker.patch(
        "ansys.saf.glow._hps_auth.interactive_authenticator.get_random_free_port",
        return_value=12345,
    )
    mock_oauth_session = mocker.spy(requests_oauthlib.OAuth2Session, "__init__")
    mock_webbrowser = mocker.patch("webbrowser.open")
    mock_socketserver = mocker.patch("socketserver.TCPServer")
    mock_server_instance: MagicMock = MagicMock()
    mock_server_instance.access_token = "test_access_token"
    mock_server_instance.refresh_token = "test_refresh_token"
    mock_socketserver.return_value.__enter__.return_value = mock_server_instance

    access_token, refresh_token = HpsInteractiveAuthenticator.acquire_token(
        hps_server_url=f"https://{hps_server_host}:8080",
        client_id="test_client",
    )

    mock_oauth_session.assert_called_once()
    assert mock_oauth_session.call_args[1] == {
        "client_id": "test_client",
        "redirect_uri": "http://localhost:12345/callback",
        "scope": ["openid", "profile", "email"],
    }

    # always localhost, 127.0.0.1 is normalized
    mock_webbrowser.assert_called_once()
    assert mock_webbrowser.call_args[0][0].startswith(
        "https://localhost:8080/test_auth/realms/test_realm/protocol/openid-connect/auth?response_type=code&client_id=test_client",
    )

    assert access_token == "test_access_token"
    assert refresh_token == "test_refresh_token"


def test_check_token_validity_empty_token() -> None:
    assert not HpsInteractiveAuthenticator.check_token_validity("")


def test_check_token_validity_expired_token(mocker: pytest_mock.MockerFixture, dummy_jwt_token: str) -> None:
    mock_jwt = mocker.patch("joserfc.jwt.JWTClaimsRegistry.validate", side_effect=ExpiredTokenError("Token expired"))
    assert not HpsInteractiveAuthenticator.check_token_validity(dummy_jwt_token)
    mock_jwt.assert_called_once()


def test_check_token_validity_valid_token(mocker: pytest_mock.MockerFixture, dummy_jwt_token: str) -> None:
    mock_jwt = mocker.patch("joserfc.jwt.JWTClaimsRegistry.validate")
    assert HpsInteractiveAuthenticator.check_token_validity(dummy_jwt_token)
    mock_jwt.assert_called_once()


@pytest.mark.parametrize("hps_server_host", ["localhost", "127.0.0.1"])
def test_refresh_token_success(mocker: pytest_mock.MockerFixture, hps_server_host: str) -> None:
    mocker.patch.object(
        HpsInteractiveAuthenticator,
        "get_config",
        return_value=(
            HpsConfig(
                base_auth_url="http://localhost:8080/test_auth/realms",
                token_endpoint="http://localhost:8080/test_auth/realms/test_realm/protocol/openid-connect/token",
                client_id="",
                scope="",
                discovery_endpoint="",
                authorization_endpoint="",
                issuer="",
            )
        ),
    )
    mock_oauth_session = mocker.patch(
        "requests_oauthlib.OAuth2Session.refresh_token",
        return_value={
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
        },
    )

    access_token, refresh_token = HpsInteractiveAuthenticator.refresh_token(
        hps_server_url=f"http://{hps_server_host}:8080",
        client_id="test_client",
        refresh_token="existing_refresh_token",
    )

    assert access_token == "new_access_token"
    assert refresh_token == "new_refresh_token"
    # always localhost, 127.0.0.1 is normalized
    mock_oauth_session.assert_called_once_with(
        "http://localhost:8080/test_auth/realms/test_realm/protocol/openid-connect/token",
        refresh_token="existing_refresh_token",
        verify=False,
        body="client_id=test_client",
    )
