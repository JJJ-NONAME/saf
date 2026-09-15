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
import platform
import re
import subprocess

import pytest
import pytest_mock

from ansys.saf.desktop.installer._package.solution import (
    create_env_file,
    create_version_file,
    get_appdata_directory,
    get_solution_package_dir,
    move_assets_and_deployment_script,
)


@pytest.fixture
def built_env_file(solution_root_dir: Path):
    built_env_file = solution_root_dir / "dist" / "solution" / "definitions" / "test_module" / ".env"
    built_env_file.parent.mkdir(parents=True, exist_ok=True)
    return built_env_file


@pytest.fixture
def solution_env_file(solution_root_dir: Path):
    solution_env_file = solution_root_dir / ".env"
    solution_env_file.parent.mkdir(parents=True, exist_ok=True)
    return solution_env_file


@pytest.fixture
def solution_version_file(solution_root_dir: Path):
    solution_version_file = solution_root_dir / "dist" / "solution" / "version.txt"
    solution_version_file.parent.mkdir(parents=True, exist_ok=True)
    return solution_version_file


def test_create_env_file_no_existing_env_file(solution_root_dir: Path, built_env_file: Path, solution_env_file: Path):
    solution_env_file.unlink(missing_ok=True)

    create_env_file(solution_root_dir, "test_module")

    assert built_env_file.is_file()
    env_content = built_env_file.read_text()
    assert "PORTAL_DATABASE_TYPE=sqlite" in env_content
    assert f"DATABASE_LOCATION={get_appdata_directory()}/ansys/portal" in env_content
    assert "PORTAL_PROJECT_DATABASE_LOCATION=${DATABASE_LOCATION}/project.db" in env_content
    assert "SAF_DESKTOP_LOG_TO_FILES=True" in env_content


def test_create_env_file_existing_env_file_without_saf_desktop_log(
    solution_root_dir: Path,
    built_env_file: Path,
    solution_env_file: Path,
):
    existing_env_content = "CUSTOM_VAR=custom_value\nANOTHER_VAR=another_value"
    solution_env_file.write_text(existing_env_content)

    create_env_file(solution_root_dir, "test_module")

    assert built_env_file.is_file()
    env_content = built_env_file.read_text()
    assert env_content.startswith(existing_env_content)
    assert env_content.endswith("SAF_DESKTOP_LOG_TO_FILES=True\n")


def test_create_env_file_existing_env_file_with_saf_desktop_log_in_middle(
    solution_root_dir: Path,
    built_env_file: Path,
    solution_env_file: Path,
):
    existing_env_content = (
        "CUSTOM_VAR=custom_value\nSAF_DESKTOP_LOG_TO_FILES=False\nANOTHER_VAR=another_value\nFINAL_VAR=final_value"
    )
    solution_env_file.write_text(existing_env_content)

    create_env_file(solution_root_dir, "test_module")

    assert built_env_file.is_file()
    env_content = built_env_file.read_text()
    assert env_content == existing_env_content


def test_create_env_file_empty_existing_env_file(
    solution_root_dir: Path,
    built_env_file: Path,
    solution_env_file: Path,
):
    solution_env_file.write_text("")

    create_env_file(solution_root_dir, "test_module")

    assert built_env_file.is_file()
    env_content = built_env_file.read_text()
    assert env_content == "\nSAF_DESKTOP_LOG_TO_FILES=True\n"


def test_create_env_file_saf_desktop_log_as_comment(
    solution_root_dir: Path,
    built_env_file: Path,
    solution_env_file: Path,
):
    existing_env_content = "CUSTOM_VAR=value\n# SAF_DESKTOP_LOG_TO_FILES=True\nOTHER_VAR=other"
    solution_env_file.write_text(existing_env_content)

    create_env_file(solution_root_dir, "test_module")

    assert built_env_file.is_file()
    env_content = built_env_file.read_text()
    assert env_content.startswith(existing_env_content)
    assert env_content.endswith("SAF_DESKTOP_LOG_TO_FILES=True\n")


def test_create_env_file_saf_desktop_log_as_value_of_another(
    solution_root_dir: Path,
    built_env_file: Path,
    solution_env_file: Path,
):
    existing_env_content = "CUSTOM_VAR=the value of this env var contains SAF_DESKTOP_LOG_TO_FILES\nOTHER_VAR=other"
    solution_env_file.write_text(existing_env_content)

    create_env_file(solution_root_dir, "test_module")

    assert built_env_file.is_file()
    env_content = built_env_file.read_text()
    assert env_content.startswith(existing_env_content)
    assert env_content.endswith("SAF_DESKTOP_LOG_TO_FILES=True\n")


def test_create_version_file(solution_root_dir: Path, solution_version_file: Path, mocker: pytest_mock.MockFixture):
    mocker.patch("subprocess.check_output", return_value="7028a8ce51ee01e0998bd7af82e3e4e529b198ed")

    create_version_file(solution_root_dir, "My Solution", "1.0.0")

    assert solution_version_file.is_file()

    version_content = solution_version_file.read_text()
    expected_pattern = (
        r"build.date = \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} (\w+)?\n"
        r"github.sha = 7028a8ce51ee01e0998bd7af82e3e4e529b198ed\n"
        r"ReleaseVersion = My Solution Solution 1\.0\.0\n"
        r"ProductName = My Solution Solution\n"
        r"Report_Release = 1\.0\.0"
    )
    assert re.fullmatch(expected_pattern, version_content)


