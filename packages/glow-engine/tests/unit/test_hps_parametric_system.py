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

import pytest
import pytest_mock

from ansys.saf.glow._config.const import (
    GLOW_HPS_HOST,
    GLOW_HPS_PORT,
    GLOW_PRODUCT_INSTANCE_SYSTEM,
    GLOW_PRODUCT_INSTANCE_SYSTEM_HOST,
    GLOW_PRODUCT_INSTANCE_SYSTEM_PORT,
)
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._hps_auth.hps_authenticator import DesktopHpsAuthenticator
from ansys.saf.glow._hps_parametric_studies.system import HpsParametricStudySystem


@pytest.mark.parametrize(("host", "port"), [("localhost", None), (None, "8443"), ("localhost", "8443")])
def test_hps_system_get_hps_server_url(host: str | None, port: str | None, monkeypatch: pytest.MonkeyPatch):
    if host is None:
        monkeypatch.delenv(GLOW_HPS_HOST, raising=False)
    else:
        monkeypatch.setenv(GLOW_HPS_HOST, host)
    if port is None:
        monkeypatch.delenv(GLOW_HPS_PORT, raising=False)
    else:
        monkeypatch.setenv(GLOW_HPS_PORT, port)

    settings = Settings(glow_solution_definition="TEST")

    if not port:
        with pytest.raises(
            RuntimeError,
            match=(
                "No HPS system is configured. Set the environment variable "
                f"{GLOW_HPS_PORT} and optionally {GLOW_HPS_HOST}, "
                "or pass the hps_server_url argument when starting the job."
            ),
        ):
            HpsParametricStudySystem.get_hps_server_url(settings)
    elif not host:
        default_host = "127.0.0.1"
        assert HpsParametricStudySystem.get_hps_server_url(settings) == f"https://{default_host}:8443/hps"
    else:
        assert HpsParametricStudySystem.get_hps_server_url(settings) == f"https://{host}:{port}/hps"


def test_hps_system_get_hps_server_url_from_instance_env_vars(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv(GLOW_HPS_HOST, raising=False)
    monkeypatch.delenv(GLOW_HPS_PORT, raising=False)

    monkeypatch.setenv(GLOW_PRODUCT_INSTANCE_SYSTEM, "HPS")
    monkeypatch.setenv(GLOW_PRODUCT_INSTANCE_SYSTEM_HOST, "test_localhost")
    monkeypatch.setenv(GLOW_PRODUCT_INSTANCE_SYSTEM_PORT, "8443")

    settings = Settings(glow_solution_definition="TEST")

    assert HpsParametricStudySystem.get_hps_server_url(settings) == "https://test_localhost:8443/hps"


def test_hps_custom_params_ignores_host_and_port(
    monkeypatch: pytest.MonkeyPatch,
    mocker: pytest_mock.MockerFixture,
):
    monkeypatch.setenv(GLOW_HPS_HOST, "localhost")
    monkeypatch.setenv(GLOW_HPS_PORT, "1234")
    hps_authenticator = DesktopHpsAuthenticator("", client_id="rep-jms-web")
    get_hps_client_mock = mocker.patch.object(DesktopHpsAuthenticator, "get_hps_client")
    settings = Settings(glow_solution_definition="TEST")
    with HpsParametricStudySystem.get_hps_client(
        hps_authenticator=hps_authenticator,
        settings=settings,
        hps_server_url="test_url",
        client_id="test_client",
    ):
        ...
    get_hps_client_mock.assert_called_once_with(
        hps_server_url="test_url",
        client_id="test_client",
    )
