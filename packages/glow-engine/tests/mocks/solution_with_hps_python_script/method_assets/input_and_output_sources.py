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
import shutil
import tempfile
from typing import cast

from ansys.saf.glow.hps_execution import HpsExecution


class InputOutputSources(HpsExecution):

    def execute(self) -> dict[str, int | float | str | bool]:

        dir_path_str = cast("str", self.context.input_parameters["input_dir"])
        dir_path = Path(dir_path_str)
        assert dir_path.is_dir(), f"Directory not found: {dir_path}"
        input_dir_txt = (dir_path / "asset.txt").read_text()

        dir_path_eval_str = cast(
            "str", self.context.input_parameters["input_dir_eval_path"],
        )
        dir_path_eval = Path(dir_path_eval_str)
        assert dir_path_eval.is_dir(), f"Directory not found: {dir_path_eval}"
        assert dir_path_eval.relative_to(
            dir_path_eval.parent.parent,
        ) == Path("subdir/sub")
        input_dir_eval_path_txt = (dir_path_eval / "another_asset.txt").read_text()

        input_zip_str = cast("str", self.context.input_parameters["input_zip"])
        input_zip = Path(input_zip_str)
        input_zip_txt = ""
        assert input_zip.is_file()
        with tempfile.TemporaryDirectory() as tmp_dir:
            shutil.unpack_archive(input_zip, tmp_dir)
            input_zip_txt = (Path(tmp_dir) / "inside_dir" / "inside_asset.txt").read_text()

        output_dir = Path("output_dir")
        output_dir.mkdir()
        output_dir_file = output_dir / "output_file.txt"
        output_dir_file.write_text("This is an output file!")

        output_sub_dir = Path("output_sub_dir/sub")
        output_sub_dir.mkdir(parents=True, exist_ok=True)
        output_sub_file = output_sub_dir / "sub_file.txt"
        output_sub_file.write_text("This is another output file!")

        output_zip = Path("output_zip_dir")
        (output_zip / "dir_a" / "dir_b").mkdir(parents=True)
        (output_zip / "dir_a" / "dir_b" / "my_file.txt").write_text("Testing no eval path")
        shutil.make_archive(
            base_name="output_zip",
            format="zip",
            root_dir="output_zip_dir",
            base_dir=".",
        )
        Path("output_zip.zip").rename("output_zip")

        output_zip_eval = Path("output_zip_dir_eval/dir_test")
        output_zip_eval.mkdir(parents=True)
        (output_zip_eval / "my_other_file.txt").write_text("Testing with eval path")
        shutil.make_archive(
            base_name="output",
            format="zip",
            root_dir="output_zip_dir_eval",
            base_dir=".",
        )
        shutil.move("output.zip", output_zip_eval.parent)

        return {
            "input_dir_txt": input_dir_txt,
            "input_dir_eval_path_txt": input_dir_eval_path_txt,
            "input_zip_txt": input_zip_txt,
        }

# fmt: on
