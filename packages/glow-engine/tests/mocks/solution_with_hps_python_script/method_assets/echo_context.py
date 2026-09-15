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

from pathlib import Path
from typing import Dict, Union
from ansys.saf.glow.hps_execution import HpsExecution


class EchoContext(HpsExecution):

    def _escape(self, s : str) -> str:
        return s.replace(".", "DOT")

    def execute(self) -> Dict[str, Union[int, float, str, bool]]:
        products = [f"{x.name} {self._escape(x.version)}" for x in self.context.products]
        required_output_files = [f"{key} {self._escape(value)}" for key, value in self.context.required_output_files.items()]
        required_output_files.sort()
        self.context.required_output_parameters.sort()
        Path("expected_dir").mkdir()
        return {
            "required_output_parameters": " ".join(self.context.required_output_parameters),
            "required_output_files" : " ".join(required_output_files),
            "required_output_directories": " ".join(self.context.required_output_directories),
            "products" : "  ".join(products),
        }

# fmt: on
