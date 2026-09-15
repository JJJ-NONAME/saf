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

import pytest

from ansys.saf.cli._utilities.conversion import namespace_to_pkg_name


@pytest.mark.parametrize(
    ("namespace", "expected_pkg_name"),
    [
        ("ansys.solutions", "ansys-solutions"),
        ("my_org.platform", "my-org-platform"),
        ("my_org.my_project.module", "my-org-my-project-module"),
    ],
)
def test_namespace_to_pkg_name(namespace: str, expected_pkg_name: str):
    assert namespace_to_pkg_name(namespace) == expected_pkg_name
