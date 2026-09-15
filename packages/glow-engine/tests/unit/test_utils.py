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

from pathlib import PurePath, PurePosixPath, PureWindowsPath
from typing import Any

import pytest

from ansys.saf.glow._crud.bdm_helper import update_opaque_identifier
from ansys.saf.glow._server.models import ProjectModel
from ansys.saf.glow._utilities.conversion import data_uri_to_bytes
from ansys.saf.glow._utilities.path_parser import parse_platform_specific_absolute_path
from tests.mocks.solutions.bdm_solution import BdmSolution


def test_data_uri_to_bytes_converts_as_expected():
    data_uri = "data:text/plain;base64,SGVsbG8gV29ybGQh"
    data = data_uri_to_bytes(data_uri)
    assert str(data, "utf-8") == "Hello World!"


@pytest.mark.parametrize(
    ("abs_dir", "platform", "expected_path_type"),
    [
        ("/my_path/my_dir", "Linux", PurePosixPath),
        ("C:\\my_path\\my_dir", "Windows", PureWindowsPath),
        ("C:/my_path/my_dir", "Windows", PureWindowsPath),
        ("C://my_path//my_dir", "Windows", PureWindowsPath),
    ],
)
def test_purepath_conversion(abs_dir: str, platform: str, expected_path_type: PurePath):
    abs_pure_path = parse_platform_specific_absolute_path(abs_dir, platform)
    assert type(abs_pure_path) is expected_path_type
    assert abs_pure_path.as_posix() == abs_dir.replace("\\", "/").replace("//", "/")


def test_update_opaque_identifier():
    old_project_id = "project_id01234567891234"
    bdm_project: dict[str, Any] = {
        "schema_version": 1,
        "solution_name": "BdmSolution",
        "solution": {
            "display_name": "Bdm Solution",
            "version": 1,
            "steps": {
                "bdm_step": {
                    "state": {
                        "my_entity": "UPTODATE",
                        "other": "UPTODATE",
                        "result": "OUTOFDATE",
                        "directory": "OUTOFDATE",
                    },
                    "my_entity": {
                        "is_blob": True,
                        "original_name": "my_entity.json",
                        "entity_id": "94033ee5-6c32-4132-898b-7a8addb3c208",
                        "opaque_identifier": f"primary/{old_project_id}/bdm/product_aaaaaaaa:_DELIMITERmy_entity.json",
                        "mime_type": "text/plain",
                        "encoding": None,
                        "size": 14,
                    },
                    "list_handles": [
                        {
                            "is_blob": True,
                            "original_name": "a.txt",
                            "entity_id": "aaaabee5-6c38-4132-898b-7a8addb3c208",
                            "opaque_identifier": f"subsidiary/{old_project_id}/bdm/method_cccccccc:_DELIMITERa.txt",
                            "mime_type": "text/plain",
                            "encoding": None,
                            "size": 12,
                        },
                    ],
                },
                "other_bdm_step": {
                    "state": {},
                },
            },
        },
        "method_states": {},
        "instances": {
            "bdm_step": {
                "x_y": {
                    "name": f"projects/{old_project_id}/steps/instance-step/instances/x-y",
                    "pim_name": "instances/x",
                    "product_version": "string",
                    "service_name": "string",
                    "max_execution_time": 7200,
                    "recovery_state_info": {
                        "project_file": {
                            "is_blob": True,
                            "original_name": "project.json",
                            "entity_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "opaque_identifier": f"subsidiary/{old_project_id}/bdm/product_ffffffff:_DELIMITERproject.json",  # noqa: E501
                            "mime_type": None,
                            "encoding": None,
                            "size": 110,
                        },
                        "product_list_handles": [
                            {
                                "is_blob": True,
                                "original_name": "from_list_a.txt",
                                "entity_id": "9403bee5-6c38-4132-898b-7aaaaaaaaaaa",
                                "opaque_identifier": f"primary/{old_project_id}/bdm/product_zzzzzzzz:_DELIMITERfrom_list_a.txt",  # noqa: E501
                                "mime_type": "text/plain",
                                "encoding": None,
                                "size": 12,
                            },
                        ],
                        "random_value": "string",
                    },
                },
            },
        },
        "bdm_locks": [],
        "display_name": "test project",
        "date_created": "2024-08-09T17:25:15.772466",
        "date_modified": "2024-08-09T17:26:12.597291",
        "name": f"projects/{old_project_id}",
    }
    new_project_id = "abcdefghijklmnopqrstuvwx"
    model = ProjectModel[BdmSolution].model_validate(bdm_project)
    result = update_opaque_identifier(model, new_project_id)  # type: ignore
    assert result.solution.get_steps().bdm_step.my_entity.opaque_identifier.startswith(f"primary/{new_project_id}/bdm/")  # type: ignore
    assert (
        result.solution.get_steps()  # type: ignore
        .bdm_step.list_handles[0]  # type: ignore
        .opaque_identifier.startswith(f"subsidiary/{new_project_id}/bdm/")
    )
    assert (
        result.instances["bdm_step"]["x_y"]  # type: ignore
        .recovery_state_info.project_file["opaque_identifier"]  # type: ignore
        .startswith(f"subsidiary/{new_project_id}/bdm/")
    )
    assert (
        result.instances["bdm_step"]["x_y"]  # type: ignore
        .recovery_state_info.product_list_handles[0]["opaque_identifier"]  # type: ignore
        .startswith(f"primary/{new_project_id}/bdm/")
    )
