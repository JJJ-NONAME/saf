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

from pathlib import Path
import platform
import re

from pydantic import BaseModel, field_validator


class SolutionRegistry(BaseModel):
    name: str
    root_dir: Path
    display_name: str

    @property
    def is_valid(self) -> bool:
        return self.root_dir.is_dir()

    @field_validator("name")
    @classmethod
    def _validate_solution_name(cls, solution_name: str) -> str:
        if platform.system() == "Windows":
            invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
        elif platform.system() == "Linux":
            invalid_chars = r"[/\x00]"
        else:
            raise ValueError("Unsupported operating system")
        if bool(re.search(invalid_chars, solution_name)):
            raise ValueError(f"Solution name contains invalid characters: {invalid_chars}")
        return solution_name

    def __eq__(self, other: object):
        if not isinstance(other, type(self)):
            return False
        return self.root_dir == other.root_dir


class SolutionDatabase(BaseModel):
    solutions: list[SolutionRegistry] = []
