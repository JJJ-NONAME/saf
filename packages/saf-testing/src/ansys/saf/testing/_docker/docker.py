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

from importlib.util import find_spec
import os

import pytest


def is_docker_installed_fun() -> bool:
    # It's not a fixture because we use it inside pytest hooks too.
    if not find_spec("docker"):
        return False
    import docker

    try:
        base_url = os.getenv("DOCKER_HOST")
        if base_url:
            with docker.APIClient(base_url=base_url) as client:
                client.ping()
        else:
            with docker.APIClient() as client:
                client.ping()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def is_docker_requested(request: pytest.FixtureRequest) -> bool:
    return bool(request.config.getoption("--docker"))


@pytest.fixture(scope="session")
def is_docker_installed() -> bool:
    return is_docker_installed_fun()


@pytest.fixture(scope="session")
def is_docker_enabled(is_docker_installed: bool, is_docker_requested: bool) -> bool:
    # For any internal use where we only care about docker availability regardless of cause, use is_docker_enabled.
    # Other fixtures kept for detailed fail/skip messaging.
    return is_docker_requested and is_docker_installed
