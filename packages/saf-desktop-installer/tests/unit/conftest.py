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

from collections.abc import Generator
from pathlib import Path
import shutil
from typing import Protocol, TypeVar

import pytest

from tests.unit.installer_ui_process import InstallerUIProcess

F = TypeVar("F")
YieldFixture = Generator[F, None, None]


class InstallerUi(Protocol):
    def __call__(
        self,
        solution_metadata_path: Path,
        installation_directory: Path | None = None,
        cwd: Path | None = None,
    ) -> InstallerUIProcess: ...


@pytest.fixture
def installer_ui() -> YieldFixture[InstallerUi]:

    procs: list[InstallerUIProcess] = []

    def _installer_ui(
        solution_metadata_path: Path,
        installation_directory: Path | None = None,
        cwd: Path | None = None,
    ) -> InstallerUIProcess:
        process = InstallerUIProcess(
            solution_metadata_path,
            installation_directory=installation_directory,
            cwd=cwd,
        ).start()
        procs.append(process)
        return process

    yield _installer_ui

    for proc in procs:
        proc.stop()


@pytest.fixture(scope="class")
def copy_assets() -> YieldFixture[None]:
    """Copy installer UI assets required when launching InstallerUIProcess from source."""
    installer_path = Path(__file__).parent.parent.parent / "src" / "ansys" / "saf" / "desktop" / "installer"
    source_logo_path = installer_path / "_package" / "assets" / "installer_ui_logo.png"
    bootstrap_css_path = installer_path / "_package" / "assets" / "bootstrap.min.css"
    assert source_logo_path.is_file(), f"Source logo not found at {source_logo_path}"
    assert bootstrap_css_path.is_file(), f"Bootstrap css not found at {bootstrap_css_path}"
    destination_dir = installer_path / "assets"
    destination_dir.mkdir(exist_ok=True)
    shutil.copy(source_logo_path, destination_dir / "installer_ui_logo.png")
    shutil.copy(bootstrap_css_path, destination_dir / "bootstrap.min.css")
    yield
    if destination_dir.is_dir():
        shutil.rmtree(destination_dir)
