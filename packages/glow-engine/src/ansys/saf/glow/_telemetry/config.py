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

from copy import deepcopy
from functools import cache
from io import StringIO
from pathlib import Path
from string import Template
from typing import Any

import yaml

from ansys.saf.glow._config.const import GLOW_METHOD_RUNNER_SERVICE_NAME, GLOW_UI_SERVICE_NAME
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._utilities.random_identifier import get_random_identifier

LOGGING_DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "streamFormat": {
            "format": "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s]- %(message)s",  # noqa: E501
        },
    },
    "handlers": {
        "stream": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "streamFormat",
            "stream": "ext://sys.stderr",
        },
    },
    "root": {"level": "WARNING", "handlers": ["stream"]},
    "loggers": {
        "ansys": {
            "level": "INFO",
            "handlers": ["stream"],
            "propagate": False,  # so messages are not handled twice, also by the root logger.
        },
        "uvicorn": {"level": "WARNING", "handlers": ["stream"], "propagate": False, "qualname": "uvicorn"},
    },
}


@cache
def _get_process_identifier():
    return get_random_identifier()


def _parse_config_from_file(logging_config_path: Path, settings: Settings, method_name: str = "") -> Any:
    variables = {
        "process_identifier": _get_process_identifier(),
        # use as as_posix to replace \ with / so that the yaml safe load parses the string correctly
        "glow_appdata_directory": str(settings.glow_appdata_directory().as_posix()),
        "glow_solution_directory": str(settings.computed_solution_appdata_directory.as_posix()),
        "solution_name": settings.computed_solution_name,
        "method_name": method_name,
    }
    config_file_content = logging_config_path.read_text()
    subbed_string = Template(config_file_content).substitute(variables)
    return yaml.safe_load(StringIO(subbed_string))


def get_log_file_paths_from_config(config: Any) -> list[str]:
    log_files: list[str] = []
    if isinstance(config, dict):
        for handler in config.get("handlers", {}).values():  # type: ignore
            if isinstance(handler, dict):
                # standard name parameter for files in all file-based logging handlers
                # see https://docs.python.org/3/library/logging.handlers.html
                filename = handler.get("filename")  # type: ignore
                if isinstance(filename, str):
                    log_files.append(filename)
    return log_files


def get_log_config_file(container_name: str, settings: Settings) -> Path | None:
    if container_name == GLOW_UI_SERVICE_NAME:
        return settings.glow_ui_log_config
    elif container_name == GLOW_METHOD_RUNNER_SERVICE_NAME:
        return settings.glow_method_log_config
    else:
        # TODO: Review if it can be deleted
        # Default value for any other container name.
        # Important for retro-compatibility with SAF Desktop,
        # where the "Orchestrator" is a container that is configured with GLOW's Instrumentor
        # and uses glow_log_config to pass the logging config path.
        return settings.glow_log_config


def create_logging_config(container_name: str, settings: Settings, method_name: str = "") -> Any:
    config = None
    logging_config_path = get_log_config_file(container_name, settings)
    if logging_config_path:
        config = _parse_config_from_file(logging_config_path, settings, method_name)

    log_file_paths = get_log_file_paths_from_config(config)
    for log_file_path in log_file_paths:
        # TODO: validate filename?
        Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)

    override_level = (
        "DEBUG" if settings.glow_debug else settings.glow_logging_level.value if settings.glow_logging_level else None
    )
    if override_level:
        # Let's override all log level, inside loggers and handlers
        # if there wasn't a config supplied using logging_config_path, overwrite default config.
        if not config:
            config = deepcopy(LOGGING_DEFAULT_CONFIG)
        if "loggers" not in config:
            # compatibility with old configurations that only had root as logger
            # For new configs, even if root is left at WARNING, since its handler is raised to ERROR+,
            # messages will be filtered for non-ansys loggers too.
            config["root"]["level"] = override_level
        else:
            for logger_conf in config["loggers"].values():
                logger_conf["level"] = override_level
        for handler in config["handlers"].values():
            handler["level"] = override_level

    return config
