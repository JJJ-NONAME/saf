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

from unittest.mock import MagicMock

import pytest_mock

from ansys.saf.desktop.orchestrator._config.schema import Settings
from ansys.saf.desktop.orchestrator._orchestration.solution_ui_framework import SolutionUIFramework
from ansys.saf.desktop.orchestrator._orchestration.streamlit_launcher import StreamlitLauncher


def test_start_solution_ui(mocker: pytest_mock.MockerFixture):
    mock_start_solution_ui_service = mocker.patch(
        "ansys.saf.desktop.orchestrator._orchestration.streamlit_launcher.StreamlitLauncher._start_solution_ui_service",
    )
    mock_get_main_module_and_path = mocker.patch(
        "ansys.saf.desktop.orchestrator._orchestration.streamlit_launcher.StreamlitLauncher._get_ui_app_path",
    )

    # Arrange
    mock_get_main_module_and_path.return_value = "/fake/path/to/module"

    launcher = StreamlitLauncher(
        Settings(saf_desktop_solution_name="solution"),
        solution_module_name="solution",
        definition_module_name="definition",
        with_pim=True,
        with_ui=True,
        ui_framework=SolutionUIFramework.streamlit,
        with_portal=True,
        env_file=None,
        enable_automatic_project_migration=False,
        log_to_files=False,
    )

    # Act
    launcher.start_solution_ui()

    # Assert
    mock_get_main_module_and_path.assert_called_once()
    mock_start_solution_ui_service.assert_called_once()


def test_get_project(mocker: pytest_mock.MockerFixture):
    mock_get_service_info = mocker.patch(
        "ansys.saf.desktop.orchestrator._orchestration.launcher.Launcher.get_service_info",
    )

    # Arrange
    mock_service_info = MagicMock()
    mock_service_info.address = "http://localhost:8501"
    mock_get_service_info.return_value = mock_service_info

    launcher = StreamlitLauncher(
        Settings(saf_desktop_solution_name="solution"),
        solution_module_name="solution",
        definition_module_name="definition",
        with_pim=True,
        with_ui=True,
        ui_framework=SolutionUIFramework.streamlit,
        with_portal=True,
        env_file=None,
        enable_automatic_project_migration=False,
        log_to_files=False,
    )

    project_name = "test_project"

    # Act
    project_url = launcher.get_project(project_name)

    # Assert
    mock_get_service_info.assert_called_once_with("UI")
    assert project_url == "http://localhost:8501/?project_id=test_project"
