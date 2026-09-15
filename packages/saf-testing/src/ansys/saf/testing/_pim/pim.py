# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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

from collections.abc import Callable
from pathlib import Path
import platform
import uuid

import pytest

from ansys.saf.testing._common.common import YieldFixture
from ansys.saf.testing._hps.process.hps_scaler_process import HpsScalerProcess
from ansys.saf.testing._pim.process.pim_process import PIM_LOCALHOSTS, PimProcess
from ansys.saf.testing._pytest.pytest import is_marker_within_collected_tests
from ansys.saf.testing._solution.const import TestProductInstanceSystemType


@pytest.fixture(scope="session")
def should_pim_be_launched(request: pytest.FixtureRequest) -> bool:
    return is_marker_within_collected_tests(request.session.items, "use_pim")


@pytest.fixture(scope="session")
def is_pim_enabled(request: pytest.FixtureRequest, should_pim_be_launched: bool) -> bool:
    return "not use_pim" not in request.config.option.markexpr and should_pim_be_launched


@pytest.fixture(scope="session")
def pim_host(request: pytest.FixtureRequest, docker_gateway_ip: str) -> str:
    return getattr(request, "param", docker_gateway_ip)


@pytest.fixture(scope="session")
def product_binding_host(request: pytest.FixtureRequest) -> str | None:
    return getattr(request, "param", None)


@pytest.fixture(scope="session")
def product_host(request: pytest.FixtureRequest) -> str | None:
    return getattr(request, "param", None)


@pytest.fixture(scope="session")
def enable_insecure_product(request: pytest.FixtureRequest) -> bool:
    return getattr(request, "param", False)


@pytest.fixture(scope="session")
def enable_insecure_pim(request: pytest.FixtureRequest) -> bool:
    return getattr(request, "param", False)


@pytest.fixture(scope="session")
def product_configs_dir(request: pytest.FixtureRequest) -> Path | None:
    if hasattr(request, "param"):
        return request.param
    default_path = Path("tests") / "mocks" / "product_instance_configs"
    if default_path.is_dir():
        return default_path
    return None


@pytest.fixture(scope="session")
def session_pim(
    is_pim_enabled: bool,
    instance_system_type: TestProductInstanceSystemType | None,
    tmp_path_factory: pytest.TempPathFactory,
    certificates_directory: Path,
    pim_host: str,
    enable_insecure_pim: bool,
    product_configs_dir: Path | None,
    product_binding_host: str | None,
) -> YieldFixture[PimProcess | None]:
    """Tests importing this fixture will have access to the session-scoped PIM process."""
    if not is_pim_enabled or instance_system_type != TestProductInstanceSystemType.PIM:
        yield
    else:
        if enable_insecure_pim:
            pim_proc = PimProcess(
                host=pim_host,
                insecure=True,
                product_configs_dir=product_configs_dir,
                product_binding_host=product_binding_host,
            )
        elif pim_host not in PIM_LOCALHOSTS:
            pim_proc = PimProcess(
                host=pim_host,
                certs_dir=certificates_directory.as_posix(),
                product_configs_dir=product_configs_dir,
                product_binding_host=product_binding_host,
            )
        elif platform.system() == "Windows":
            pim_proc = PimProcess(
                host=pim_host,
                product_configs_dir=product_configs_dir,
                product_binding_host=product_binding_host,
            )
        else:
            uds_dir = tmp_path_factory.mktemp("pim_uds")
            shortid = uuid.uuid4().hex[:8]
            # on linux, pim is using sockets stored for secure connection.
            # a unique id to allow multiple servers to be running on the same host.
            pim_proc = PimProcess(
                host=pim_host,
                uds_dir=uds_dir,
                uds_id=shortid,
                product_configs_dir=product_configs_dir,
                product_binding_host=product_binding_host,
            )

        try:
            pim_proc.start()
            yield pim_proc
        finally:
            pim_proc.stop()


@pytest.fixture(scope="session")
def pim_port(session_pim: PimProcess | None) -> int | None:
    return session_pim.port if session_pim else None


@pytest.fixture(scope="session")
def pim_socket_path(session_pim: PimProcess | None) -> Path | None:
    return session_pim.socket_path if session_pim else None


@pytest.fixture(scope="session")
def pim_uri(session_pim: PimProcess | None) -> str | None:
    return session_pim.uri if session_pim else None


@pytest.fixture(scope="session")
def restart_product_instance_system(
    session_pim: PimProcess | None,
    hps_scaler: HpsScalerProcess | None,
    instance_system_type: TestProductInstanceSystemType,
) -> Callable[[], None]:
    def _restart_method():
        if instance_system_type == TestProductInstanceSystemType.PIM:
            if not session_pim:
                pytest.fail("PIM is not running, can't restart.")
            session_pim.restart()
        elif instance_system_type == TestProductInstanceSystemType.HPS:
            if not hps_scaler:
                pytest.fail("HPS scaler is not running, can't restart.")
            hps_scaler.restart()
        else:
            pytest.fail("Unknown product instance system.")

    return _restart_method
