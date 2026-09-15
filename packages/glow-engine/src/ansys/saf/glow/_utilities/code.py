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

import importlib.util
import inspect
from pathlib import Path
from types import ModuleType


def is_compiled(file_path: Path) -> bool:
    # return whether the code base is compiled

    return file_path.suffix == ".pyc"


def load_python_file(file_path: Path) -> ModuleType:
    try:
        module_name = inspect.getmodulename(str(file_path))
        if not module_name:
            raise Exception(f"Module name not found for file {file_path}.")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            raise Exception(f"Cannot extract module spec from module {module_name}.")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        raise ValueError(f"Cannot import python file: {file_path}: {e}") from e
