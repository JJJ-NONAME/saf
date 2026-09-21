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

import os

import pytest


def is_marker_within_collected_tests(items: list[pytest.Item], expected_marker: str) -> bool:
    for item in items:
        markers = [marker.name for marker in item.iter_markers()]
        if expected_marker in markers:
            return True
    return False


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--docker",
        action="store_true",
        default=False,
        help="Run tests that require docker: containerization, HPS and PostgreSQL. Only available for Linux.",
    )
    parser.addoption("--ext-hps", action="store_true", help="Run HPS tests assuming HPS Deployment runs externally.")
    parser.addoption("--ext-hps-scaler", action="store_true", help="Run HPS tests assuming HPS Scaler runs externally.")
    parser.addoption(
        "--debug-mode",
        action="store_true",
        help="Run every end-to-end test in debug mode. May cause debug-related tests to fail.",
    )


@pytest.fixture(scope="session")
def num_pytest_workers() -> int:
    return int(os.getenv("PYTEST_XDIST_WORKER_COUNT", 1))
