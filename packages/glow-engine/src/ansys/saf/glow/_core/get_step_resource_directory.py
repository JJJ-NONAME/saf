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

import inspect
from pathlib import Path


def get_step_resource_directory(step_type: type, directory_name: str) -> Path:
    source_file = inspect.getsourcefile(step_type)
    if source_file is None:
        raise ValueError(f"Cannot find source file named {source_file} for step type {step_type}")
    parents = Path(source_file).parents
    for parent in parents:
        asset_dir = parent / directory_name
        if asset_dir.is_dir():
            return asset_dir
    raise ValueError(f"Cannot find {directory_name} directory for step type {step_type}")
