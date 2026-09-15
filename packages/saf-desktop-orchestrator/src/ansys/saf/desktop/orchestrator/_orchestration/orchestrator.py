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

import concurrent.futures
import logging

from ansys.saf.desktop.orchestrator._orchestration.process import ServiceProcess
from ansys.saf.desktop.orchestrator._orchestration.service_info import ServiceInfo
from ansys.saf.desktop.orchestrator._utilities.ip_utilities import resolve_ip

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self):
        """A simple orchestrator to manage services."""
        self._services_info: list[ServiceInfo] = []
        self._health_checks: dict[str, concurrent.futures.Future[None]] = {}
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    def stop(self) -> None:
        """Stop all the services that have been launched by the orchestrator."""
        self._executor.shutdown(cancel_futures=True)
        for service_info in self._services_info:
            service_info.process.stop()

    def try_get_service(self, service_type: str) -> ServiceInfo | None:
        services = [service for service in self._services_info if service.service_type == service_type]
        if len(services) == 0:
            return None

        if len(services) != 1:
            raise RuntimeError("more than one matching service")

        return services[0]

    def get_service(self, service_type: str) -> ServiceInfo:
        service = self.try_get_service(service_type)
        if service is None:
            raise RuntimeError("no matching services")
        return service

    def start_service(
        self,
        service_type: str,
        service: ServiceProcess,
        allow_window: bool = True,
        additional_args: list[str] | None = None,
    ) -> ServiceInfo:
        """Start the given process service."""
        service.run(additional_args=additional_args, allow_window=allow_window)
        address = resolve_ip(service.url)
        service_info = ServiceInfo(service_type=service_type, process=service, address=address)
        self._services_info.append(service_info)
        self._health_checks[service_type] = self._executor.submit(service.wait_for_healthy)
        return service_info

    def healthy(self, service_types: list[str] | None = None):
        service_types = service_types if service_types is not None else list(self._health_checks.keys())
        for service_type in service_types:
            if service_type not in self._health_checks:
                raise RuntimeError("no matching services")
            # Exception in health check will be reraised by result()
            self._health_checks[service_type].result()
