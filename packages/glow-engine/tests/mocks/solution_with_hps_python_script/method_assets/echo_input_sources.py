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
# fmt: off
from pathlib import Path
from typing import cast

from ansys.saf.glow.hps_execution import HpsExecution


class EchoInputSources(HpsExecution):

    def execute(self) -> dict[str, int | float | str | bool]:

        file_path_str = cast("str", self.context.input_parameters["test_input_file"])
        file_path = Path(file_path_str)
        assert file_path.is_file(), f"File not found: {file_path}"
        relative_path = file_path.relative_to(Path.cwd())

        dir_path_str = cast("str", self.context.input_parameters["test_input_dir"])
        dir_path = Path(dir_path_str)
        assert dir_path.is_dir(), f"Directory not found: {dir_path}"
        asset_txt_content = (dir_path / "asset.txt").read_text()

        another_dir_path_str = cast("str", self.context.input_parameters["another_input_dir"])
        another_dir_path = Path(another_dir_path_str)
        assert another_dir_path.is_dir(), f"Another directory not found: {another_dir_path}"
        another_asset_txt_content = (another_dir_path / "another_asset.txt").read_text()

        return {
            "result": relative_path.as_posix().replace("/", "SLASH").replace(".", "DOT"),
            "asset_content": asset_txt_content,
            "another_asset_content": another_asset_txt_content,
        }

# fmt: on
