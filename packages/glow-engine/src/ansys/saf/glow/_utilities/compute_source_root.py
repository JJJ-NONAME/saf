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

from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType


def compute_source_root(module: ModuleType) -> Path:
    if hasattr(module, "__path__"):
        paths = module.__path__
        if not paths:
            raise ValueError("solution module path could not be determined.")
        path = Path(paths[-1])
    else:
        spec = module.__spec__
        path = _compute_module_path_from_spec(spec)

    package = module.__package__
    if package is None:
        raise ValueError("solution module package could not be determined.")
    num_of_package_parts = package.count(".") + 1
    return Path(*(path.parts[:-num_of_package_parts]))


def _compute_module_path_from_spec(spec: ModuleSpec | None):
    if spec is None:
        raise ValueError("solution module spec could not be determined.")
    if spec.origin is None:
        search_locations = spec.submodule_search_locations
        if search_locations is None or len(search_locations) == 0:
            raise ValueError("solution module submodule search locations could not be determined.")
        path = Path(search_locations[-1])
    else:
        path = Path(spec.origin)
        if path.is_file():
            path = path.parent
    return path
