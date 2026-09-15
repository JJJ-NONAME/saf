# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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

from ansys.saf.testing._common.common import YieldFixture


@pytest.fixture
def check_docstring(request: pytest.FixtureRequest) -> YieldFixture[None]:
    yield  # Let the test pass/fail before checking for docstrings

    docstring: str = request.node.function.__doc__  # type: ignore

    error_message = ""

    if not docstring:
        error_message = "Docstring missing on E2E test."
    elif "Test Cases:\n" not in docstring:
        error_message = "Test Case information missing on E2E test."
    # TODO: check if test case links are working

    if error_message:
        pytest.fail(reason=error_message)
