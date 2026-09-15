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
from pathlib import Path
from string import Template

from pydantic import BaseModel


class SharedFilesystemContextConfiguration(BaseModel):
    relative_path: Path


class SharedFilesystemConfiguration(BaseModel):
    shared_filesystem_root: Path
    contexts: dict[str, SharedFilesystemContextConfiguration]

    @classmethod
    def _substitute(
        cls,
        inp: SharedFilesystemContextConfiguration,
        substitute: Callable[[Path], Path],
    ) -> SharedFilesystemContextConfiguration:
        return SharedFilesystemContextConfiguration(relative_path=substitute(inp.relative_path))

    def render_template_vars(self, template_vars: dict[str, str]) -> "SharedFilesystemConfiguration":
        def substitute(path_template: Path) -> Path:
            return Path(Template(str(path_template)).substitute(**template_vars))

        return SharedFilesystemConfiguration(
            shared_filesystem_root=substitute(self.shared_filesystem_root).resolve(),
            contexts={k: SharedFilesystemConfiguration._substitute(v, substitute) for k, v in self.contexts.items()},
        )
