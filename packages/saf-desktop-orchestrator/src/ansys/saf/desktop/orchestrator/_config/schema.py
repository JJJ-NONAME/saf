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
from pathlib import Path
import platform

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# env vars to configure SAF Desktop, should match the names of the fields of Settings
SAF_DESKTOP_SOLUTION_NAME = "SAF_DESKTOP_SOLUTION_NAME"
PORTAL_API_VERSION = "PORTAL_API_VERSION"
SAF_DESKTOP_TEST_ENV = "SAF_DESKTOP_TEST_ENV"
SAF_DEFINITION_PATH = "SAF_DEFINITION_PATH"
SAF_DESKTOP_HEALTH_CHECK_TIMEOUT = "SAF_DESKTOP_HEALTH_CHECK_TIMEOUT"
SAF_DESKTOP_LOG_TO_FILES = "SAF_DESKTOP_LOG_TO_FILES"
SAF_DESKTOP_PROJECTS_DASHBOARD_PATH = "SAF_DESKTOP_PROJECTS_DASHBOARD_PATH"

# env vars of other components that are used to configure them
PORTAL_UI_PORT = "PORTAL_UI_PORT"
PORTAL_UI_HOST = "PORTAL_UI_HOST"
GLOW_API_PORT = "GLOW_API_PORT"
GLOW_API_HOST = "GLOW_API_HOST"
GLOW_API_URL = "GLOW_API_URL"
GLOW_UI_PORT = "GLOW_UI_PORT"
GLOW_UI_HOST = "GLOW_UI_HOST"
GLOW_CORS_ORIGINS = "GLOW_CORS_ORIGINS"
GLOW_SOLUTION_DEFINITION = "GLOW_SOLUTION_DEFINITION"
GLOW_PORTAL_URL = "GLOW_PORTAL_URL"
GLOW_DEPLOYMENT = "GLOW_DEPLOYMENT"
GLOW_WS_EVENTS_ADDR = "GLOW_WS_EVENTS_ADDR"
GLOW_PRODUCT_INSTANCE_SYSTEM = "GLOW_PRODUCT_INSTANCE_SYSTEM"
GLOW_PRODUCT_INSTANCE_SYSTEM_PORT = "GLOW_PRODUCT_INSTANCE_SYSTEM_PORT"
GLOW_PRODUCT_INSTANCE_SYSTEM_HOST = "GLOW_PRODUCT_INSTANCE_SYSTEM_HOST"
GLOW_ENABLE_AUTOMATIC_PROJECT_MIGRATION = "GLOW_ENABLE_AUTOMATIC_PROJECT_MIGRATION"
OTEL_DASHBOARD_PORT = "OTEL_DASHBOARD_PORT"
OTEL_EXPORTER_OTLP_ENDPOINT = "OTEL_EXPORTER_OTLP_ENDPOINT"
OTEL_EXPORTER_OTLP_HEADERS = "OTEL_EXPORTER_OTLP_HEADERS"
GLOW_LOG_CONFIG = "GLOW_LOG_CONFIG"
GLOW_UI_LOG_CONFIG = "GLOW_UI_LOG_CONFIG"
GLOW_METHOD_LOG_CONFIG = "GLOW_METHOD_LOG_CONFIG"

# other constants used across the codebase
DEFAULT_PORTAL_API_VERSION = "v1"
DEPLOYMENT_DESKTOP = "Desktop"
LOCALHOST_IP = "127.0.0.1"
PROJECTS_DASHBOARD_PATH = "/projects"
DEFAULT_SAF_DESKTOP_HEALTH_CHECK_TIMEOUT = 25
HEALTH_CHECK_INTERVAL = 0.25
PIM_LOCALHOSTS = ["localhost", "127.0.0.1"]
# For finding instance configurations
PRODUCT_INSTANCE_CONFIGS_DIR_NAME = "product_instance_configs"
DEPRECATED_INSTANCE_CONFIGS_DIR_NAME = "pim_configurations"


class Settings(BaseSettings):
    """Configuration variables read from the environment.

    See: https://pydantic-docs.helpmanual.io/usage/settings/
    and https://fastapi.tiangolo.com/advanced/settings/#environment-variables
    """

    saf_desktop_solution_name: str = Field(
        description="The short camel case name for the solution that GLOW is running.",
    )
    portal_api_version: str = Field(
        default=DEFAULT_PORTAL_API_VERSION,
        description="The version of the Portal API.",
    )
    saf_desktop_test_env: bool = Field(default=False, description="Whether to enable test environment.")
    saf_definition_path: Path | None = Field(
        default=None,
        description="Path to the YAML file specifying the additional services required by the solution.",
    )
    saf_desktop_health_check_timeout: int = Field(
        default=DEFAULT_SAF_DESKTOP_HEALTH_CHECK_TIMEOUT,
        description="Timeout in seconds for health checks.",
    )
    saf_desktop_log_to_files: bool = Field(default=False, description="Whether to enable logging to files.")

    @field_validator("saf_desktop_log_to_files")
    @classmethod
    def validate_otel_log_compatibility(cls, value: bool) -> bool:
        if os.getenv(OTEL_EXPORTER_OTLP_ENDPOINT) and value:
            raise ValueError(
                f"The env var '{OTEL_EXPORTER_OTLP_ENDPOINT}' is defined "
                "but it is not compatible with logging to files.",
            )
        return value

    @property
    def computed_solution_appdata_directory(self) -> Path:
        return self._glow_appdata_directory() / self.saf_desktop_solution_name

    def _glow_appdata_directory(self) -> Path:
        if platform.system() == "Windows":
            directory = Path(os.environ["APPDATA"])
        else:
            directory = Path(os.getenv("XDG_DATA_HOME", "~/.local/share")).expanduser()

        return directory / "ansys" / "glow"
