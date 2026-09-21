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

CONTENT = "hello world"


def assert_subdirectory_content(subtop: Path):
    subtop_children = list(subtop.iterdir())
    assert len(subtop_children) == 1
    leaf = subtop_children[0]
    assert leaf.name == "leaf.txt"
    assert leaf.is_file()
    assert leaf.read_text() == CONTENT


def assert_directory_content(top: Path, top_name: str = "top") -> None:
    assert top.is_dir()
    assert top.name == top_name
    top_children = list(top.iterdir())
    assert not any(f for f in top_children if f.is_file())
    empty = next(filter(lambda d: d.name == "empty", top_children))
    subtop = next(filter(lambda d: d.name == "subtop", top_children))
    assert not any(empty.iterdir())
    assert_subdirectory_content(subtop)


def create_directory_content(root: Path):
    top = root / "top"
    top.mkdir()
    (top / "empty").mkdir()
    subtop = top / "subtop"
    subtop.mkdir()
    leaf = subtop / "leaf.txt"
    leaf.write_text(CONTENT)
    return top
