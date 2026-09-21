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
import re
import shutil

STEP_FILES = [
    "solution/{{cookiecutter.__step_module_name}}.py",
]

DASH_UI_FILES = [
    "ui/pages/{{cookiecutter.__ui_page_file_name}}.py",
]


if "{{ cookiecutter.__ui_framework }}" == "dash":  # pyright: ignore[reportUnnecessaryComparison]
    STEP_FILES.extend(DASH_UI_FILES)


def _patch_page(solution_root_dir: Path) -> None:
    step_name = "{{ cookiecutter.__step_name }}"
    page_py = (
        solution_root_dir
        / "src"
        / "{{ cookiecutter.__solution_namespace_path }}"
        / "{{ cookiecutter.__solution_module_name }}"
        / "ui"
        / "pages"
        / "page.py"
    )
    if not page_py.is_file():
        raise FileNotFoundError(f"Page file {page_py} not found.")
    content = page_py.read_text(encoding="utf-8")
    anchor_start = "dmc.MantineProvider(\n    ["
    new_divs = (
        f'        dcc.Store(id="{step_name}-console-logs-store", data=""),\n'
        f'        html.Div(id="{step_name}-event-listeners-container"),'
    )
    if re.search(re.escape(new_divs.strip()), content):
        raise RuntimeError(f"The required UI elements already exist in {page_py} for step {step_name}.")
    anchor_pos = content.find(anchor_start)
    if anchor_pos == -1:
        raise RuntimeError(
            f"Cannot add the required UI elements to {page_py}. "
            f"The solution template might be incompatible with step {step_name}.",
        )
    closing_pos = content.find("\n    ],", anchor_pos + len(anchor_start))
    if closing_pos == -1:
        raise RuntimeError(
            f"Cannot add the required UI elements to {page_py}. "
            f"The solution template might be incompatible with step {step_name}.",
        )
    content = content[:closing_pos] + "\n" + new_divs + content[closing_pos:]
    page_py.write_text(content, encoding="utf-8")


def main() -> None:
    solution_root_dir = Path("{{ cookiecutter.__solution_root_dir }}")
    src_files: list[Path] = []
    dst_files: list[Path] = []
    for file in STEP_FILES:
        src = Path.cwd() / file
        dst = (
            solution_root_dir
            / "src"
            / "{{ cookiecutter.__solution_namespace_path }}"
            / "{{ cookiecutter.__solution_module_name }}"
            / file
        )
        if dst.is_file():
            raise FileExistsError(f"File {dst} already exists.")
        src_files.append(src)
        dst_files.append(dst)

    for src, dst in zip(src_files, dst_files, strict=True):
        shutil.copy(src, dst)

    _patch_page(solution_root_dir)


if __name__ == "__main__":
    main()
