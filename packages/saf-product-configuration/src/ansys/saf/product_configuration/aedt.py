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

import os
import sys

from ansys.saf.product_configuration.interfaces import (
    IProductInstanceConfiguration,
    IProductInstanceVersionConfiguration,
    ISoftware,
    ServiceType,
    Software,
)
from ansys.saf.product_configuration.wrappers.versions import AEDT_WRAPPER_VERSION

PRODUCT_NAME = "aedt"
SERVICE_NAME = "http"


class AedtInstanceVersionConfiguration(IProductInstanceVersionConfiguration):
    """Configuration class for a specific version of Ansys Electronics Desktop (AEDT)."""

    def __init__(self, version: str) -> None:
        """
        Initialize the configuration class for AEDT with the specified version.

        Parameters
        ----------
        version : str
            The version of the AEDT instance.
        """
        self._version = version

    @property
    def service_name(self) -> str:
        """The name of the service associated with the AEDT instance."""
        return SERVICE_NAME

    @property
    def execution_command(self) -> str:
        """The command to launch AEDT."""
        return (
            "${EXECUTABLE} -m ansys.saf.product_configuration.wrappers.aedt --port ${PORT} --host ${HOST} "
            f"--version {self._version}"
        )

    @property
    def environment(self) -> dict[str, str]:
        """Environment variables for the AEDT instance."""
        return {}

    @property
    def software_requirements(self) -> list[ISoftware]:
        """Required software to run AEDT in HPS."""
        return [
            Software(
                name="Ansys SAF Product Wrapper [AEDT]",
                version=AEDT_WRAPPER_VERSION,
            ),
            Software(
                name="Ansys Electronics Desktop",
                version=f"20{self._version[0:2]} R{self._version[2:]}",
            ),
        ]

    @property
    def exe_path_for_pim(self) -> str:
        """Path to the AEDT executable."""
        for var_name, _ in os.environ.copy().items():
            aedt_var_name_prefix = "ANSYSEM_ROOT"
            if var_name.startswith(aedt_var_name_prefix):
                version_str = var_name[len(aedt_var_name_prefix) :]
                try:
                    int(version_str)
                except ValueError:
                    continue
                if version_str != self._version:
                    continue
                return sys.executable
        raise ValueError(f"Ansys Electronics Desktop version {self._version} cannot be found")

    @property
    def service_type(self) -> ServiceType:
        """Service type use for the health check."""
        return ServiceType.HTTP

    @property
    def enable_secure_flags(self) -> bool:
        return True

    @property
    def linux_local_secure_flags(self) -> str:
        """The command line arguments needed to configure the product instance for secure local communication on
        Linux."""
        return "--transport-mode=UDS"

    @property
    def windows_local_secure_flags(self) -> str:
        """The command line arguments needed to configure the product instance for secure local communication on
        Windows."""
        return "--transport-mode=WNUA"

    @property
    def remote_secure_flags(self) -> str:
        """The command line arguments needed to configure the product instance for secure remote communication."""
        # the option --certs-dir is not necessary for PyAEDT, but we add it to comply with the current HPS job script
        # implementation, which expects the secure flags to contain this option when the transport mode is mtls.
        return "--transport-mode=MTLS --certs-dir=${CERTS_DIR}"

    @property
    def insecure_flags(self) -> str:
        """The command line arguments needed to configure the product instance for insecure communication."""
        return "--transport-mode=insecure"


class AedtInstanceConfiguration(IProductInstanceConfiguration):
    """Configuration class for Ansys Electronics Desktop (AEDT)."""

    @property
    def product_name(self) -> str:
        """Name used to identify AEDT in the product instance management system."""
        return PRODUCT_NAME

    @property
    def versions(self) -> list[str]:
        """Supported AEDT versions."""
        return ["251", "252", "261"]

    def get_version_configuration(self, version: str) -> IProductInstanceVersionConfiguration:
        """Get configuration class for a particular version of AEDT."""
        return AedtInstanceVersionConfiguration(version)
