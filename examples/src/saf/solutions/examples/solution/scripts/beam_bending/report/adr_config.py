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

# ©2026, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.
"""This module defines the configuration for setting up the ADR instance used to generate the beam bending report."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ADR_INSTALLATION_DIRECTORY = os.getenv("ADR_INSTALLATION_DIRECTORY")
GLOW_PROJECT_FILES_DIRECTORY = os.getenv("GLOW_PROJECT_FILES_DIRECTORY")

if ADR_INSTALLATION_DIRECTORY and GLOW_PROJECT_FILES_DIRECTORY:
    PROJECT_DIR = Path(GLOW_PROJECT_FILES_DIRECTORY)
    PATH_TO_ADR_DB = PROJECT_DIR.parent / "adr" / "report_data"
    PATH_TO_MEDIA = PATH_TO_ADR_DB / "media"
    PATH_TO_STATIC = PATH_TO_ADR_DB.parent / "static_assets"
else:
    PROJECT_DIR = None
    PATH_TO_ADR_DB = None
    PATH_TO_MEDIA = None
    PATH_TO_STATIC = None


def get_adr_config():
    """Load and validate ADR configuration when the reporting feature is used.

    Returns
    -------
    dict
        A dictionary containing:
        - 'ADR_INSTALLATION_DIRECTORY'
        - 'GLOW_PROJECT_FILES_DIRECTORY'
        - 'PROJECT_DIR'
        - 'PATH_TO_ADR_DB'
        - 'PATH_TO_MEDIA'
        - 'PATH_TO_STATIC'

    Raises
    ------
    RuntimeError
        If required environment variables are not set.
    """
    load_dotenv()

    adr_installation_directory = os.getenv("ADR_INSTALLATION_DIRECTORY")
    if not adr_installation_directory:
        raise RuntimeError("ADR_INSTALLATION_DIRECTORY environment variable is not set.")

    glow_project_files_directory = os.getenv("GLOW_PROJECT_FILES_DIRECTORY")
    if not glow_project_files_directory:
        raise RuntimeError("GLOW_PROJECT_FILES_DIRECTORY environment variable is not set.")

    project_dir = Path(glow_project_files_directory)
    path_to_adr_db = project_dir.parent / "adr" / "report_data"
    path_to_media = path_to_adr_db / "media"
    path_to_static = path_to_adr_db.parent / "static_assets"

    global ADR_INSTALLATION_DIRECTORY, GLOW_PROJECT_FILES_DIRECTORY
    global PROJECT_DIR, PATH_TO_ADR_DB, PATH_TO_MEDIA, PATH_TO_STATIC

    ADR_INSTALLATION_DIRECTORY = adr_installation_directory
    GLOW_PROJECT_FILES_DIRECTORY = glow_project_files_directory
    PROJECT_DIR = project_dir
    PATH_TO_ADR_DB = path_to_adr_db
    PATH_TO_MEDIA = path_to_media
    PATH_TO_STATIC = path_to_static

    return {
        "ADR_INSTALLATION_DIRECTORY": ADR_INSTALLATION_DIRECTORY,
        "GLOW_PROJECT_FILES_DIRECTORY": GLOW_PROJECT_FILES_DIRECTORY,
        "PROJECT_DIR": PROJECT_DIR,
        "PATH_TO_ADR_DB": PATH_TO_ADR_DB,
        "PATH_TO_MEDIA": PATH_TO_MEDIA,
        "PATH_TO_STATIC": PATH_TO_STATIC,
    }
