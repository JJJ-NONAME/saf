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

from io import BytesIO
import json
from pathlib import Path
from typing import Any
import zipfile

from fastapi.testclient import TestClient


def get_project(client: TestClient, project_name: str) -> Any:
    exported_project = client.get(f"{project_name}:export").content
    with zipfile.ZipFile(BytesIO(exported_project), "r") as archive:
        sap_file = [f for f in archive.namelist() if f.endswith(".sap")][0]
        return json.loads(archive.read(sap_file))


def _do_upgrade_or_import_project(
    old_client: TestClient,
    new_client: TestClient,
    source: str,
    project_name: str,
    tmp_path: Path,
):
    if source == "db":
        return new_client.post(f"/{project_name}:upgrade")
    else:
        response = old_client.get(f"{project_name}:export")
        response.raise_for_status()
        safx_path = tmp_path / "project.safx"
        safx_path.write_bytes(response.content)

        try:
            with safx_path.open("rb") as f:
                response = new_client.post(
                    "/projects:import",
                    files={"safx_file": f},
                    data={"display_name": "Unused Display Name"},
                )
        finally:
            safx_path.unlink()

        return response


def assert_error_from_upgrade_or_import(
    old_client: TestClient,
    new_client: TestClient,
    source: str,
    project_name: str,
    tmp_path: Path,
    expected_error_text: str,
):
    response = _do_upgrade_or_import_project(old_client, new_client, source, project_name, tmp_path)
    assert response.status_code == 422
    assert expected_error_text in response.text, response.text


def upgrade_or_import_project(
    old_client: TestClient,
    new_client: TestClient,
    source: str,
    project_name: str,
    tmp_path: Path,
):
    response = _do_upgrade_or_import_project(old_client, new_client, source, project_name, tmp_path)
    assert response.status_code == 200, f"{response.status_code=} {response.text=}"
    return response.json()
