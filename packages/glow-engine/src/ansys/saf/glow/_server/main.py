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
import uvicorn

from ansys.saf.glow._config.const import DEFAULT_DEBUG_PORT, GLOW_API_SERVICE_NAME
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._telemetry.instrumentor import Instrumentor
from ansys.saf.glow._utilities.ip_utilities import next_free_port

logger = logging.getLogger(__name__)


def run_api_server(env_file: Path | None = None) -> None:
    env_file = env_file or Path.cwd() / ".env"
    if env_file.is_file():
        # load it in case it contains env vars not included in Settings (e.g., GLOW_PRODUCT_HOST)
        load_dotenv(dotenv_path=env_file.resolve())

    # we pass it to Settings too to avoid collision in case env_file is used at the same time that a local .env exists
    settings = Settings(_env_file=env_file, _env_file_encoding="utf-8")  # type: ignore
    Instrumentor.instrumentalize_process(GLOW_API_SERVICE_NAME, settings)

    if env_file.is_file():
        # just to be sure that the log msg is done after process is instrumentalized
        logger.info(f"Environment variables loaded from {env_file.absolute()}")

    if bool(settings.glow_debug) and settings.glow_debug_api_port != -1:
        if settings.glow_debug_api_port is None:
            debug_api_port = next_free_port(DEFAULT_DEBUG_PORT)
        else:
            debug_api_port = settings.glow_debug_api_port
        logger.info(f"#### API server listening for debug on port: {debug_api_port} ####")
        debugpy.listen(debug_api_port)

    hot_reload_enabled: bool = bool(settings.glow_debug) and bool(settings.glow_api_hot_reload)
    if hot_reload_enabled:
        logger.info("#### Uvicorn hot reload enabled. ####")

    uvicorn.run(  # pyright: ignore[reportUnknownMemberType]
        "ansys.saf.glow.api:app",
        host=settings.glow_api_host,
        port=settings.glow_api_port,
        reload=hot_reload_enabled,
        env_file=env_file,
        # Passing None to log_config to disable the default logging config from uvicorn and let glow configuring it.
        log_config=None,
        workers=settings.computed_number_of_workers,
        reload_dirs=settings.computed_api_hot_reload_monitoring_dir.as_posix(),
    )
