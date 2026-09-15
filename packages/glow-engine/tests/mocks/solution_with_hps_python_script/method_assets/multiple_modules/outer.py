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

from importlib.machinery import SourceFileLoader
from pathlib import Path


def compute_series(n: int):
    # instead of using import we have to dynamically import because
    # the solution is copied as part of the test :-(
    # in a real solution you'd use a normal import
    inner_module_path = Path(__file__).parent / "inner.py"
    inner = SourceFileLoader("inner", inner_module_path.as_posix()).load_module()
    return {"result": inner.compute_series(n)}
