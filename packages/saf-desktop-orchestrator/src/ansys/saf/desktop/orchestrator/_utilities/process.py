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

from collections.abc import Callable
import contextlib
import os
import signal
from typing import Any

import psutil


# taken from psutils recipes: https://psutil.readthedocs.io/en/latest/#kill-process-tree
def kill_proc_tree(
    pid: int,
    sig: signal.Signals = signal.SIGTERM,
    include_parent: bool = True,
    timeout: float | None = None,
    on_terminate: Callable[[psutil.Process], Any] | None = None,
) -> tuple[list[psutil.Process], list[psutil.Process]]:
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callback function which is
    called as soon as a child terminates.
    """
    if pid == os.getpid():
        raise RuntimeError("I won't kill myself!")
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return ([], [])
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        with contextlib.suppress(psutil.NoSuchProcess):
            p.send_signal(sig)
    gone, alive = psutil.wait_procs(children, timeout=timeout, callback=on_terminate)
    return (gone, alive)
