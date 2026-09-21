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
from typing import Any, Dict, cast
from ansys.saf.glow.hps_execution import HpsExecution

class AddInput:

    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

class AddOutput:

    def __init__(self, result: int, positive: bool) -> None:
        self._result = result
        self._positive = positive

    @property
    def result(self) -> int:
        return self._result

    @property
    def positive(self) -> bool:
        return self._positive

class Add(HpsExecution):

    def execute(self) -> Dict[str, Any]:
        input= cast(AddInput, self.context.input_parameters["input"])
        result = input.x + input.y
        positive = result >= 0
        return {"output":AddOutput(result, positive)}

# fmt: on
