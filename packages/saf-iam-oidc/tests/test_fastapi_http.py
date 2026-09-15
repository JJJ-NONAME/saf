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

from fastapi.testclient import TestClient
from joserfc.jwk import OctKey
import pytest
from pytest_httpx2 import HTTPXMock

from ansys.iam.oidc import NoIssuerOrAudienceError, OidcDependency

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
        OidcDependency(oidc_issuer=oidc_issuer, audience=audience, auto_error=True)


@pytest.mark.parametrize("caplog", ["ansys.iam.oidc._fastapi"], indirect=True)
@pytest.mark.parametrize("endpoint", ["/token", "/token_optional_auth", "/token_without_issuer_auth"])
class TestHttpRequests:
    def test_authorized_request_returns_token(
        self,
        client: TestClient,
        dummy_jwt_token: str,
        endpoint: str,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        response = client.get(endpoint, headers={"Authorization": f"Bearer {dummy_jwt_token}"})  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        debug_messages = [record.message for record in caplog.records if record.levelname == "DEBUG"]
        assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType]
        assert response.json() == dummy_jwt_token  # pyright: ignore[reportUnknownMemberType]
        if endpoint == "/token":
            assert any("The validation of the access token was successful." in msg for msg in debug_messages)
        else:
            assert any("The validation of the access token was skipped." in msg for msg in debug_messages)

    def test_no_header_raise_401_if_not_optional(
        self,
        client: TestClient,
        endpoint: str,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        response = client.get(endpoint)  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        debug_messages = [record.message for record in caplog.records if record.levelname == "DEBUG"]
        if endpoint == "/token":
            assert response.status_code == 401  # pyright: ignore[reportUnknownMemberType]
            assert response.json() == {"detail": "Not authenticated"}  # pyright: ignore[reportUnknownMemberType]
        else:
            assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType]
            assert response.json() is None  # pyright: ignore[reportUnknownMemberType]
            assert any("No authorization header was included in the request." in msg for msg in debug_messages)

    def test_header_no_bearer_raise_401_if_not_optional(
        self,
        client: TestClient,
        endpoint: str,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        response = client.get(endpoint, headers={"Authorization": "NotBearer something"})  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        debug_messages = [record.message for record in caplog.records if record.levelname == "DEBUG"]
        if endpoint == "/token":
            assert response.status_code == 401  # pyright: ignore[reportUnknownMemberType]
            assert response.json() == {"detail": "Not authenticated"}  # pyright: ignore[reportUnknownMemberType]
        else:
            assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType]
            assert response.json() is None  # pyright: ignore[reportUnknownMemberType]
            assert any("No bearer access token in the request's authorization header." in msg for msg in debug_messages)

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
    def test_invalid_token_raise_401_if_not_optional(
        self,
        client: TestClient,
        invalid_token: str,
        error_msg: str,
        endpoint: str,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        response = client.get(endpoint, headers={"Authorization": f"Bearer {invalid_token}"})  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        debug_messages = [record.message for record in caplog.records if record.levelname == "DEBUG"]
        if endpoint == "/token":
            assert response.status_code == 401  # pyright: ignore[reportUnknownMemberType]
            assert response.json() == {"detail": f"The token is invalid: {error_msg}"}  # pyright: ignore[reportUnknownMemberType]
        else:
            assert response.status_code == 200  # pyright: ignore[reportUnknownMemberType]
            assert response.json() == invalid_token  # pyright: ignore[reportUnknownMemberType]
            assert any("The validation of the access token was skipped." in msg for msg in debug_messages)
