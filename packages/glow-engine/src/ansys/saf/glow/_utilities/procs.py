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

import contextlib
import logging
import signal

import psutil

logger = logging.getLogger(__name__)


# Inspired by https://psutil.readthedocs.io/latest/recipes.html#controlling-processes
def kill_pids(
    pids: list[int],
    sig: signal.Signals = signal.SIGTERM,
    timeout: float = 10.0,
) -> tuple[list[psutil.Process], list[psutil.Process]]:
    """Kill a list of processes by PID with signal "sig" and return a (gone, still_alive) tuple."""
    processes: list[psutil.Process] = []
    for pid in pids:
        with contextlib.suppress(psutil.NoSuchProcess):
            try:
                p = psutil.Process(pid)
                logger.debug(f"Killing child process (pid: {p.pid})")
                p.send_signal(sig)
            except psutil.AccessDenied:
                logger.warning("Access denied when trying to kill process %d", pid)
                continue
            processes.append(p)
    gone, alive = psutil.wait_procs(processes, timeout=timeout)
    return (gone, alive)
