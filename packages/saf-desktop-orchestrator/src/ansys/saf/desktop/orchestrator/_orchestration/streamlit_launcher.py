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
import sys

from ansys.saf.desktop.orchestrator._config.schema import (
    DEPLOYMENT_DESKTOP,
    GLOW_API_HOST,
    GLOW_API_PORT,
    GLOW_DEPLOYMENT,
    GLOW_UI_HOST,
    GLOW_WS_EVENTS_ADDR,
    LOCALHOST_IP,
    PORTAL_UI_PORT,
)
from ansys.saf.desktop.orchestrator._orchestration.launcher import Launcher

logger = logging.getLogger(__name__)


class StreamlitLauncher(Launcher):
    def start_solution_ui(self):
        """Starts the solution UI service using the Streamlit framework."""
        logger.info("Starting the solution UI service using the Streamlit framework")
        ui_host = os.getenv(GLOW_UI_HOST, LOCALHOST_IP)
        api_host = os.getenv(GLOW_API_HOST, LOCALHOST_IP)

        args = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            self._get_ui_app_path(),
            "--server.headless",
            "true",
            "--server.address",
            ui_host,
            "--server.port",
            str(self._ports["solution_ui"]),
        ]
        ui_env = os.environ.copy()
        ui_env[GLOW_DEPLOYMENT] = DEPLOYMENT_DESKTOP
        ui_env[GLOW_WS_EVENTS_ADDR] = f"ws://{api_host}:{self._ports['solution_api']}"
        ui_env[GLOW_API_PORT] = str(self._ports["solution_api"])
        if self._with_portal:
            ui_env[PORTAL_UI_PORT] = str(self._ports["portal_ui"])

        self._start_solution_ui_service(args, self._orchestrator, ui_env=ui_env)

    def get_project(
        self,
        project_name: str,
    ) -> str:
        return f"{self.get_service_info('UI').address}/?project_id={project_name}"

    def start_portal(self, additional_ui_params: str = "?project_id="):
        super().start_portal(additional_ui_params)

    def _get_ui_app_path(self) -> str:
        module_path = self._solution_module_name
        filesystem_path = module_path.replace(".", "/")
        absolute_path = Path(filesystem_path).resolve()

        solution_dir = absolute_path.parent

        if not solution_dir.is_dir():
            raise NotADirectoryError(f"Solution source directory not found at {solution_dir}")

        ui_app_path = solution_dir / "ui" / "app.py"

        if not ui_app_path.is_file():
            raise FileNotFoundError(f"Solution {solution_dir} has no entry point for streamlit run.")

        return str(ui_app_path)
