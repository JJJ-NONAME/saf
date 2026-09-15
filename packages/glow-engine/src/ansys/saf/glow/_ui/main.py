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
from pathlib import Path

import debugpy  # pyright: ignore[reportMissingTypeStubs]
from dotenv import load_dotenv

from ansys.saf.glow._config.const import DEFAULT_UI_DEBUG_PORT, GLOW_UI_SERVICE_NAME
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._telemetry.instrumentor import Instrumentor
from ansys.saf.glow._ui.server import create_app
from ansys.saf.glow._utilities.ip_utilities import next_free_port

logger = logging.getLogger(__name__)


def run_ui_server(env_file: Path | None = None):
    env_file = env_file or Path.cwd() / ".env"
    if env_file.is_file():
        # load it in case it contains env vars not included in Settings (e.g., GLOW_API_URL, GLOW_WS_EVENTS_ADDR)
        load_dotenv(dotenv_path=env_file.resolve())

    # we pass it to Settings too to avoid collision in case env_file is used at the same time that a local .env exists
    settings = Settings(_env_file=env_file, _env_file_encoding="utf-8")  # type: ignore
    Instrumentor.instrumentalize_process(GLOW_UI_SERVICE_NAME, settings)

    if env_file.is_file():
        # just to be sure that the log msg is done after process is instrumentalized
        logger.info(f"Environment variables loaded from {env_file.absolute()}")

    if bool(settings.glow_ui_python_debugging) and settings.glow_debug_ui_port != -1:
        if settings.glow_debug_ui_port is None:
            debug_ui_port = next_free_port(DEFAULT_UI_DEBUG_PORT)
        else:
            debug_ui_port = settings.glow_debug_ui_port
        logger.info(f"#### UI server listening for debug on port: {debug_ui_port} ####")
        debugpy.listen(debug_ui_port)

    ui_app = create_app(settings)
    if hasattr(ui_app, "logger"):
        # not sure what's the appropriate here and we don't have tests for it.
        ui_app.logger = logging.getLogger()

    run_method = getattr(ui_app, "run", None)
    if run_method is None or not callable(run_method):
        raise RuntimeError("The 'app' object in the UI module does not have a callable 'run' method.")

    # The debug argument here is controlling whether Dash and Flask debug features
    # are present in the rendered UI. Those features are not compatible with debugpy.listen
    # so the debug feature is only enabled when GLOW system debugging is enabled and UI debugging is disabled.
    logger.info(f"Running GLOW UI server on http://{settings.glow_ui_host}:{settings.glow_ui_port}")
    run_method(
        host=settings.glow_ui_host,
        port=settings.glow_ui_port,
        debug=bool(settings.glow_debug) and not bool(settings.glow_ui_python_debugging),
    )
