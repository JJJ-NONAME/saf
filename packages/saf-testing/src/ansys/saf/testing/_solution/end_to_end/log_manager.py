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
from enum import Enum
from pathlib import Path
import shutil


class ServiceType(Enum):
    """When allowing errors via the error_logged marker, we will specify this value."""

    API = "api"
    UI = "ui"
    Other = "other"


class LogContainer:
    def __init__(
        self,
        process_output_method: Callable[..., list[str]],
        log_file_path: Path,
        container_type: ServiceType = ServiceType.Other,
        current_test: str = "Test not set yet.",
    ) -> None:
        self._process_output_method = process_output_method
        self._filepath: Path = log_file_path
        self._copied_lines: int = 0
        self._type: ServiceType = container_type
        self.current_test: str = current_test
        self.current_test_cache: list[str] = []

    @property
    def output(self) -> list[str]:
        return self._process_output_method()

    def copy_and_return_lines(self, tag: str):
        new_lines = self.output[self._copied_lines :]
        self._copied_lines += len(new_lines)
        if new_lines:
            tag_str = f"{tag}-first_copy" if not self._filepath.is_file() else tag
            with self._filepath.open("a", encoding="utf-8") as dst:
                for line in new_lines:
                    dst.write(f"{line.strip()} [{tag_str}]\n")
            self.current_test_cache.extend(new_lines)
        return new_lines

    def reset_copy_count(self):
        self._copied_lines = 0


class LogContainerManager:
    def __init__(self, root_logs_folder: Path) -> None:
        self._log_containers: dict[str, LogContainer] = {}
        self._logs_folder: Path = root_logs_folder
        self.current_test: str = "Current test not set yet."

        if self._logs_folder.exists():
            shutil.rmtree(self._logs_folder)

        self._logs_folder.mkdir(exist_ok=True, parents=True)

    @property
    def containers(self) -> dict[str, LogContainer]:
        return self._log_containers

    def add_log_container(
        self,
        process_output_method: Callable[..., list[str]],
        log_name: str,
        container_type: ServiceType,
    ):
        if log_name in self.containers:
            self.remove_log_container(log_name)
        # Need to call process_output_method each time because the output is retrieved dynamically.
        container = LogContainer(
            process_output_method,
            self._logs_folder / (log_name + ".log"),
            container_type,
            self.current_test,
        )
        self._log_containers[log_name] = container
        return container

    def remove_log_container(self, log_name: str):
        container = self._log_containers.pop(log_name)
        container.copy_and_return_lines("clearing container")

    def clear_processes(self, name_pattern: str):
        names = list(self.containers.keys())
        for name in names:
            if name_pattern in name:
                self.remove_log_container(name)

    def copy_and_return_logs(self, tag: str, return_names: list[str] | None = None) -> dict[str, list[str]]:
        return_names = return_names if return_names is not None else list(self.containers.keys())
        return_lines: dict[str, list[str]] = {}

        for name, container in self.containers.items():
            lines = container.copy_and_return_lines(tag)
            if name in return_names:
                return_lines[name] = lines

        return return_lines

    def set_current_test(self, test_name: str) -> None:
        """Since Glow processes may be restarted during tests, log lines before restarting are only persisted on files
        (since process output is cleared on restarts.). To avoid having to read the files again and scan for lines from
        the test being checked for errors, we cache every line for the current test and only flush it after checking."""
        self.current_test: str = test_name
        for container in self.containers.values():
            container.current_test = test_name
            container.current_test_cache = []
