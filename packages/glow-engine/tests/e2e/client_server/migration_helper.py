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

from pathlib import Path
from typing import TypeVar

from fastapi import status

from ansys.saf.glow.client import Client
from ansys.saf.glow.solution import Solution

T = TypeVar("T", bound=Solution)


def upgrade_or_import_project(
    source: str,
    glow_client: Client[T],
    base_api_url: str,
    project_id: str,
    safx_path: Path,
    expected_status_code: int = 200,
    expected_error_message: str = "",
):
    if source == "db":
        response = glow_client.http_client.post(
            f"{base_api_url}/projects/{project_id}:upgrade",
        )
    else:
        with safx_path.open("rb") as f:
            response = glow_client.http_client.post(
                f"{base_api_url}/projects:import",
                files={"safx_file": f},
                data={"display_name": "My Solution"},
            )
    assert response.status_code == expected_status_code
    if response.status_code != status.HTTP_200_OK:
        assert expected_error_message in response.text
    else:
        project_info = response.json()
        return project_info
