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

import os
from pathlib import Path

import pytest
import pytest_mock

from ansys.saf.desktop.installer.__main__ import package_solution
from ansys.saf.desktop.installer._package.config import InstallerConfig
from ansys.saf.desktop.installer._package.solution import SolutionInfo


@pytest.fixture
def mock_installer_calls(mocker: pytest_mock.MockerFixture) -> None:
    mocker.patch("ansys.saf.desktop.installer.__main__.initial_cleanup")
    mocker.patch("ansys.saf.desktop.installer.__main__.setup_solution_folder")
    mocker.patch("ansys.saf.desktop.installer.__main__.build_executable_installer")


@pytest.mark.usefixtures("mock_installer_calls", "mock_solution_display_name")
def test_env_file_in_solution_root_dir(solution_root_dir: Path, mocker: pytest_mock.MockerFixture):
    env_file = solution_root_dir / ".env"
    env_file.write_text("POETRY_HTTP_BASIC_MOCK=mock")
    solution_info = SolutionInfo(solution_root_dir)
    config = InstallerConfig()

    mocker.patch.dict(os.environ, {})
    assert "POETRY_HTTP_BASIC_MOCK" not in os.environ
    package_solution(solution_info, config)
    assert os.environ["POETRY_HTTP_BASIC_MOCK"] == "mock"


@pytest.mark.usefixtures("mock_installer_calls", "mock_solution_display_name")
@pytest.mark.parametrize("relative_path", [True, False])
def test_passing_env_file(
    solution_root_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    mocker: pytest_mock.MockerFixture,
    relative_path: bool,
):
    env_file = solution_root_dir / "custom_dir" / ".env"
    env_file.parent.mkdir()
    env_file.write_text("POETRY_HTTP_BASIC_MOCK=mock")
    (solution_root_dir / ".env").unlink(missing_ok=True)

    solution_info = SolutionInfo(solution_root_dir)
    if relative_path:
        monkeypatch.chdir(solution_root_dir)
    config = InstallerConfig(env_file=env_file.relative_to(solution_root_dir) if relative_path else env_file.resolve())

    mocker.patch.dict(os.environ, {})
    assert "POETRY_HTTP_BASIC_MOCK" not in os.environ
    package_solution(solution_info, config)
    assert os.environ["POETRY_HTTP_BASIC_MOCK"] == "mock"


@pytest.mark.usefixtures("mock_installer_calls", "mock_solution_display_name")
def test_passing_env_file_has_priority_over_solution_root_dir(
    solution_root_dir: Path,
    mocker: pytest_mock.MockerFixture,
):
    env_file = solution_root_dir / "custom_dir" / ".env"
    env_file.parent.mkdir()
    env_file.write_text("POETRY_HTTP_BASIC_MOCK=mock")
    env_file_2 = solution_root_dir / ".env"
    env_file_2.write_text("POETRY_HTTP_BASIC_MOCK_2=mock")

    solution_info = SolutionInfo(solution_root_dir)
    config = InstallerConfig(env_file=env_file)

    mocker.patch.dict(os.environ, {})
    assert "POETRY_HTTP_BASIC_MOCK" not in os.environ
    assert "POETRY_HTTP_BASIC_MOCK_2" not in os.environ
    package_solution(solution_info, config)
    assert os.environ["POETRY_HTTP_BASIC_MOCK"] == "mock"
    assert "POETRY_HTTP_BASIC_MOCK_2" not in os.environ


@pytest.mark.usefixtures("mock_installer_calls", "mock_solution_display_name")
def test_non_related_env_vars_are_ignored(solution_root_dir: Path, mocker: pytest_mock.MockerFixture):
    env_file = solution_root_dir / ".env"
    env_file.write_text("POETRY_HTTP_BASIC_MOCK=mock\nMY_OTHER_ENV_VAR=mock")
    solution_info = SolutionInfo(solution_root_dir)
    config = InstallerConfig()

    mocker.patch.dict(os.environ, {})
    assert "POETRY_HTTP_BASIC_MOCK" not in os.environ
    assert "MY_OTHER_ENV_VAR" not in os.environ
    package_solution(solution_info, config)
    assert os.environ["POETRY_HTTP_BASIC_MOCK"] == "mock"
    assert "MY_OTHER_ENV_VAR" not in os.environ
