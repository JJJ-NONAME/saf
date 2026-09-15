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
from typing import Dict, Union
from ansys.saf.glow.hps_execution import HpsExecution
import pathlib
from sympy import Symbol, cos  # type: ignore


class UseSympy(HpsExecution):

    def execute(self) -> Dict[str, Union[int, float, str, bool]]:

        n = self.context.input_parameters["n"]
        x = Symbol("x")  # type: ignore
        e = 1 / cos(x)  # type: ignore
        result = str(e.series(x, 0, n))  # type: ignore
        pathlib.Path("result").write_text(result)
        return {}

# fmt: on
