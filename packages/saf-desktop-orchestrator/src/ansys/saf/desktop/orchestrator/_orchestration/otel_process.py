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
import os
from pathlib import Path
import platform

from ansys.saf.desktop.orchestrator._config.schema import DEFAULT_SAF_DESKTOP_HEALTH_CHECK_TIMEOUT, LOCALHOST_IP
from ansys.saf.desktop.orchestrator._orchestration.process import ServiceProcess
from ansys.saf.desktop.orchestrator._utilities.ip_utilities import get_random_free_port

logger = logging.getLogger(__name__)


class OtelProcess(ServiceProcess):
    def __init__(
        self,
        dashboard_port: int | None = None,
        otlp_url: str = "",
        health_check_timeout: int = DEFAULT_SAF_DESKTOP_HEALTH_CHECK_TIMEOUT,
        api_key: str = "",
    ) -> None:
        # Importing Aspire here to make it an optional dependency. It needs to be installed separately.
        try:
            import ansys.saf.aspire  # pyright: ignore[reportMissingTypeStubs, reportMissingImports]
        except ModuleNotFoundError as ex:
            raise ModuleNotFoundError(
                "The package 'ansys-saf-aspire' is not installed or could not be found.",
            ) from ex

        dashboard_url = f"http://{LOCALHOST_IP}:{dashboard_port}"
        binary_name = "Aspire.Dashboard"
        if platform.system() == "Windows":
            binary_name += ".exe"
        aspire_path = Path(ansys.saf.aspire.__path__[0]) / binary_name  # type: ignore
        cwd = aspire_path.parent
        args = [aspire_path.as_posix()]
        otel_env = os.environ.copy()
        otel_env["ASPNETCORE_URLS"] = dashboard_url
        otel_env["DASHBOARD__OTLP__AUTHMODE"] = "ApiKey"
        otel_env["DASHBOARD__OTLP__PRIMARYAPIKEY"] = api_key
        otel_env["DOTNET_DASHBOARD_OTLP_ENDPOINT_URL"] = f"http://{LOCALHOST_IP}:{get_random_free_port()}"
        otel_env["DOTNET_DASHBOARD_OTLP_HTTP_ENDPOINT_URL"] = otlp_url
        super().__init__(
            args,
            port=dashboard_port,
            ip=LOCALHOST_IP,
            health_route="/structuredLogs",
            health_check_timeout=health_check_timeout,
            env=otel_env,
            cwd=cwd,
        )
