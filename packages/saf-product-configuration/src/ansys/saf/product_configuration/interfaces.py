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

from enum import Enum
from typing import Protocol


class ServiceType(Enum):
    """Define the type of API the service is using."""

    GRPC = "grpc"
    HTTP = "http"
    TCP = "tcp"


class ISoftware(Protocol):
    """Interface to define the software requirements."""

    name: str
    version: str | None


class Software:
    """Define the software requirements."""

    def __init__(self, name: str, version: str | None) -> None:
        self.name = name
        self.version = version


class IProductInstanceVersionConfiguration(Protocol):
    """Interface to configure a given version of a product instance."""

    @property
    def service_name(self) -> str:
        """This is the name of the service that is exposed by the instance management system (HPS or PIM)
        that identifies it from other services.

        It should be consistent with the name used in the PIM light amd PIM K8S configurations. Typically its something
        simple like ``grpc`` or ``http``.
        """
        ...

    @property
    def enable_secure_flags(self) -> bool:
        """Must be set to True for the product instance to use the secure communication command line arguments."""
        return False

    @property
    def linux_local_secure_flags(self) -> str:
        """The command line arguments needed to configure the product instance for secure local communication on
        Linux."""
        return (
            "--transport-mode=UDS --uds-dir=${UDS_DIR} --uds-id=${UDS_ID}"
            if self.service_type == ServiceType.GRPC
            else ""
        )

    @property
    def linux_uds_id(self) -> str:
        """Template for the uds_id, which is used to identify the socket file for UDS communication."""
        return "glow-${TASK_ID}"

    @property
    def windows_local_secure_flags(self) -> str:
        """The command line arguments needed to configure the product instance for secure local communication on
        Windows."""
        return "--transport-mode=WNUA" if self.service_type == ServiceType.GRPC else ""

    @property
    def remote_secure_flags(self) -> str:
        """The command line arguments needed to configure the product instance for secure remote communication."""
        return "--transport-mode=MTLS --certs-dir=${CERTS_DIR}" if self.service_type == ServiceType.GRPC else ""

    @property
    def insecure_flags(self) -> str:
        """The command line arguments needed to configure the product instance for insecure communication."""
        return "--transport-mode=insecure" if self.service_type == ServiceType.GRPC else ""

    @property
    def execution_command(self) -> str:
        """This is the command line used to start the product instance process.

        It can contain template variables in the form `${VAR}`. Supported variables are:

        - PORT: an integer which is the port that the process should expose its service on.
        - EXECUTABLE: the full path to the executable using either the first product listed
          in the `software_requirements` for HPS or the path specified by `exe_path_for_pim` for PIM.

        Note that for PIM this code runs just once during the YAML file generation that PIM later uses to
        launch the products. Thus, it's not feasible to generate and assign resources here for each launch.
        For instance, attempting to generate a temporary file/directory here and passing it to the command
        won't work as expected.
        """
        ...

    @property
    def environment(self) -> dict[str, str]:
        """The environment variables that will be set in the environment running the ``execution_command``."""
        ...

    @property
    def software_requirements(self) -> list[ISoftware]:
        """(For HPS only!) The software that must be installed on the node running the ``execution_command``.

        Find built-in products at ansys-rep-application-plugins.
        """
        ...

    @property
    def exe_path_for_pim(self) -> str:
        """(For PIM only!) The path to the product's executable."""
        ...

    @property
    def health_route(self) -> str | None:
        """The health route for the service. Typically '/health' for a HTTP service."""
        return None

    @property
    def service_type(self) -> ServiceType:
        """The type of service: grpc, http or tcp."""
        ...


class IProductInstanceConfiguration(Protocol):
    """Interface to configure a product instance.

    All products managed by the product instance system (HPS or PIM) must implement this interface.
    """

    @property
    def product_name(self) -> str:
        """This is the product name that is exposed by the product instance management system.

        It should be consistent with the name used in the PIM light and HPS configurations.
        """
        ...

    @property
    def versions(self) -> list[str]:
        """The set of versions that are supported.

        The last version is the default if no version is specified when an instance is created.
        """
        ...

    def get_version_configuration(self, version: str) -> IProductInstanceVersionConfiguration:
        """Return the configuration of a product for a specific version."""
        ...
