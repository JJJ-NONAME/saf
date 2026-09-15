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

import platform
import time

import psutil
import pytest

from tests.e2e.conftest import MINIMAL_SOLUTION_WITH_DASH_UI, OrchestrateSolution


@pytest.mark.skipif(platform.system() == "Linux", reason="No splash screen on Linux yet")
def test_time_from_process_start_to_splash(orchestrate_solution: OrchestrateSolution):
    """Verify that the splash screen subprocess is spawned within the acceptable time threshold.

    The orchestrator spawns the splash screen as a multiprocessing.Process before any
    heavy imports. This test monitors the orchestrator's child processes via psutil to
    detect when the splash subprocess appears (identified by --multiprocessing-fork in
    frozen builds or spawn_main in normal interpreters) and asserts the elapsed time
    from process creation is below the configured threshold.
    """
    args = [
        "-m",
        "ansys.saf.desktop.orchestrator",
        "--solution-main-module-name",
        MINIMAL_SOLUTION_WITH_DASH_UI + ".main",
    ]

    process = orchestrate_solution(
        args=args,
        wait_for_healthy=False,
    )

    assert process.process
    pid = process.process.pid
    assert pid

    psutil_proc = psutil.Process(pid)

    process_create_time = psutil_proc.create_time()

    # Poll for the splash screen subprocess. In a frozen environment (e.g. PyInstaller)
    # the child cmdline contains --multiprocessing-fork; in a normal interpreter it uses
    # -c "from multiprocessing.spawn import spawn_main; spawn_main(...)".
    splash_create_time: float | None = None
    for _ in range(60):  # 60 * 0.05s = 3s max polling
        try:
            for child in psutil_proc.children(recursive=True):
                try:
                    cmdline = " ".join(child.cmdline())
                    if "--multiprocessing-fork" in cmdline or "spawn_main" in cmdline:
                        splash_create_time = child.create_time()
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            if splash_create_time is not None:
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            break
        time.sleep(0.05)

    assert splash_create_time
    elapsed = splash_create_time - process_create_time
    assert elapsed < 2.0
