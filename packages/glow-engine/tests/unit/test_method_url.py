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

from ansys.saf.glow._server.method_url import MethodUrl


@pytest.mark.parametrize(
    ("url", "step_name", "method_name", "step_id", "method_id", "project_url", "step_url", "project_resource_name"),
    [
        (
            "http://209.191.122.70/projects/12345678/steps/my-step:test-method",
            "my_step",
            "test_method",
            "my-step",
            "test-method",
            "http://209.191.122.70/projects/12345678",
            "http://209.191.122.70/projects/12345678/steps/my-step",
            "projects/12345678",
        ),
        (
            "http://[2001:db8:85a3:8d3:1319:8a2e:370:7348]/projects/12345678/steps/my-step:test-method",
            "my_step",
            "test_method",
            "my-step",
            "test-method",
            "http://[2001:db8:85a3:8d3:1319:8a2e:370:7348]/projects/12345678",
            "http://[2001:db8:85a3:8d3:1319:8a2e:370:7348]/projects/12345678/steps/my-step",
            "projects/12345678",
        ),
    ],
)
def test_method_parser_returns_step_name_and_method_from_well_formed_urls(
    url: str,
    step_name: str,
    method_name: str,
    step_id: str,
    method_id: str,
    project_url: str,
    step_url: str,
    project_resource_name: str,
):
    parsed_url = MethodUrl(url)
    assert parsed_url.step_name == step_name
    assert parsed_url.method_name == method_name
    assert parsed_url.step_id == step_id
    assert parsed_url.method_id == method_id
    assert parsed_url.project_resource_name == project_resource_name
    assert parsed_url.project_url == project_url
    assert parsed_url.step_url == step_url


@pytest.mark.parametrize(
    ("url", "match"),
    [
        (
            "http://209.191.122.70/projects/12345678/steps/my-step",
            "Expecting url of the form \\<domain\\>\\/projects\\/\\<project\\>\\/steps\\/\\<step\\>\\:\\<method\\> "
            "\\- got http\\:\\/\\/209\\.191\\.122\\.70\\/projects\\/12345678\\/steps\\/my\\-step",
        ),
        (
            "http://[2001:db8:85a3:8d3:1319:8a2e:370:7348]/projects/12345678/steps/my-step",
            "Expecting url of the form \\<domain\\>\\/projects\\/\\<project\\>\\/steps\\/\\<step\\>\\:\\<method\\> "
            "\\- got http\\:\\/\\/\\[2001\\:db8\\:85a3\\:8d3\\:1319\\:8a2e\\:370\\:7348\\]\\/projects\\/12345678\\"
            "/steps\\/my\\-step",
        ),
    ],
)
def test_method_parser_raises_exception_from_url_missing_colon(url: str, match: str):
    with pytest.raises(Exception, match=match):
        MethodUrl(url)
