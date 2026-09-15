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
import pathlib
import re
from typing import Dict, Union, cast
from ansys.saf.glow.hps_execution import HpsExecution
import time


class Add(HpsExecution):

    def execute(self) -> Dict[str, Union[int, float, str, bool]]:
        time_to_generate_the_output_file = cast(float, self.context.input_parameters["time_to_generate_the_output_file"])
        path_str = cast(str, self.context.input_parameters["custom_input_file"])
        content = pathlib.Path(path_str).read_text()
        args = re.split("\\s+", content)
        result = float(args[0]) + float(args[1])
        time.sleep(time_to_generate_the_output_file)
        pathlib.Path("result").write_text(f"{result=}")
        return {}

# fmt: on
