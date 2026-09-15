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

import logging

from ansys.saf.desktop.orchestrator._config.schema import DEFAULT_SAF_DESKTOP_HEALTH_CHECK_TIMEOUT
from ansys.saf.desktop.orchestrator._orchestration.process import ServiceProcess
from ansys.saf.desktop.orchestrator._utilities.ip_utilities import get_random_free_port

logger = logging.getLogger(__name__)


class AdditionalServiceProcess(ServiceProcess):
    def __init__(
        self,
        name: str,
        command_line_template: str,
        health_check: dict[str, str],
        health_check_timeout: int = DEFAULT_SAF_DESKTOP_HEALTH_CHECK_TIMEOUT,
        port: int | None = None,
        ip: str = "localhost",
    ) -> None:
        logger.debug(f"Starting additional service process for {name}...")
        self._name = name
        self._command_line_template = command_line_template
        self._health_check = health_check
        if port is None:
            port = get_random_free_port()
        self._port = port
        self._ip = ip
        self._command_line = self._command_line_template.replace("$PORT", str(port))
        args: list[str] = self._command_line.split()
        logger.debug(f"Command line for {name}: {args}")
        super().__init__(
            args,
            port=port,
            ip=ip,
            health_route=health_check.get("route", ""),
            health_check_timeout=health_check_timeout,
        )

    def wait_for_healthy(self):
        health_check_type = self._health_check["type"]
        if health_check_type == "HTTP":
            self._http_health_check(self._name)
        elif health_check_type == "TCP":
            self._tcp_health_check(self._name)
        elif health_check_type == "GRPC":
            self._grpc_health_check(self._name)
        else:
            logger.warning(f"Unknown health check type: {health_check_type}")
