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
import logging
import multiprocessing as mp
from multiprocessing.context import SpawnProcess
import os
from typing import Any

from ansys.saf.desktop.orchestrator._config.schema import DEFAULT_SAF_DESKTOP_HEALTH_CHECK_TIMEOUT
from ansys.saf.desktop.orchestrator._orchestration.process import ServiceProcess
from ansys.saf.desktop.orchestrator._utilities.process import kill_proc_tree

# By default, multiprocessing uses different start methods in Linux and Windows. Force the same in both.
# More info: https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
ctx = mp.get_context("spawn")
logger = logging.getLogger(__name__)


def _function_with_env(
    function: Callable[..., None],
    function_args: list[str],
    function_kwargs: dict[str, Any],
    env: dict[str, str],
):
    # Note that functions are executed with their own independent logger as with ServiceProcess.
    # It relies on further configuration. Otherwise, build a wrapper with the configuration and pass it here.
    os.environ.update(env)
    function(*function_args, **function_kwargs)


class PythonProcess(ServiceProcess):
    def __init__(
        self,
        function: Callable[..., None],
        function_kwargs: dict[str, Any] | None = None,
        port: int | None = None,
        ip: str = "localhost",
        env: dict[str, str] | None = None,
        health_route: str = "/health",
        health_check_timeout: int = DEFAULT_SAF_DESKTOP_HEALTH_CHECK_TIMEOUT,
    ) -> None:
        self._function = function
        self._function_kwargs = function_kwargs if function_kwargs is not None else {}
        super().__init__(
            [],
            port=port,
            ip=ip,
            env=env,
            health_route=health_route,
            health_check_timeout=health_check_timeout,
        )
        self._function_process: SpawnProcess | None = None

    @property
    def function_process(self) -> SpawnProcess | None:
        return self._function_process

    def run(self, additional_args: list[str] | None = None, allow_window: bool = True) -> None:
        args = self._args + (additional_args or [])
        if not allow_window:
            raise ValueError("allow_window = False not supported")
        logger.debug(
            f"starting process {self._function.__name__} with args: '{args}' and kwargs: '{self._function_kwargs}'",
        )
        self._function_process = ctx.Process(
            target=_function_with_env,
            args=[self._function, args, self._function_kwargs, self._env],
            daemon=False,
        )
        self._function_process.start()

    def stop(self) -> None:
        if self._function_process is None:
            return
        if self._function_process.pid is None:
            return
        logger.debug(f"Killing process '{self._function.__name__}' with pid: '{self._function_process.pid}'")
        # multiprocessing.terminate() does terminate descendant processes of the process...
        # see https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process.terminate
        kill_proc_tree(self._function_process.pid)
        self._function_process.terminate()
        self._function_process.join()
