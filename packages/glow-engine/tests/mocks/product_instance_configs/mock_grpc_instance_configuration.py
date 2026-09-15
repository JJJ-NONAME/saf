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

import sys

from ansys.saf.glow.solution.products.config import (
    IProductInstanceConfiguration,
    IProductInstanceVersionConfiguration,
    ISoftware,
    ServiceType,
    Software,
)


class MockInstanceVersionConfiguration(IProductInstanceVersionConfiguration):
    def __init__(self, version: str) -> None:
        self._version = version

    @property
    def service_name(self) -> str:
        return "grpc"

    @property
    def execution_command(self) -> str:
        return f"${{EXECUTABLE}} -m tests.mocks.mock_products.grpc_server ${{PORT}} --version {self._version}"

    @property
    def exe_path_for_pim(self) -> str:
        return sys.executable

    @property
    def environment(self) -> dict[str, str]:
        return {}

    @property
    def software_requirements(self) -> list[ISoftware]:
        return [Software(name="Python", version=f"{sys.version_info.major}.{sys.version_info.minor}")]

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.GRPC


class MockInstanceConfiguration(IProductInstanceConfiguration):
    @property
    def product_name(self) -> str:
        return "custom-grpc-product"

    @property
    def versions(self) -> list[str]:
        return ["1", "2", "222"]

    def get_version_configuration(self, version: str) -> IProductInstanceVersionConfiguration:
        return MockInstanceVersionConfiguration(version)


class MockGRPCCustomRouteInstanceVersionConfiguration(MockInstanceVersionConfiguration):
    @property
    def health_route(self) -> str:
        return "my_custom_health_route"


class MockGRPCCustomRouteInstanceConfiguration(IProductInstanceConfiguration):
    @property
    def product_name(self) -> str:
        return "custom-grpc-product-custom-route"

    @property
    def versions(self) -> list[str]:
        return ["1", "2", "222"]

    def get_version_configuration(self, version: str) -> IProductInstanceVersionConfiguration:
        return MockGRPCCustomRouteInstanceVersionConfiguration(version)


class MockGRPCCustomHostInstanceVersionConfiguration(MockInstanceVersionConfiguration):
    @property
    def execution_command(self) -> str:
        return f"${{EXECUTABLE}} -m tests.mocks.mock_products.grpc_server ${{PORT}} --host ${{HOST}} --version {self._version}"  # noqa: E501


class MockGRPCCustomHostInstanceConfiguration(IProductInstanceConfiguration):
    @property
    def product_name(self) -> str:
        return "custom-grpc-product-custom-host"

    @property
    def versions(self) -> list[str]:
        return ["1", "2", "222"]

    def get_version_configuration(self, version: str) -> IProductInstanceVersionConfiguration:
        return MockGRPCCustomHostInstanceVersionConfiguration(version)


class MockSecureGRPCInstanceVersionConfiguration(MockInstanceVersionConfiguration):
    @property
    def execution_command(self) -> str:
        return f"${{EXECUTABLE}} -m tests.mocks.mock_products.grpc_secure_server ${{PORT}} --host ${{HOST}} --version {self._version}"  # noqa: E501

    @property
    def enable_secure_flags(self) -> bool:
        return True


class MockSecureGRPCInstanceConfiguration(IProductInstanceConfiguration):
    @property
    def product_name(self) -> str:
        return "custom-grpc-product-secure"

    @property
    def versions(self) -> list[str]:
        return ["1", "2", "222"]

    def get_version_configuration(self, version: str) -> IProductInstanceVersionConfiguration:
        return MockSecureGRPCInstanceVersionConfiguration(version)


class MockSecureGRPCCustomInstanceVersionConfiguration(MockInstanceVersionConfiguration):
    # In comparison with MockSecureGRPCInstanceVersionConfiguration, this config is testing:
    # - custom values for all secure flag properties
    # - HOST, PORT and UDS_DIR in env vars
    # - custom UDS_ID.
    @property
    def execution_command(self) -> str:
        return f"${{EXECUTABLE}} -m tests.mocks.mock_products.grpc_secure_server_customized --version {self._version}"

    @property
    def enable_secure_flags(self) -> bool:
        return True

    @property
    def windows_local_secure_flags(self) -> str:
        return "-transport wnua"

    @property
    def linux_local_secure_flags(self) -> str:
        return "-transport uds"

    @property
    def remote_secure_flags(self) -> str:
        return "-transport mtls"

    @property
    def insecure_flags(self) -> str:
        return "-transport insecure"

    @property
    def environment(self) -> dict[str, str]:
        return {
            "MOCK_UDS_DIR": "${UDS_DIR}",
            "MOCK_HOST": "${HOST}",
            "MOCK_PORT": "${PORT}",
        }

    @property
    def linux_uds_id(self) -> str:
        return "${PORT}"


class MockSecureGRPCCustomInstanceConfiguration(IProductInstanceConfiguration):
    @property
    def product_name(self) -> str:
        return "custom-grpc-product-secure-2"

    @property
    def versions(self) -> list[str]:
        return ["1", "2", "222"]

    def get_version_configuration(self, version: str) -> IProductInstanceVersionConfiguration:
        return MockSecureGRPCCustomInstanceVersionConfiguration(version)


class MockSecureGRPCMtlsInstanceVersionConfiguration(MockInstanceVersionConfiguration):
    # In comparison with MockSecureGRPCInstanceVersionConfiguration, this config is testing:
    # that ${CERTS_DIR} is properly interpolated
    @property
    def execution_command(self) -> str:
        return f"${{EXECUTABLE}} -m tests.mocks.mock_products.grpc_secure_server ${{PORT}} --host ${{HOST}} --version {self._version}"  # noqa: E501

    @property
    def enable_secure_flags(self) -> bool:
        return True

    @property
    def windows_local_secure_flags(self) -> str:
        # unnecessary certs-dir, but we want to check that it is properly
        # interpolated
        return "--transport-mode=WNUA --certs-dir=${CERTS_DIR}"

    @property
    def linux_local_secure_flags(self) -> str:
        # mechanical-like config
        return "--transport-mode=MTLS --certs-dir=${CERTS_DIR}"

    @property
    def remote_secure_flags(self) -> str:
        return "--transport-mode=MTLS --certs-dir=${CERTS_DIR}"

    @property
    def insecure_flags(self) -> str:
        return "--transport-mode=insecure"


class MockSecureGRPCMtlsInstanceConfiguration(IProductInstanceConfiguration):
    @property
    def product_name(self) -> str:
        return "custom-grpc-product-secure-mtls"

    @property
    def versions(self) -> list[str]:
        return ["1", "2", "222"]

    def get_version_configuration(self, version: str) -> IProductInstanceVersionConfiguration:
        return MockSecureGRPCMtlsInstanceVersionConfiguration(version)