@pytest.mark.parametrize(
    "git_exception",
    [subprocess.CalledProcessError(1, "git"), FileNotFoundError()],
    ids=["CalledProcessError", "FileNotFoundError"],
)
def test_create_version_file_git_error(
    solution_root_dir: Path,
    solution_version_file: Path,
    mocker: pytest_mock.MockFixture,
    caplog: pytest.LogCaptureFixture,
    git_exception: Exception,
):
    mocker.patch("subprocess.check_output", side_effect=git_exception)

    create_version_file(solution_root_dir, "My Solution", "1.0.0")

    assert solution_version_file.is_file()

    version_content = solution_version_file.read_text()
    expected_pattern = (
        r"build.date = \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} (\w+)?\n"
        r"github.sha = Unknown\n"
        r"ReleaseVersion = My Solution Solution 1\.0\.0\n"
        r"ProductName = My Solution Solution\n"
        r"Report_Release = 1\.0\.0"
    )
    assert re.fullmatch(expected_pattern, version_content)

    log_warning = (
        "Could not get the git SHA to populate the version file. Check if git is installed and initialized in the "
        "current project. Setting git SHA to Unknown."
    )
    assert log_warning in caplog.text


def _get_solution_module_name(solution_root_dir: Path) -> str:
    src_dir = solution_root_dir / "src"
    definition_files = sorted(src_dir.rglob("solution/definition.py"))
    if not definition_files:
        raise FileNotFoundError(f"No solution definition.py found under {src_dir}")
    if len(definition_files) > 1:
        raise RuntimeError(f"Multiple solution definition.py files found under {src_dir}: {definition_files}")
    return definition_files[0].parent.parent.name


def _get_platform_suffix() -> str:
    return ".ico" if platform.system() == "Windows" else ".png"


def test_move_assets_and_deployment_script_fallback_to_default_assets(solution_root_dir: Path) -> None:
    solution_folder = solution_root_dir / "dist" / "solution"
    solution_folder.mkdir(parents=True, exist_ok=True)
    solution_module_name = _get_solution_module_name(solution_root_dir)
    suffix = _get_platform_suffix()

    move_assets_and_deployment_script(solution_folder, solution_root_dir, solution_module_name)

    logo_file = solution_folder / "assets" / "installer_ui_logo.png"
    favicon_file = solution_folder / "assets" / f"favicon{suffix}"
    shortcut_file = solution_folder / "assets" / f"shortcut{suffix}"

    assert logo_file.is_file()
    assert favicon_file.is_file()
    assert shortcut_file.is_file()
    assert shortcut_file.read_bytes() == favicon_file.read_bytes()


def test_move_assets_and_deployment_script_overrides_with_custom_assets(solution_root_dir: Path) -> None:
    solution_folder = solution_root_dir / "dist" / "solution"
    solution_folder.mkdir(parents=True, exist_ok=True)
    solution_module_name = _get_solution_module_name(solution_root_dir)
    suffix = _get_platform_suffix()

    custom_assets_dir = (
        get_solution_package_dir(solution_root_dir, solution_module_name) / "ui" / "assets" / "installer"
    )
    custom_assets_dir.mkdir(parents=True, exist_ok=True)

    custom_logo = custom_assets_dir / "installer_ui_logo.png"
    custom_favicon = custom_assets_dir / f"favicon{suffix}"
    custom_shortcut = custom_assets_dir / f"shortcut{suffix}"
    custom_logo.write_bytes(b"custom-logo")
    custom_favicon.write_bytes(b"custom-favicon")
    custom_shortcut.write_bytes(b"custom-shortcut")

    move_assets_and_deployment_script(solution_folder, solution_root_dir, solution_module_name)

    assert (solution_folder / "assets" / "installer_ui_logo.png").read_bytes() == custom_logo.read_bytes()
    assert (solution_folder / "assets" / f"favicon{suffix}").read_bytes() == custom_favicon.read_bytes()
    assert (solution_folder / "assets" / f"shortcut{suffix}").read_bytes() == custom_shortcut.read_bytes()


def test_move_assets_and_deployment_script_warns_for_non_platform_favicon(
    solution_root_dir: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    solution_folder = solution_root_dir / "dist" / "solution"
    solution_folder.mkdir(parents=True, exist_ok=True)
    solution_module_name = _get_solution_module_name(solution_root_dir)
    suffix = _get_platform_suffix()
    other_suffix = ".png" if suffix == ".ico" else ".ico"

    custom_assets_dir = (
        get_solution_package_dir(solution_root_dir, solution_module_name) / "ui" / "assets" / "installer"
    )
    custom_assets_dir.mkdir(parents=True, exist_ok=True)
    (custom_assets_dir / f"favicon{other_suffix}").write_bytes(b"wrong-platform-favicon")

    caplog.set_level("WARNING")
    move_assets_and_deployment_script(solution_folder, solution_root_dir, solution_module_name)

    assert f"Ignoring favicon{other_suffix}" in caplog.text
    default_favicon = (
        Path(__file__).parent.parent.parent
        / "src"
        / "ansys"
        / "saf"
        / "desktop"
        / "installer"
        / "_package"
        / "assets"
        / f"favicon{suffix}"
    )
    assert (solution_folder / "assets" / f"favicon{suffix}").read_bytes() == default_favicon.read_bytes()
