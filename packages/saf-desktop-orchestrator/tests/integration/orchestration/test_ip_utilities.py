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

import os
import platform
import subprocess
import sys

import psutil
import pytest

from ansys.saf.desktop.orchestrator._config.schema import LOCALHOST_IP
from ansys.saf.desktop.orchestrator._utilities.ip_utilities import (
    get_random_free_port,
    next_free_port,
    port_is_free,
    resolve_ip,
    wait_for_response,
)


@pytest.mark.parametrize("random_port", [False, True])
def test_port_is_not_free_after_use(random_port: bool):
    port = get_random_free_port() if random_port else next_free_port(54321)
    args = [sys.executable, "-m", "tests.integration.orchestration.simple_server", "--port", str(port)]
    print("starting process " + " ".join(args))
    process = None
    try:
        if platform.system() == "Windows":
            process = subprocess.Popen(
                args,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,  # type: ignore
                bufsize=1,  # type: ignore
            )
        else:
            process = subprocess.Popen(args, shell=False, preexec_fn=os.setsid)  # type: ignore

        wait_for_response(
            f"http://{LOCALHOST_IP}:{port}/health",
            tries=20,
        )
        assert not port_is_free(port)
    finally:
        if process:
            psutil.Process(process.pid).kill()
            process.wait()


def test_resolve_ip():
    # Case 1: IP contains 0.0.0.0
    input_ip = "0.0.0.0"
    expected_result = LOCALHOST_IP
    assert resolve_ip(input_ip) == expected_result

    # Case 2: IP does not contain 0.0.0.0
    input_ip = "192.168.1.1"
    assert resolve_ip(input_ip) == input_ip

    # Case 3: URL contains 0.0.0.0
    input_url = "http://0.0.0.0:8000/path"
    expected_url_result = "http://127.0.0.1:8000/path"
    assert resolve_ip(input_url) == expected_url_result

    # Case 4: URL does not contain 0.0.0.0
    input_url = "http://test.com/path"
    assert resolve_ip(input_url) == input_url
