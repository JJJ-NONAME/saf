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
from ansys.saf.product_configuration.wrappers.versions import OPTISLANG_WRAPPER_VERSION

PRODUCT_NAME_SECURE = "optislang-wrapper-secure"

# Earlier versions are not supporting to pass the project_properties file path
# along with the project path when issuing the pyosl.open()
SUPPORTED_VERSIONS = ["241", "242", "251", "252", "261"]


def format_version(version: str) -> str:
    """Format the version to the expected format, for example 251 -> 2025 R1."""
    return f"20{version[0:2]} R{version[2]}"  # For example 251 -> 2025 R1


class OptislangWrapperInstanceVersionConfiguration(IProductInstanceVersionConfiguration):
    """Configuration class for a specific version of Ansys optiSLang."""

    def __init__(self, version: str) -> None:
        """
        Initialize the configuration class for optiSLang with the specified version.

        Parameters
        ----------
        version : str
            The version of the optiSLang instance.
        """
        self._version = version

    @property
    def service_name(self) -> str:
        """The name of the service associated with the optiSLang wrapper instance."""
        return ServiceType.HTTP.value

    @property
    def execution_command(self) -> str:
        """The command to launch optiSLang wrapper."""

        args = [
            "${EXECUTABLE}",
            "-m",
            "ansys.saf.product_configuration.wrappers.optislang",
            "--port",
            "${PORT}",
            "--host",
            "${HOST}",
        ]

        return " ".join(args)

    @property
    def environment(self) -> dict[str, str]:
        """Environment variables for the optiSLang wrapper instance."""
        return {}

    @property
    def software_requirements(self) -> list[ISoftware]:
        """Required software to run optiSLang wrapper in HPS."""
        return [
            Software(
                name="Ansys SAF Product Wrapper [optiSLang]",
                version=OPTISLANG_WRAPPER_VERSION,
            ),
            Software(
                name="Ansys optiSLang",
                version=format_version(self._version),
            ),
        ]

    @property
    def exe_path_for_pim(self) -> str:
        """The path to the python executable."""

        awp_root = f"AWP_ROOT{self._version}"

        if awp_root in os.environ:
            return sys.executable
        else:
            raise ValueError(f"Ansys version {self._version} cannot be found")

    @property
    def health_route(self) -> str | None:
        """The health route for the service."""
        return "/health"

    @property
    def service_type(self) -> ServiceType:
        """Service type use for the health check."""
        return ServiceType.HTTP

    @property
    def enable_secure_flags(self) -> bool:
        return True

    @property
    def linux_local_secure_flags(self) -> str:
        return "--transport-mode=UDS"

    @property
    def windows_local_secure_flags(self) -> str:
        return "--transport-mode=WNUA"

    @property
    def remote_secure_flags(self) -> str:
        return "--transport-mode=MTLS"

    @property
    def insecure_flags(self) -> str:
        return "--transport-mode=insecure"


class OptislangWrapperInstanceConfiguration(IProductInstanceConfiguration):
    """Configuration class for Ansys optiSLang wrapper."""

    @property
    def product_name(self) -> str:
        """Name used to identify the optiSLang wrapper in the product instance management system."""
        return PRODUCT_NAME_SECURE

    @property
    def versions(self) -> list[str]:
        """Supported optiSLang versions."""
        return SUPPORTED_VERSIONS

    def get_version_configuration(self, version: str) -> IProductInstanceVersionConfiguration:
        """Return the configuration of a product for a specific version."""
        return OptislangWrapperInstanceVersionConfiguration(version)
