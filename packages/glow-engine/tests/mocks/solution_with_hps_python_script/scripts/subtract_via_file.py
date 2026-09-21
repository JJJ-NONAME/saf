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

from pathlib import Path


class NestedString:
    def __init__(self, nested_string: str):
        self._nested_string = nested_string

    @property
    def nested_string(self) -> str:
        return self._nested_string


def subtract_via_file(a: Path, b: int, suffix_dir: Path, prefix_dir: Path, nested_string: NestedString):
    a_number = int(a.read_text().strip())
    subtract = a_number - b
    add = a_number + b
    concat = NestedString(
        (prefix_dir / "prefix.txt").read_text().strip()
        + nested_string.nested_string
        + (suffix_dir / "suffix.txt").read_text().strip(),
    )
    multiply = a_number * b

    Path("result.txt").write_text(str(subtract))
    results_dir = Path("results")
    results_dir.mkdir()
    (results_dir / "r.txt").write_text(str(multiply))

    return {"add": add, "concat": concat}
