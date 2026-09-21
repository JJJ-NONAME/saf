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

from dataclasses import dataclass
from pathlib import Path
import sys

DEFAULT_ENCRIPTION_FILE = Path.cwd() / "obfuscate.txt"
DEFAULT_PYPROJECT_LOCATION = Path.cwd() / "pyproject.toml"
DEFAULT_PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
DEFAULT_UI_FRAMEWORK = "dash"

DESKTOP_ORCHESTRATOR_PACKAGE_NAME = "ansys-saf-desktop-orchestrator"
DESKTOP_ORCHESTRATOR_MODULE_NAME = "ansys.saf.desktop.orchestrator"


@dataclass
class InstallerConfig:
    display_console_window: bool = False
    encrypt: bool = False
    encryption_file: Path = DEFAULT_ENCRIPTION_FILE
    obfuscate: bool = False
    offline_package: bool = False
    pyproject_location: Path = DEFAULT_PYPROJECT_LOCATION
    exclude_python: bool = False
    python_version: str = DEFAULT_PYTHON_VERSION
    force_python_from_source: bool = False
    solution_entry_point: str = ""
    solution_ui_framework: str = DEFAULT_UI_FRAMEWORK
    use_glow: bool = False
    no_executable: bool = False
    github_token: str | None = None
    encryption_key: str | None = None
    env_file: Path | None = None
    executable_as_dir: bool = False


def validate_config(config: InstallerConfig) -> None:
    if config.encrypt:
        try:
            from ansys.translation_utilities.translator import c  # noqa: F401 # type: ignore
        except ImportError:
            print(
                "The ansys-translation-utilities package is required for encryption and is a private dependency. "
                "To use the --encrypt option, you must request "
                "access to this package from the SAF-SDK maintainers/team.",
                file=sys.stderr,
                flush=True,
            )
            sys.exit(1)
