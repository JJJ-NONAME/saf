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

from fastapi import status
from fastapi.testclient import TestClient
import pytest
import pytest_mock

from ansys.saf.glow._config.const import DatabaseType, ProductInstanceSystemType
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._hps_auth.interactive_authenticator import HpsInteractiveAuthenticator
from ansys.saf.glow._server.hps_auth_info import HpsAuthInfo
import tests.mocks.solutions.desktop as desktop

pytestmark = pytest.mark.parametrize(
    "mock_module_settings",
    [{"glow_database_type": DatabaseType.Sqlite}, {"glow_database_type": DatabaseType.PostgreSql}],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = desktop


def test_docs(client: TestClient):
    response = client.get("openapi.json")
    assert "/desktop:exit" in list(response.json()["paths"].keys())
    assert "/desktop:hps-auth-info" in list(response.json()["paths"].keys())


@pytest.fixture(autouse=True)
def mock_hps_auth_info(mocker: pytest_mock.MockerFixture):
    # cleanup hps auth info between tests
    mocker.patch("ansys.saf.glow._server.dependencies._hps_auth_info", dict[str, HpsAuthInfo]())


@pytest.mark.parametrize(
    "settings",
    [
        {
            "glow_product_instance_system": ProductInstanceSystemType.HPS,
            "glow_product_instance_system_host": "fake_host",
            "glow_product_instance_system_port": 8888,
            "glow_hps_host": None,
            "glow_hps_port": None,
            "glow_hps_username": None,
            "glow_hps_password": None,
        },
    ],
    ids=["hps"],
    indirect=["settings"],
)
def test_get_hps_auth_info_using_instance_env_vars(
    settings: Settings,
    client: TestClient,
    mocker: pytest_mock.MockerFixture,
):
    # GIVEN: GLOW API configured with instance system using HPS
    assert settings.glow_product_instance_system == ProductInstanceSystemType.HPS
    assert settings.computed_glow_product_instance_system_host == "fake_host"
    assert settings.computed_glow_product_instance_system_port == 8888
    assert settings.computed_glow_hps_host == "fake_host"
    assert settings.computed_glow_hps_port == 8888
    assert not settings.glow_hps_username
    assert not settings.glow_hps_password
    # WHEN: asking for tokens multiple times
    mocked_interactive_auth = mocker.patch.object(
        HpsInteractiveAuthenticator,
        "acquire_token",
        return_value=("fake_token", "fake_refresh"),
    )
    response = client.get("/desktop:hps-auth-info")
    # THEN: same tokens are retrieved every time
    assert response.status_code == 200
    assert response.json() == {"access_token": "fake_token", "refresh_token": "fake_refresh"}
    mocked_check_token_validity = mocker.patch.object(
        HpsInteractiveAuthenticator,
        "check_token_validity",
        return_value=True,
    )
    response = client.get("/desktop:hps-auth-info")
    assert response.status_code == 200
    assert response.json() == {"access_token": "fake_token", "refresh_token": "fake_refresh"}
    # THEN: the interactive authenticator is only called once with the correct host and port
    mocked_interactive_auth.assert_called_once_with(
        hps_server_url="https://fake_host:8888/hps",
        client_id="rep-jms-web",
    )
    mocked_check_token_validity.assert_called_once_with("fake_token")


@pytest.mark.parametrize(
    "settings",
    [
        {
            "glow_hps_host": "fake_host",
            "glow_hps_port": 8888,
            "glow_hps_username": None,
            "glow_hps_password": None,
        },
        {
            "glow_product_instance_system": ProductInstanceSystemType.PIM,
            "glow_product_instance_system_host": "my_host",
            "glow_product_instance_system_port": 3333,
            "glow_hps_host": "fake_host",
            "glow_hps_port": 8888,
            "glow_hps_username": None,
            "glow_hps_password": None,
        },
    ],
    ids=["no_system", "pim"],
    indirect=["settings"],
)
def test_get_hps_auth_info_using_hps_env_vars(
    settings: Settings,
    client: TestClient,
    mocker: pytest_mock.MockerFixture,
):
    # GIVEN: GLOW API configured with HPS env vars and without instance system or with PIM as instance system
    assert settings.glow_product_instance_system != ProductInstanceSystemType.HPS
    assert settings.computed_glow_product_instance_system_host != "fake_host"
    assert settings.computed_glow_product_instance_system_port != 8888
    assert settings.computed_glow_hps_host == "fake_host"
    assert settings.computed_glow_hps_port == 8888
    assert not settings.glow_hps_username
    assert not settings.glow_hps_password
    # WHEN: asking for tokens
    mocked_interactive_auth = mocker.patch.object(
        HpsInteractiveAuthenticator,
        "acquire_token",
        return_value=("fake_token", "fake_refresh"),
    )
    response = client.get("/desktop:hps-auth-info")
    # THEN: tokens are retrieved and interactive authenticator is called with correct host and port
    assert response.status_code == 200
    assert response.json() == {"access_token": "fake_token", "refresh_token": "fake_refresh"}
    mocked_interactive_auth.assert_called_once_with(
        hps_server_url="https://fake_host:8888/hps",
        client_id="rep-jms-web",
    )


@pytest.mark.parametrize(
    "settings",
    [
        {
            "glow_product_instance_system": ProductInstanceSystemType.PIM,
            "glow_product_instance_system_host": "fake_host",
            "glow_product_instance_system_port": 8888,
            "glow_hps_host": None,
            "glow_hps_port": None,
            "glow_hps_username": None,
            "glow_hps_password": None,
        },
    ],
    ids=["debug"],
    indirect=["settings"],
)
def test_get_hps_auth_info_using_pim_as_instance_system_raises_error(settings: Settings, client: TestClient):
    # GIVEN: GLOW API configured with instance system using PIM and without HPS env vars
    assert settings.glow_product_instance_system == ProductInstanceSystemType.PIM
    assert settings.computed_glow_product_instance_system_host == "fake_host"
    assert settings.computed_glow_product_instance_system_port == 8888
    assert not settings.computed_glow_hps_host
    assert settings.computed_glow_hps_port is None
    assert not settings.glow_hps_username
    assert not settings.glow_hps_password
    # WHEN: asking for tokens
    response = client.get("/desktop:hps-auth-info")
    # THEN: an error is raised because host and/or port are unconfigured
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "HPS system unconfigured."


@pytest.mark.parametrize(
    "settings",
    [
        {
            "glow_hps_host": "fake_host",
            "glow_hps_port": 8888,
            "glow_hps_username": "fake_user",
            "glow_hps_password": "fake_pwd",
        },
    ],
    ids=["username-password"],
    indirect=["settings"],
)
def test_get_hps_auth_info_using_hps_user_pwd(
    settings: Settings,
    client: TestClient,
    mocker: pytest_mock.MockerFixture,
):
    # GIVEN: GLOW API configured with HPS user and password
    assert settings.glow_hps_username == "fake_user"
    assert settings.glow_hps_password == "fake_pwd"
    # WHEN: asking for tokens
    mocked_interactive_auth = mocker.patch.object(
        HpsInteractiveAuthenticator,
        "acquire_token",
        return_value=("fake_token", "fake_refresh"),
    )
    response = client.get("/desktop:hps-auth-info")
    # THEN: empty tokens are retrieved and interactive authenticator is not called
    assert response.status_code == 200
    assert response.json() == {"access_token": "", "refresh_token": ""}
    mocked_interactive_auth.assert_not_called()


@pytest.mark.parametrize(
    "settings",
    [
        {
            "glow_hps_username": "",
            "glow_hps_password": "",
        },
    ],
    ids=["username-password"],
    indirect=["settings"],
)
@pytest.mark.parametrize(
    "hps_server_url",
    ["https://testhost:12345/test", "https://testhost/test"],
    ids=["port", "no-port"],
)
def test_hps_custom_params_used_on_interactive_auth(
    settings: Settings,
    client: TestClient,
    mocker: pytest_mock.MockerFixture,
    hps_server_url: str,
):
    assert not settings.glow_hps_username
    assert not settings.glow_hps_password
    mocked_interactive_auth = mocker.patch.object(
        HpsInteractiveAuthenticator,
        "acquire_token",
        return_value=("fake_token", "fake_refresh"),
    )
    response = client.get(
        "/desktop:hps-auth-info",
        params={
            "hps_server_url": hps_server_url,
            "client_id": "test_client",
        },
    )
    assert response.status_code == 200
    mocked_interactive_auth.assert_called_once_with(
        hps_server_url=hps_server_url,
        client_id="test_client",
    )


@pytest.mark.parametrize(
    "settings",
    [
        {
            "glow_hps_host": None,
            "glow_hps_port": None,
            "glow_hps_username": None,
            "glow_hps_password": None,
        },
    ],
    ids=["debug"],
    indirect=["settings"],
)
def test_get_hps_auth_info_without_url_or_env_config_raises_error(settings: Settings, client: TestClient):
    # GIVEN: GLOW API configured with instance system without HPS env vars
    assert not settings.computed_glow_hps_host
    assert settings.computed_glow_hps_port is None
    assert not settings.glow_hps_username
    assert not settings.glow_hps_password
    # WHEN: asking for tokens (explicitly setting params to None for readability)
    response = client.get("/desktop:hps-auth-info", params=None)
    # THEN: an error is raised because host and/or port are unconfigured
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "HPS system unconfigured."


@pytest.mark.parametrize(
    "settings",
    [
        {
            "glow_hps_username": "",
            "glow_hps_password": "",
        },
    ],
    ids=["username-password"],
    indirect=["settings"],
)
def test_hps_server_multi_url_used_on_interactive_auth(
    settings: Settings,
    client: TestClient,
    mocker: pytest_mock.MockerFixture,
):
    assert not settings.glow_hps_username
    assert not settings.glow_hps_password

    def mocked_acquire_token(
        hps_server_url: str,
        client_id: str,
    ):
        return (
            ("first_access", "first_refresh") if "first_host" in hps_server_url else ("second_access", "second_refresh")
        )

    mocker.patch.object(
        HpsInteractiveAuthenticator,
        "acquire_token",
        mocked_acquire_token,
    )
    response = client.get("/desktop:hps-auth-info", params={"hps_server_url": "http://first_host:12345"})
    assert response.status_code == 200
    assert response.json() == {"access_token": "first_access", "refresh_token": "first_refresh"}

    response = client.get("/desktop:hps-auth-info", params={"hps_server_url": "http://second_host:12345"})
    assert response.status_code == 200
    assert response.json() == {"access_token": "second_access", "refresh_token": "second_refresh"}


@pytest.mark.parametrize(
    "settings",
    [
        {
            "glow_hps_host": "fake_host",
            "glow_hps_port": 8888,
            "glow_hps_username": None,
            "glow_hps_password": None,
        },
    ],
    ids=["token_refresh"],
    indirect=["settings"],
)
def test_get_hps_auth_info_token_refresh_on_expired_token(
    settings: Settings,
    client: TestClient,
    mocker: pytest_mock.MockerFixture,
):
    assert not settings.glow_hps_username
    assert not settings.glow_hps_password

    # First call to acquire tokens and cache them
    mocker.patch.object(
        HpsInteractiveAuthenticator,
        "acquire_token",
        return_value=("initial_token", "initial_refresh"),
    )
    response = client.get("/desktop:hps-auth-info")
    assert response.status_code == 200
    assert response.json() == {"access_token": "initial_token", "refresh_token": "initial_refresh"}

    # WHEN: token is expired and needs refresh
    mocked_check_token_validity = mocker.patch.object(
        HpsInteractiveAuthenticator,
        "check_token_validity",
        return_value=False,
    )
    mocked_refresh_token = mocker.patch.object(
        HpsInteractiveAuthenticator,
        "refresh_token",
        return_value=("refreshed_token", "refreshed_refresh"),
    )

    response = client.get("/desktop:hps-auth-info")

    # THEN: token is refreshed and new tokens are returned
    assert response.status_code == 200
    assert response.json() == {"access_token": "refreshed_token", "refresh_token": "refreshed_refresh"}
    mocked_check_token_validity.assert_called_once_with("initial_token")
    mocked_refresh_token.assert_called_once_with(
        hps_server_url="https://fake_host:8888/hps",
        client_id="rep-jms-web",
        refresh_token="initial_refresh",
    )


@pytest.mark.parametrize(
    "settings",
    [
        {
            "glow_hps_host": "fake_host",
            "glow_hps_port": 8888,
            "glow_hps_username": None,
            "glow_hps_password": None,
        },
    ],
    ids=["token_refresh_failure"],
    indirect=["settings"],
)
def test_get_hps_auth_info_token_refresh_failure_fallback_to_acquire(
    settings: Settings,
    client: TestClient,
    mocker: pytest_mock.MockerFixture,
):
    assert not settings.glow_hps_username
    assert not settings.glow_hps_password

    # First call to acquire tokens and cache them
    mocker.patch.object(
        HpsInteractiveAuthenticator,
        "acquire_token",
        return_value=("initial_token", "initial_refresh"),
    )
    response = client.get("/desktop:hps-auth-info")
    assert response.status_code == 200

    # Reset the mock to track subsequent calls and set new return value
    mocked_acquire_token = mocker.patch.object(
        HpsInteractiveAuthenticator,
        "acquire_token",
        return_value=("fallback_token", "fallback_refresh"),
    )

    # WHEN: token is expired and refresh fails
    mocker.patch.object(
        HpsInteractiveAuthenticator,
        "check_token_validity",
        return_value=False,
    )
    mocked_refresh_token = mocker.patch.object(
        HpsInteractiveAuthenticator,
        "refresh_token",
        side_effect=Exception("Refresh token expired or invalid"),
    )

    response = client.get("/desktop:hps-auth-info")

    # THEN: fallback to acquire_token and new tokens are returned
    assert response.status_code == 200
    assert response.json() == {"access_token": "fallback_token", "refresh_token": "fallback_refresh"}
    mocked_refresh_token.assert_called_once()
    mocked_acquire_token.assert_called_once_with(hps_server_url="https://fake_host:8888/hps", client_id="rep-jms-web")


@pytest.mark.parametrize(
    "settings",
    [
        {
            "glow_hps_username": None,
            "glow_hps_password": None,
        },
    ],
    ids=["custom_params_refresh"],
    indirect=["settings"],
)
def test_hps_custom_params_used_on_token_refresh(
    settings: Settings,
    client: TestClient,
    mocker: pytest_mock.MockerFixture,
):
    assert not settings.glow_hps_username
    assert not settings.glow_hps_password

    # First call with custom params to acquire tokens and cache them
    mocker.patch.object(
        HpsInteractiveAuthenticator,
        "acquire_token",
        return_value=("initial_token", "initial_refresh"),
    )
    hps_server_url = "https://custom_host:9999/custom"
    response = client.get(
        "/desktop:hps-auth-info",
        params={
            "hps_server_url": hps_server_url,
            "client_id": "custom_client",
        },
    )
    assert response.status_code == 200

    # WHEN: token is expired and needs refresh with custom params
    mocker.patch.object(
        HpsInteractiveAuthenticator,
        "check_token_validity",
        return_value=False,  # Token is expired
    )
    mocked_refresh_token = mocker.patch.object(
        HpsInteractiveAuthenticator,
        "refresh_token",
        return_value=("refreshed_token", "refreshed_refresh"),
    )

    response = client.get(
        "/desktop:hps-auth-info",
        params={
            "hps_server_url": hps_server_url,
            "client_id": "custom_client",
        },
    )

    # THEN: refresh_token is called with custom parameters
    assert response.status_code == 200
    assert response.json() == {"access_token": "refreshed_token", "refresh_token": "refreshed_refresh"}
    mocked_refresh_token.assert_called_once_with(
        hps_server_url=hps_server_url,
        client_id="custom_client",
        refresh_token="initial_refresh",
    )
