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

from collections.abc import Callable
import os
from pathlib import Path
import re
import subprocess
from threading import Thread
from typing import IO, Any, Self

import psutil
import pytest


class Process:
    """
    A utility class to launch and manage subprocesses for testing purposes.
    """

    def __init__(
        self,
        cmd: list[str],
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
        bg: bool = False,
        input_str: str = "",
        health_check: Callable[["Process"], None] | None = None,
        expected_return_code: int | None = None,
    ) -> None:
        """
        Initialize a Process instance.

        Parameters
        ----------
        cmd : list[str]
            The command to run.
        env : dict[str, str] | None, optional
            Environment variables for the process (default: current environment).
        cwd : Path | None, optional
            Working directory for the process (default: current working directory).
        bg : bool, optional
            If True, run the process in the background (default: False).
        input_str : str, optional
            Input string to send to the process (foreground only).
        health_check : Callable[[Process], None] | None, optional
            Function to check process health (background only).
        expected_return_code : int | None, optional
            Expected return code (foreground only).

        Returns
        -------
        None
        """
        self._cmd = cmd
        self._env = env or os.environ.copy()
        self._cwd = cwd or Path.cwd()
        self._bg = bg
        self._input_str = input_str
        self._health_check = health_check
        self._expected_return_code = expected_return_code

        if self._health_check and not self._bg:
            raise ValueError("health_check can only be used with bg=True")
        if self._input_str and self._bg:
            raise ValueError("input_str can only be used with bg=False")
        if self._expected_return_code is not None and self._bg:
            raise ValueError("expected_return_code can only be used with bg=False")

        self._process: subprocess.Popen[str] | None = None
        self._process_output: list[str] = []

    @classmethod
    def run(cls, *args: Any, **kwargs: Any) -> Self:
        """
        Create, start, and return a Process instance.

        Equivalent to `Process(*args, **kwargs).start()`.

        Returns
        -------
        Process
            The started Process instance.
        """
        process = cls(*args, **kwargs)
        process.start()
        return process

    @property
    def process(self) -> subprocess.Popen[str] | None:
        """
        The underlying subprocess.Popen object, or None if not started.

        Returns
        -------
        subprocess.Popen[str] | None
            The process object, or None if not started.
        """
        return self._process

    @property
    def return_code(self) -> int | None:
        """
        The return code of the process, or None if not finished.

        Returns
        -------
        int | None
            The return code, or None if the process has not finished.
        """
        return self._process.returncode if self._process else None

    @property
    def output(self) -> list[str]:
        """
        The captured output lines from the process's stdout and stderr.

        Returns
        -------
        list[str]
            The output lines from the process.
        """
        return self._process_output

    def _read_process_output(self, out: IO[str]):
        for line in iter(out.readline, ""):
            clean_line = line.rstrip()
            if clean_line:
                self._process_output.append(clean_line)

    def start(self) -> None:
        """
        Start the process and capture its output.

        For foreground processes, waits for completion and checks return code if specified.
        For background processes, starts a thread to read output and optionally runs a health check.

        Returns
        -------
        None
        """
        self._process = subprocess.Popen(
            self._cmd,
            env=self._env,
            cwd=self._cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            text=True,
        )
        if not self._bg:
            # not using the thread in this case because it wasn't able to capture all the output
            stdout, _ = self._process.communicate(self._input_str)
            self._process_output = stdout.splitlines()
            if self._expected_return_code is not None:
                assert self._process.returncode == self._expected_return_code, self._process_output
            return

        t = Thread(target=self._read_process_output, args=(self._process.stdout,))
        t.daemon = True
        t.start()

        if self._health_check:
            try:
                self._health_check(self)
            except Exception as e:
                print(self.output)
                pytest.fail(f"Launch was not successful. Health check function failed. Error msg: {str(e)}.")

    def stop(self) -> None:
        """
        Stop the process and all its child processes, if running.

        Returns
        -------
        None
        """
        if self._process is None:
            return

        parent: psutil.Process | None = None
        try:
            parent = psutil.Process(self._process.pid)
        except psutil.NoSuchProcess:
            parent = None

        if parent is not None:
            for child in parent.children(recursive=True):
                self._terminate(child)
            self._terminate(parent, timeout=20)
            self._process = None

    def _terminate(self, process: psutil.Process, timeout: int = 0) -> None:
        try:
            process.terminate()
            if timeout > 0:
                process.wait(timeout)
        except psutil.NoSuchProcess:
            pass

    def restart(self, clear_output: bool = False) -> None:
        self.stop()
        if clear_output:
            self._process_output = []
        self.start()

    def find_msg_in_output(self, msg: str, regex: bool = False) -> str | None:
        """
        Search for a message in the process output.

        Parameters
        ----------
        msg : str
            The message or regex pattern to search for.
        regex : bool, optional
            If True, interpret `msg` as a regular expression (default: False).

        Returns
        -------
        str | None
            The first matching output line, or None if not found.
        """
        for line in self._process_output:
            if not regex:
                if msg in line:
                    return line
            else:
                if re.search(msg, line):
                    return line
