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

import re

from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient
from joserfc.jwk import OctKey
import pytest
from pytest_httpx2 import HTTPXMock

from ansys.iam.oidc import (
    DEFAULT_SUBPROTOCOL_PREFIX,
    NoIssuerOrAudienceError,
    OidcWebSocketDependency,
    decode_base64_token,
)

pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)


@pytest.fixture(autouse=True)
def metadata_server_mock(httpx_mock: HTTPXMock, secret_key: OctKey) -> None:
    httpx_mock.add_response(
        url="http://test_issuer_url/.well-known/openid-configuration",
        json={"jwks_uri": "http://jwks_uri"},
    )
    keys = {"keys": [secret_key.as_dict()]}
    httpx_mock.add_response(
        url="http://jwks_uri",
        json=keys,
    )


@pytest.mark.parametrize(
    ("oidc_issuer", "audience"),
    [(None, None), ("http://test_issuer_url", None), (None, "audience")],
)
def test_auto_error_requires_issuer_and_audience(oidc_issuer: str | None, audience: str | None) -> None:
    with pytest.raises(
        NoIssuerOrAudienceError,
        match=re.escape("Both 'oidc_issuer' and 'audience' must be provided when 'auto_error' is True."),
    ):
        OidcWebSocketDependency(oidc_issuer=oidc_issuer, audience=audience, auto_error=True)


@pytest.mark.usefixtures("encode_token")
@pytest.mark.parametrize("endpoint", ["/token", "/token_optional_auth", "/token_without_issuer_auth"])
class TestWebSocketRequests:
    @pytest.mark.parametrize("encode_token", [True], indirect=True)
    def test_authorized_websocket_returns_token(self, client: TestClient, dummy_jwt_token: str, endpoint: str) -> None:
        with client.websocket_connect(endpoint, subprotocols=[f"{DEFAULT_SUBPROTOCOL_PREFIX}{dummy_jwt_token}"]) as ws:
            assert ws.receive_text() == decode_base64_token(dummy_jwt_token)

    @pytest.mark.parametrize("encode_token", [False], indirect=True)
    def test_websocket_token_not_base64_encoded_raise_1008_if_not_optional(
        self,
        client: TestClient,
        dummy_jwt_token: str,
        endpoint: str,
    ) -> None:
        if endpoint == "/token":
            with (
                pytest.raises(WebSocketDisconnect) as e,
                client.websocket_connect(
                    "/token",
                    subprotocols=[f"{DEFAULT_SUBPROTOCOL_PREFIX}{dummy_jwt_token}"],
                ),
            ):
                ...
            assert e.value.code == 1008
            assert "Token cannot be decoded: " in e.value.reason
        else:
            with client.websocket_connect(
                "/token_optional_auth",
                subprotocols=[f"{DEFAULT_SUBPROTOCOL_PREFIX}{dummy_jwt_token}"],
            ) as ws:
                assert ws.receive_text() == dummy_jwt_token

    def test_websocket_no_token_raise_1008_if_not_optional(self, client: TestClient, endpoint: str) -> None:
        if endpoint == "/token":
            with pytest.raises(WebSocketDisconnect) as e, client.websocket_connect("/token"):
                ...
            assert e.value.code == 1008
            assert "Not authenticated" in e.value.reason
        else:
            with client.websocket_connect("/token_optional_auth") as ws:
                assert ws.receive_text() == "no_token"

    @pytest.mark.parametrize("encode_token", [True], indirect=True)
    @pytest.mark.parametrize(
        ("invalid_token", "error_msg"),
        [
            ("expired", "The token is expired"),
            ("wrong_iss", "Invalid claim: 'iss'"),
            ("wrong_aud", "Invalid claim: 'aud'"),
            ("wrong_nbf", "The token is not yet valid"),
        ],
        indirect=["invalid_token"],
    )
    def test_websocket_invalid_token_raise_1008_if_not_optional(
        self,
        client: TestClient,
        invalid_token: str,
        error_msg: str,
        endpoint: str,
    ) -> None:
        if endpoint == "/token":
            with (
                pytest.raises(WebSocketDisconnect) as e,
                client.websocket_connect(
                    "/token",
                    subprotocols=[f"{DEFAULT_SUBPROTOCOL_PREFIX}{invalid_token}"],
                ),
            ):
                ...
            assert e.value.code == 1008
            assert f"The token is invalid: {error_msg}" in e.value.reason
        else:
            with client.websocket_connect(
                "/token_optional_auth",
                subprotocols=[f"{DEFAULT_SUBPROTOCOL_PREFIX}{invalid_token}"],
            ) as ws:
                assert ws.receive_text() == decode_base64_token(invalid_token)


@pytest.mark.parametrize("encode_token", [True], indirect=True)
def test_authorized_websocket_custom_prefix_returns_token(client: TestClient, dummy_jwt_token: str) -> None:
    with client.websocket_connect("/token_custom_prefix", subprotocols=[f"my.mock.prefix.{dummy_jwt_token}"]) as ws:
        assert ws.receive_text() == decode_base64_token(dummy_jwt_token)
