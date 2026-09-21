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

import sys
import time

import httpx2
import psutil
import pytest

from ansys.saf.desktop.orchestrator._orchestration.orchestrator import Orchestrator
from ansys.saf.desktop.orchestrator._orchestration.process import ServiceProcess
from ansys.saf.desktop.orchestrator._orchestration.python_process import PythonProcess
from ansys.saf.desktop.orchestrator._utilities.ip_utilities import get_random_free_port
from tests.integration.orchestration.simple_server import launch_server


def verify_pid_not_exists(pid: int):
    pid_exists = True
    num_tries = 0
    while pid_exists and num_tries < 10:
        pid_exists = psutil.pid_exists(pid)
        if not pid_exists:
            break
        num_tries += 1
        time.sleep(0.25)
    assert not pid_exists


@pytest.mark.parametrize("ip", [("127.0.0.1"), ("localhost"), ("0.0.0.0")])
def test_orchestrator_launch_simple_function(ip: str):
    """Tests that the orchestrator can launch a simple function,
    that the service is running and responding.
    """
    orchestrator = Orchestrator()
    port = get_random_free_port()
    service = PythonProcess(launch_server, function_kwargs={"host": ip, "port": port}, ip=ip, port=port)
    service_info = orchestrator.start_service("type", service)
    orchestrator.healthy()
    # Verify service being running and responding.
    process: PythonProcess = service_info.process  # type: ignore
    assert process.function_process is not None
    assert isinstance(process.function_process.pid, int)
    assert psutil.pid_exists(process.function_process.pid)
    orchestrator.stop()
    # Verify that the process is no longer running.
    verify_pid_not_exists(process.function_process.pid)


def test_orchestrator_launch_simple_server():
    """Tests that the orchestrator can launch a simple server,
    that the service is running and responding.
    """
    orchestrator = Orchestrator()
    port = get_random_free_port()
    service = ServiceProcess(
        args=[sys.executable, "-m", "tests.integration.orchestration.simple_server", "--port", str(port)],
        port=port,
    )
    service_info = orchestrator.start_service("type", service)
    orchestrator.healthy()
    # Verify service being running and responding.
    process: ServiceProcess = service_info.process
    assert process.process is not None
    assert isinstance(process.process.pid, int)
    assert psutil.pid_exists(process.process.pid)
    orchestrator.stop()
    # Verify that the process is no longer running.
    verify_pid_not_exists(process.process.pid)


@pytest.mark.parametrize("pid_url", [("multiprocessing-pid"), ("subprocess-pid")])
def test_orchestrator_kill_subprocesses(pid_url: str):
    """Tests that the orchestrator can kill subprocesses."""
    orchestrator = Orchestrator()
    port = get_random_free_port()
    ip = "localhost"
    service = PythonProcess(launch_server, function_kwargs={"host": ip, "port": port}, ip=ip, port=port)
    orchestrator.start_service("type", service)
    orchestrator.healthy()
    # Verify service being running and responding.
    launched_subprocess_pid = int(httpx2.get(f"http://localhost:{port}/{pid_url}").text)
    assert psutil.pid_exists(launched_subprocess_pid)
    orchestrator.stop()
    # Verify that the subprocess is no longer running.
    verify_pid_not_exists(launched_subprocess_pid)
