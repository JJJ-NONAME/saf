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

# this code is designed to be loadable into older versions of python in HPS
# hence disabling ruff and black
# ruff: noqa
# fmt: off

# type ignore here because sympy is not a dependency of glow
# but is loaded into the test SAF Product Environment.
# This means that tests can't import this script directly.
from sympy import Symbol, cos  # type: ignore

def compute_series(n: int):

    x = Symbol("x")  # type: ignore
    e = 1 / cos(x)  # type: ignore
    return str(e.series(x, 0, n))  # type: ignore

# fmt: on
