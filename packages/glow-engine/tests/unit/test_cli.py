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

import ast
import importlib.util
import os
from pathlib import Path
import py_compile
import shutil
import sys
from types import ModuleType
from unittest import mock
from unittest.mock import patch

from click.testing import CliRunner
from pydantic import PostgresDsn
import pytest

from ansys.saf.glow._config.const import (
    GLOW_API_HOST,
    GLOW_API_PORT,
    GLOW_API_URL,
    GLOW_DATABASE_LOCATION,
    GLOW_DATABASE_TYPE,
    GLOW_PIM_SOCKET_PATH,
    GLOW_PORTAL_URL,
    GLOW_PRODUCT_INSTANCE_SYSTEM_HOST,
    GLOW_PRODUCT_INSTANCE_SYSTEM_PORT,
    GLOW_PROJECT_FILES_DIRECTORY,
    GLOW_UI_HOST,
    GLOW_UI_PORT,
    GLOW_WS_EVENTS_ADDR,
    DatabaseType,
)
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow.cli._cli_entry_point import SolutionModule, cli
from tests.conftest import IGNORE_PYC_FILES, MOCKS_DIR, SOLUTIONS_MOCKS_DIR
import tests.mocks.solutions.minimal_solution


@pytest.fixture(autouse=True)
def clean_env():
    # Tested functions internally import modules, modify the sys.path/sys.modules and environment variables
    # such as GLOW_SOLUTION_NAME, _URL, _HOST, _PORT... Clean it up between tests
    old_paths = sys.path.copy()
    old_modules = sys.modules.copy()
    with mock.patch.dict(os.environ, os.environ.copy()):
        yield
    sys.path = old_paths
    sys.modules = old_modules


def test_glow_engine_api_default():
    with (
        patch("ansys.saf.glow.cli._cli_entry_point.run_api_server"),
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_definition_module",
            return_value="",
        ),
        patch(
            "ansys.saf.glow.cli._cli_entry_point._import_definition_module",
            return_value=tests.mocks.solutions.minimal_solution,
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["api"])
        settings = Settings()
        assert str(settings.glow_api_host) == "127.0.0.1"
        assert settings.glow_api_port == 5432
        assert str(settings.glow_product_instance_system_host) == "127.0.0.1"
        assert settings.glow_product_instance_system_port is None
        assert result.exit_code == 0


def test_glow_engine_api_customize_via_cli():
    with (
        patch("ansys.saf.glow.cli._cli_entry_point.run_api") as run_api_mock,
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_definition_module",
            return_value="",
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["api", "--host", "0.0.0.0", "--port", "4354", "--pim-host", "7.7.7.8", "--pim-port", "4567"],
        )
        run_api_params = run_api_mock.call_args_list[0][0]
        assert run_api_params == ("0.0.0.0", 4354, "", "7.7.7.8", 4567, [], None)
        assert result.exit_code == 0
        assert not os.environ.get(GLOW_API_HOST)
        assert not os.environ.get(GLOW_API_PORT)
        assert not os.environ.get(GLOW_PRODUCT_INSTANCE_SYSTEM_HOST)
        assert not os.environ.get(GLOW_PRODUCT_INSTANCE_SYSTEM_PORT)


def test_cli_api_customize_via_env_var(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(GLOW_API_HOST, "0.0.0.0")
    monkeypatch.setenv(GLOW_API_PORT, "4356")
    monkeypatch.setenv(GLOW_PRODUCT_INSTANCE_SYSTEM_HOST, "8.8.8.8")
    monkeypatch.setenv(GLOW_PRODUCT_INSTANCE_SYSTEM_PORT, "4357")
    with (
        patch("ansys.saf.glow.cli._cli_entry_point.run_api") as run_api_mock,
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_definition_module",
            return_value="",
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["api"])
        run_api_params = run_api_mock.call_args_list[0][0]
        assert run_api_params == ("0.0.0.0", 4356, "", "8.8.8.8", 4357, [], None)
        assert result.exit_code == 0


def test_glow_engine_api_customize_via_li():
    with patch("uvicorn.run"):
        runner = CliRunner()
        result = runner.invoke(cli, ["api", "--definition", "tests.mocks.solutions.minimal_solution"])
        assert result.exit_code == 0
        settings = Settings()  # type: ignore
        assert str(settings.glow_api_host) == "127.0.0.1"
        assert settings.glow_api_port == 5432
        assert str(settings.glow_product_instance_system_host) == "127.0.0.1"
        assert settings.glow_product_instance_system_port is None


def test_glow_engine_api_dotenv_provide_default():
    with patch("ansys.saf.glow._server.main.uvicorn.Server.main_loop"):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".env").write_text(
                f"{GLOW_PRODUCT_INSTANCE_SYSTEM_PORT}=5678\n{GLOW_API_PORT}=1234\n{GLOW_PIM_SOCKET_PATH}=/tmp/pim.sock",
            )
            runner.invoke(cli, ["api", "--definition", "tests.mocks.solutions.minimal_solution"])
            assert os.environ.get(GLOW_API_PORT) == "1234"
            assert os.environ.get(GLOW_PRODUCT_INSTANCE_SYSTEM_PORT) == "5678"
            assert os.environ.get(GLOW_PIM_SOCKET_PATH) == "/tmp/pim.sock"


def test_glow_engine_api_env_var_override_dotenv(monkeypatch: pytest.MonkeyPatch):
    with patch("ansys.saf.glow._server.main.uvicorn.Server.main_loop"):
        monkeypatch.setenv(GLOW_API_PORT, "1111")
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".env").write_text(
                f"{GLOW_PRODUCT_INSTANCE_SYSTEM_PORT}=5678\n{GLOW_API_PORT}=1234\n{GLOW_PIM_SOCKET_PATH}=/tmp/pim.sock",
            )
            runner.invoke(cli, ["api", "--definition", "tests.mocks.solutions.minimal_solution"])
            assert os.environ.get(GLOW_API_PORT) == "1111"
            assert os.environ.get(GLOW_PRODUCT_INSTANCE_SYSTEM_PORT) == "5678"
            assert os.environ.get(GLOW_PIM_SOCKET_PATH) == "/tmp/pim.sock"


def test_glow_engine_api_cli_arg_override_env_var(monkeypatch: pytest.MonkeyPatch):
    with patch("ansys.saf.glow._server.main.uvicorn.Server.main_loop"):
        monkeypatch.setenv(GLOW_API_PORT, "1111")
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".env").write_text(
                f"{GLOW_PRODUCT_INSTANCE_SYSTEM_PORT}=5678\n{GLOW_API_PORT}=1234\n{GLOW_PIM_SOCKET_PATH}=/tmp/pim.sock",
            )
            runner.invoke(cli, ["api", "--definition", "tests.mocks.solutions.minimal_solution", "--port", "9999"])
            assert os.environ.get(GLOW_API_PORT) == "9999"
            assert os.environ.get(GLOW_PRODUCT_INSTANCE_SYSTEM_PORT) == "5678"
            assert os.environ.get(GLOW_PIM_SOCKET_PATH) == "/tmp/pim.sock"


def test_glow_engine_api_env_file_option_override_default_dotenv():
    with patch("ansys.saf.glow._server.main.uvicorn.Server.main_loop"):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".env").write_text(
                f"{GLOW_PRODUCT_INSTANCE_SYSTEM_PORT}=5678\n{GLOW_API_PORT}=1234\n{GLOW_PIM_SOCKET_PATH}=/tmp/pim.sock",
            )  # .env in cwd
            env_file = Path("dir") / ".env"
            env_file.parent.mkdir(exist_ok=True, parents=True)
            env_file.write_text(f"{GLOW_PRODUCT_INSTANCE_SYSTEM_PORT}=1111\n{GLOW_PIM_SOCKET_PATH}=/tmp/pim2.sock")
            runner.invoke(
                cli,
                ["api", "--definition", "tests.mocks.solutions.minimal_solution", "--env-file", "dir/.env"],
            )
            assert os.environ.get(GLOW_API_PORT) is None
            assert os.environ.get(GLOW_PRODUCT_INSTANCE_SYSTEM_PORT) == "1111"
            assert os.environ.get(GLOW_PIM_SOCKET_PATH) == "/tmp/pim2.sock"


def test_glow_engine_api_cli_arg_override_env_file():
    with patch("ansys.saf.glow._server.main.uvicorn.Server.main_loop"):
        runner = CliRunner()
        with runner.isolated_filesystem():
            env_file = Path("dir") / ".env"
            env_file.parent.mkdir(exist_ok=True, parents=True)
            env_file.write_text(
                f"{GLOW_PRODUCT_INSTANCE_SYSTEM_PORT}=1111\n{GLOW_API_PORT}=2222\n{GLOW_PIM_SOCKET_PATH}=/tmp/pim.sock",
            )
            runner.invoke(
                cli,
                [
                    "api",
                    "--definition",
                    "tests.mocks.solutions.minimal_solution",
                    "--env-file",
                    "dir/.env",
                    "--port",
                    "9090",
                ],
            )
            assert os.environ.get(GLOW_API_PORT) == "9090"
            assert os.environ.get(GLOW_PRODUCT_INSTANCE_SYSTEM_PORT) == "1111"
            assert os.environ.get(GLOW_PIM_SOCKET_PATH) == "/tmp/pim.sock"


def verify_run_server(
    args: list[str],
    expected_definition_module: str = "",
    expected_ui_module: str = "",
    expected_exception: str = "",
):
    with (
        patch("ansys.saf.glow.cli._cli_entry_point.run_ui") as run_ui_mock,
        patch(
            "ansys.saf.glow.cli._cli_entry_point.run_api",
        ) as run_api_mock,
    ):
        runner = CliRunner()
        result = runner.invoke(cli, args)
        assert result.exit_code == 0 if not expected_exception else 1
        if expected_exception:
            assert expected_exception in result.output
        elif expected_definition_module and not expected_ui_module:
            definition_module = run_api_mock.call_args_list[0][0][2]
            assert isinstance(definition_module, ModuleType)
            assert definition_module.__name__ == expected_definition_module
        elif expected_ui_module:
            definition_module = run_ui_mock.call_args_list[0][0][2]
            assert isinstance(definition_module, ModuleType)
            assert definition_module.__name__ == expected_definition_module
            ui_module = run_ui_mock.call_args_list[0][0][3]
            assert isinstance(ui_module, ModuleType)
            assert ui_module.__name__ == expected_ui_module


def copy_solution(orig_dir: Path, dest_dir: Path, compile_solution: bool):
    shutil.copytree(orig_dir, dest_dir, dirs_exist_ok=True, ignore=IGNORE_PYC_FILES)
    if compile_solution:
        for file in dest_dir.rglob("*"):
            if file.is_file() and file.suffix == ".py":
                py_compile.compile(str(file), str(file.with_suffix(".pyc")))
                file.unlink()


def test_glow_engine_api_with_definition():
    verify_run_server(
        ["api", "--definition", "tests.mocks.solutions.minimal_solution"],
        expected_definition_module="tests.mocks.solutions.minimal_solution",
    )


def test_glow_engine_api_with_definition_compiled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "compiled_mocks" / "minimal_solution_compiled.pyc"
    solution_dir.parent.mkdir(parents=True, exist_ok=True)
    py_compile.compile(str(SOLUTIONS_MOCKS_DIR / "minimal_solution.py"), str(solution_dir))
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["api", "--definition", "compiled_mocks.minimal_solution_compiled"],
        expected_definition_module="compiled_mocks.minimal_solution_compiled",
    )


def test_glow_engine_api_with_definition_using_path(tmp_path: Path):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "minimal_solution.py"
    solution_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOLUTIONS_MOCKS_DIR / "minimal_solution.py", solution_dir)
    verify_run_server(
        ["api", "--definition", str(solution_dir)],
        expected_definition_module="ansys.solutions.minimal_solution",
    )


def test_glow_engine_api_with_definition_using_compiled_path(tmp_path: Path):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "minimal_solution.pyc"
    solution_dir.parent.mkdir(parents=True, exist_ok=True)
    py_compile.compile(str(SOLUTIONS_MOCKS_DIR / "minimal_solution.py"), str(solution_dir))
    verify_run_server(
        ["api", "--definition", str(solution_dir)],
        expected_definition_module="ansys.solutions.minimal_solution",
    )


def test_glow_engine_api_with_solution():
    verify_run_server(
        ["api", "--solution", "tests.mocks.solution_with_ui.main"],
        expected_definition_module="tests.mocks.solution_with_ui.solution.definition",
    )


def test_glow_engine_api_with_solution_rare_structure():
    verify_run_server(
        ["api", "--solution", "tests.mocks.solution_rare_structure.minimal_main"],
        expected_exception="The solution definition module cannot be omitted in this configuration or mode",
    )


def test_glow_engine_api_with_compiled_solution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "compiled_mocks" / "solution_with_ui_compiled"
    copy_solution(MOCKS_DIR / "solution_with_ui", solution_dir, compile_solution=True)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["api", "--solution", "compiled_mocks.solution_with_ui_compiled.main"],
        expected_definition_module="compiled_mocks.solution_with_ui_compiled.solution.definition",
    )


def test_glow_engine_api_with_compiled_solution_rare_structure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "compiled_mocks" / "solution_rare_structure"
    copy_solution(MOCKS_DIR / "solution_rare_structure", solution_dir, compile_solution=True)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["api", "--solution", "compiled_mocks.solution_rare_structure.minimal_main"],
        expected_exception="The solution definition module cannot be omitted in this configuration or mode",
    )


def test_glow_engine_api_with_solution_using_path(tmp_path: Path):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_without_ui_in_ansys"
    copy_solution(MOCKS_DIR / "solution_without_ui_in_ansys", solution_dir, compile_solution=False)
    verify_run_server(
        ["api", "--solution", str(solution_dir / "main.py")],
        expected_definition_module="ansys.solutions.solution_without_ui_in_ansys.solution.definition",
    )


def test_glow_engine_api_with_solution_using_path_rare_structure(tmp_path: Path):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_rare_structure_in_ansys"
    copy_solution(MOCKS_DIR / "solution_rare_structure_in_ansys", solution_dir, compile_solution=False)
    verify_run_server(
        ["api", "--solution", str(solution_dir / "minimal_main.py")],
        expected_definition_module="ansys.solutions.solution_rare_structure_in_ansys.minimal_solution",
    )


def test_glow_engine_api_with_solution_using_compiled_path(tmp_path: Path):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_without_ui_in_ansys"
    copy_solution(MOCKS_DIR / "solution_without_ui_in_ansys", solution_dir, compile_solution=True)
    verify_run_server(
        ["api", "--solution", str(solution_dir / "main.pyc")],
        expected_definition_module="ansys.solutions.solution_without_ui_in_ansys.solution.definition",
    )


def test_glow_engine_api_with_solution_using_compiled_path_rare_structure(tmp_path: Path):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_rare_structure_in_ansys"
    copy_solution(MOCKS_DIR / "solution_rare_structure_in_ansys", solution_dir, compile_solution=True)
    verify_run_server(
        ["api", "--solution", str(solution_dir / "minimal_main.pyc")],
        expected_exception="The solution definition module cannot be omitted in this configuration or mode",
    )


def test_glow_engine_api_with_context_from_solution():
    with patch("ansys.saf.glow.cli._cli_entry_point.run_api") as run_api_mock:
        runner = CliRunner()
        definition_module = importlib.import_module("tests.mocks.solutions.minimal_solution")
        runner.invoke(cli, ["api"], obj=SolutionModule(definition_module))
        definition_module = run_api_mock.call_args_list[0][0][2]
        assert isinstance(definition_module, ModuleType)
        assert definition_module.__name__ == "tests.mocks.solutions.minimal_solution"


def test_glow_engine_api_with_autodiscovery(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_without_ui_in_ansys"
    copy_solution(MOCKS_DIR / "solution_without_ui_in_ansys", solution_dir, compile_solution=False)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["api"],
        expected_definition_module="ansys.solutions.solution_without_ui_in_ansys.solution.definition",
    )


def test_glow_engine_api_with_autodiscovery_missing_import(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Simulates scenario where we don't have the UI libraries
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_with_missing_import_in_ansys"
    copy_solution(
        MOCKS_DIR / "solution_with_missing_import_in_ansys",
        solution_dir,
        compile_solution=False,
    )
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["api"],
        expected_definition_module="ansys.solutions.solution_with_missing_import_in_ansys.solution.definition",
    )


def test_glow_engine_api_with_autodiscovery_rare_structure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_rare_structure_in_ansys"
    copy_solution(MOCKS_DIR / "solution_rare_structure_in_ansys", solution_dir, compile_solution=False)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    expected_error = (
        "Error: Failed to find a viable solution entry point.\n"
        "None of the following directories contain main.py or main.pyc files:\n"
        f"{str(solution_dir)}"
    )

    # Mocking the find_spec() result because we may have dependencies in the tests group that are in th
    # ansys.solutions namespace
    class MockSpec:
        submodule_search_locations = [str(solution_dir.parent)]

    with patch("importlib.util.find_spec", return_value=MockSpec):
        verify_run_server(["api"], expected_exception=expected_error)


def test_glow_engine_api_with_autodiscovery_compiled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_without_ui_in_ansys"
    copy_solution(MOCKS_DIR / "solution_without_ui_in_ansys", solution_dir, compile_solution=True)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["api"],
        expected_definition_module="ansys.solutions.solution_without_ui_in_ansys.solution.definition",
    )


def test_glow_engine_api_with_autodiscovery_rare_structure_compiled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_rare_structure_in_ansys"
    copy_solution(MOCKS_DIR / "solution_rare_structure_in_ansys", solution_dir, compile_solution=True)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    expected_error = (
        "Error: Failed to find a viable solution entry point.\n"
        "None of the following directories contain main.py or main.pyc files:\n"
        f"{str(solution_dir)}"
    )

    # Mocking the find_spec() result because we may have dependencies in the tests group that are in th
    # ansys.solutions namespace
    class MockSpec:
        submodule_search_locations = [str(solution_dir.parent)]

    with patch("importlib.util.find_spec", return_value=MockSpec):
        verify_run_server(["api"], expected_exception=expected_error)


def test_glow_engine_api_with_autodiscovery_missing_import_compiled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Simulates scenario where we don't have the UI libraries
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_with_missing_import_in_ansys"
    copy_solution(
        MOCKS_DIR / "solution_with_missing_import_in_ansys",
        solution_dir,
        compile_solution=True,
    )
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["api"],
        expected_definition_module="ansys.solutions.solution_with_missing_import_in_ansys.solution.definition",
    )


def test_glow_engine_api_with_autodiscovery_with_ui(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_with_ui_in_ansys"
    copy_solution(MOCKS_DIR / "solution_with_ui_in_ansys", solution_dir, compile_solution=False)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["api"],
        expected_definition_module="ansys.solutions.solution_with_ui_in_ansys.solution.definition",
    )


def test_glow_engine_ui_default():
    with (
        patch("dash_extensions.enrich.DashProxy.run"),
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_ui_module",
            return_value="tests.mocks.solution_with_ui.ui.app",
        ),
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_definition_module",
            return_value="tests.mocks.solution_with_ui.solution.definition",
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["ui"])
        assert result.exit_code == 0
        settings = Settings()
        assert str(settings.glow_ui_host) == "127.0.0.1"
        assert settings.glow_ui_port == 5433
        assert str(settings.glow_api_host) == "127.0.0.1"
        assert settings.glow_api_port == 5432
        assert os.environ.get(GLOW_API_URL) == "http://127.0.0.1:5432"
        assert not os.environ.get(GLOW_PORTAL_URL)
        assert os.environ.get(GLOW_WS_EVENTS_ADDR) == "ws://127.0.0.1:5432"


def test_glow_engine_ui_without_ui_module():
    with (
        patch("ansys.saf.glow.cli._cli_entry_point.get_ui_module", return_value=None),
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_definition_module",
            return_value="",
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["ui"])
        assert result.output.startswith("Error: The ui app module cannot be omitted in this configuration or mode")
        assert result.exit_code == 1


def test_glow_engine_ui_customize_via_cli():
    with (
        patch("dash_extensions.enrich.DashProxy.run"),
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_ui_module",
            return_value="tests.mocks.solution_with_ui.ui.app",
        ),
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_definition_module",
            return_value="tests.mocks.solution_with_ui.solution.definition",
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "ui",
                "--host",
                "0.0.0.0",
                "--port",
                "3462",
                "--api-server-url",
                "http://23.4.6.145:54432",
                "--portal-ui-url",
                "http://0.0.0.1234:12345",
            ],
        )
        assert result.exit_code == 0
        settings = Settings()
        assert str(settings.glow_ui_host) == "0.0.0.0"
        assert settings.glow_ui_port == 3462
        assert str(settings.glow_api_host) == "127.0.0.1"
        assert settings.glow_api_port == 5432
        assert os.environ.get(GLOW_API_URL) == "http://23.4.6.145:54432"
        assert os.environ.get(GLOW_PORTAL_URL) == "http://0.0.0.1234:12345"
        assert os.environ.get(GLOW_WS_EVENTS_ADDR) == "ws://23.4.6.145:54432"


def test_glow_engine_ui_customize_via_env_var(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(GLOW_UI_HOST, "0.0.0.0")
    monkeypatch.setenv(GLOW_UI_PORT, "3462")
    monkeypatch.setenv(GLOW_API_URL, "http://23.4.6.145:54432")
    monkeypatch.setenv(GLOW_PORTAL_URL, "http://0.0.0.1234:12345")
    with (
        patch("dash_extensions.enrich.DashProxy.run"),
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_ui_module",
            return_value="tests.mocks.solution_with_ui.ui.app",
        ),
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_definition_module",
            return_value="tests.mocks.solution_with_ui.solution.definition",
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["ui"])
        assert result.exit_code == 0
        settings = Settings()
        assert str(settings.glow_ui_host) == "0.0.0.0"
        assert settings.glow_ui_port == 3462
        assert str(settings.glow_api_host) == "127.0.0.1"
        assert settings.glow_api_port == 5432
        assert os.environ.get(GLOW_API_URL) == "http://23.4.6.145:54432"
        assert os.environ.get(GLOW_PORTAL_URL) == "http://0.0.0.1234:12345"
        assert os.environ.get(GLOW_WS_EVENTS_ADDR) == "ws://23.4.6.145:54432"


def test_glow_engine_ui_glow_ws_events_addr_is_configurable_via_env_var(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(GLOW_WS_EVENTS_ADDR, "ws://0.0.0.0:8080")
    with (
        patch("dash_extensions.enrich.DashProxy.run"),
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_ui_module",
            return_value="tests.mocks.solution_with_ui.ui.app",
        ),
        patch(
            "ansys.saf.glow.cli._cli_entry_point.get_definition_module",
            return_value="tests.mocks.solution_with_ui.solution.definition",
        ),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["ui"])
        assert result.exit_code == 0
        assert os.environ.get(GLOW_API_URL) == "http://127.0.0.1:5432"
        assert os.environ.get(GLOW_WS_EVENTS_ADDR) == "ws://0.0.0.0:8080"


def test_glow_engine_ui_with_solution():
    verify_run_server(
        ["ui", "--solution", "tests.mocks.solution_with_ui.main"],
        expected_definition_module="tests.mocks.solution_with_ui.solution.definition",
        expected_ui_module="tests.mocks.solution_with_ui.ui.app",
    )


def test_glow_engine_ui_with_solution_rare_structure():
    verify_run_server(
        ["ui", "--solution", "tests.mocks.solution_with_ui_rare_structure.minimal_main"],
        expected_definition_module="tests.mocks.solutions.minimal_solution",
        expected_ui_module="tests.mocks.solution_with_ui_rare_structure.my_ui.my_app",
    )


def test_glow_engine_ui_with_compiled_solution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "compiled_mocks" / "solution_with_ui"
    copy_solution(MOCKS_DIR / "solution_with_ui", solution_dir, compile_solution=True)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["ui", "--solution", "compiled_mocks.solution_with_ui.main"],
        expected_definition_module="tests.mocks.solution_with_ui.solution.definition",
        expected_ui_module="tests.mocks.solution_with_ui.ui.app",
    )


def test_glow_engine_ui_with_compiled_solution_rare_structure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "compiled_mocks" / "solution_with_ui_rare_structure"
    copy_solution(MOCKS_DIR / "solution_with_ui_rare_structure", solution_dir, compile_solution=True)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["ui", "--solution", "compiled_mocks.solution_with_ui_rare_structure.minimal_main"],
        expected_definition_module="tests.mocks.solutions.minimal_solution",
        expected_ui_module="tests.mocks.solution_with_ui_rare_structure.my_ui.my_app",
    )


def test_glow_engine_ui_with_solution_without_ui():
    verify_run_server(
        ["ui", "--solution", "tests.mocks.solution_without_ui.main"],
        expected_exception="Error: The ui app module cannot be omitted in this configuration or mode",
    )


def test_glow_engine_ui_with_solution_using_path(tmp_path: Path):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_with_ui_in_ansys"
    copy_solution(MOCKS_DIR / "solution_with_ui_in_ansys", solution_dir, compile_solution=False)
    verify_run_server(
        ["ui", "--solution", str(solution_dir / "main.py")],
        expected_definition_module="ansys.solutions.solution_with_ui_in_ansys.solution.definition",
        expected_ui_module="ansys.solutions.solution_with_ui_in_ansys.ui.app",
    )


def test_glow_engine_ui_with_solution_using_path_rare_structure(tmp_path: Path):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_with_ui_in_ansys_rare_structure"
    copy_solution(
        MOCKS_DIR / "solution_with_ui_in_ansys_rare_structure",
        solution_dir,
        compile_solution=False,
    )
    verify_run_server(
        ["ui", "--solution", str(solution_dir / "minimal_main.py")],
        expected_definition_module="ansys.solutions.solution_with_ui_in_ansys_rare_structure.my_solution.my_definition",
        expected_ui_module="ansys.solutions.solution_with_ui_in_ansys_rare_structure.my_ui.my_app",
    )


def test_glow_engine_ui_with_solution_using_compiled_path(tmp_path: Path):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_with_ui_in_ansys"
    copy_solution(MOCKS_DIR / "solution_with_ui_in_ansys", solution_dir, compile_solution=True)
    verify_run_server(
        ["ui", "--solution", str(solution_dir / "main.pyc")],
        expected_definition_module="ansys.solutions.solution_with_ui_in_ansys.solution.definition",
        expected_ui_module="ansys.solutions.solution_with_ui_in_ansys.ui.app",
    )


def test_glow_engine_ui_with_solution_using_compiled_path_rare_structure(tmp_path: Path):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_with_ui_in_ansys_rare_structure"
    copy_solution(
        MOCKS_DIR / "solution_with_ui_in_ansys_rare_structure",
        solution_dir,
        compile_solution=True,
    )
    verify_run_server(
        ["ui", "--solution", str(solution_dir / "minimal_main.pyc")],
        expected_definition_module="ansys.solutions.solution_with_ui_in_ansys_rare_structure.my_solution.my_definition",
        expected_ui_module="ansys.solutions.solution_with_ui_in_ansys_rare_structure.my_ui.my_app",
    )


def test_glow_engine_ui_with_context_from_solution():
    with patch("ansys.saf.glow.cli._cli_entry_point.run_ui") as run_ui_mock:
        runner = CliRunner()
        definition_module = importlib.import_module("tests.mocks.solution_with_ui.solution.definition")
        ui_module = importlib.import_module("tests.mocks.solution_with_ui.ui.app")
        runner.invoke(cli, ["ui"], obj=SolutionModule(definition_module, ui_module))
        definition_module = run_ui_mock.call_args_list[0][0][2]
        assert isinstance(definition_module, ModuleType)
        assert definition_module.__name__ == "tests.mocks.solution_with_ui.solution.definition"
        ui_module = run_ui_mock.call_args_list[0][0][3]
        assert isinstance(ui_module, ModuleType)
        assert ui_module.__name__ == "tests.mocks.solution_with_ui.ui.app"


def test_glow_engine_ui_with_context_from_solution_without_ui():
    runner = CliRunner()
    definition_module = importlib.import_module("tests.mocks.solution_with_ui.solution.definition")
    r = runner.invoke(cli, ["ui"], obj=SolutionModule(definition_module))
    assert r.exit_code == 1
    assert r.output.startswith("Error: The ui app module cannot be omitted in this configuration or mode")


def test_glow_engine_ui_with_autodiscovery(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_with_ui_in_ansys"
    copy_solution(MOCKS_DIR / "solution_with_ui_in_ansys", solution_dir, compile_solution=False)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["ui"],
        expected_definition_module="ansys.solutions.solution_with_ui_in_ansys.solution.definition",
        expected_ui_module="ansys.solutions.solution_with_ui_in_ansys.ui.app",
    )


def test_glow_engine_ui_with_autodiscovery_rare_structure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_with_ui_in_ansys_rare_structure"
    copy_solution(
        MOCKS_DIR / "solution_with_ui_in_ansys_rare_structure",
        solution_dir,
        compile_solution=False,
    )
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    expected_error = (
        "Error: Failed to find a viable solution entry point.\n"
        "None of the following directories contain main.py or main.pyc files:\n"
        f"{str(solution_dir)}"
    )

    # Mocking the find_spec() result because we may have dependencies in the tests group that are in th
    # ansys.solutions namespace
    class MockSpec:
        submodule_search_locations = [str(solution_dir.parent)]  # pyright: ignore[reportUnannotatedClassAttribute]

    with patch("importlib.util.find_spec", return_value=MockSpec):
        verify_run_server(["ui"], expected_exception=expected_error)


def test_glow_engine_ui_with_autodiscovery_compiled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_with_ui_in_ansys"
    copy_solution(MOCKS_DIR / "solution_with_ui_in_ansys", solution_dir, compile_solution=True)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["ui"],
        expected_definition_module="ansys.solutions.solution_with_ui_in_ansys.solution.definition",
        expected_ui_module="ansys.solutions.solution_with_ui_in_ansys.ui.app",
    )


def test_glow_engine_ui_with_autodiscovery_without_ui(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    solution_dir = tmp_path / "src" / "ansys" / "solutions" / "solution_without_ui_in_ansys"
    copy_solution(MOCKS_DIR / "solution_without_ui_in_ansys", solution_dir, compile_solution=False)
    monkeypatch.syspath_prepend(str(tmp_path / "src"))  # pyright: ignore[reportUnknownMemberType]
    verify_run_server(
        ["ui"],
        expected_exception="Error: The ui app module cannot be omitted in this configuration or mode",
    )


@pytest.mark.parametrize("env_var", [GLOW_PROJECT_FILES_DIRECTORY])
def test_glow_engine_api_unexisting_directory_created(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, env_var: str):
    unexisting_dir = tmp_path / "missing_dir"
    assert not unexisting_dir.exists()
    monkeypatch.setenv(env_var, str(unexisting_dir))
    with patch("uvicorn.run"):
        runner = CliRunner()
        result = runner.invoke(cli, ["api", "--definition", "tests.mocks.solutions.minimal_solution"])
        assert result.exit_code == 0
        assert unexisting_dir.exists()


def test_glow_engine_api_wrong_sqlite_location_raise_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(GLOW_DATABASE_LOCATION, "__wrong_directory_path__/glow.db")
    runner = CliRunner()
    result = runner.invoke(cli, ["api", "--definition", "tests.mocks.solutions.minimal_solution"])
    assert "The system cannot find directory for the Sqlite DB file" in result.output


def test_glow_engine_api_correct_postgres_location(monkeypatch: pytest.MonkeyPatch):
    # Pydantic >= 2.5 has a breaking change where one of the forward slashes in GLOW_DATABASE_LOCATION disappears
    monkeypatch.setenv(GLOW_DATABASE_TYPE, "postgresql")
    monkeypatch.setenv(GLOW_DATABASE_LOCATION, "postgresql://glow:glow@127.0.0.1:5432")
    with patch("uvicorn.run"):
        runner = CliRunner()
        result = runner.invoke(cli, ["api", "--definition", "tests.mocks.solutions.minimal_solution"])
        assert result.exit_code == 0
        settings = Settings()
        assert settings.glow_database_type == DatabaseType.PostgreSql
        assert settings.glow_database_location == PostgresDsn("postgresql://glow:glow@127.0.0.1:5432")


def test_glow_engine_api_wrong_postgres_location_raise_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(GLOW_DATABASE_TYPE, "postgresql")
    monkeypatch.setenv(GLOW_DATABASE_LOCATION, "__wrong_directory_path__/glow.db")
    runner = CliRunner()
    result = runner.invoke(cli, ["api", "--definition", "tests.mocks.solutions.minimal_solution"])
    assert "Invalid database location for PostgreSql database" in result.output


def test_glow_engine_ui_dotenv_provide_default():
    with patch("dash_extensions.enrich.DashProxy.run"):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".env").write_text(
                f"{GLOW_UI_HOST}=0.0.0.0\n{GLOW_UI_PORT}=5678\n{GLOW_PORTAL_URL}=http://localhost:1234\n{GLOW_API_URL}=http://localhost:5555",
            )
            runner.invoke(cli, ["ui", "--solution", "tests.mocks.solution_with_ui.main"])
            settings = Settings()  # type: ignore
            assert str(settings.glow_ui_host) == "0.0.0.0"
            assert settings.glow_ui_port == 5678
            assert os.environ.get(GLOW_PORTAL_URL) == "http://localhost:1234"
            assert os.environ.get(GLOW_API_URL) == "http://localhost:5555"
            assert os.environ.get(GLOW_WS_EVENTS_ADDR) == "ws://localhost:5555"


def test_glow_engine_ui_env_var_override_dotenv(monkeypatch: pytest.MonkeyPatch):
    with patch("dash_extensions.enrich.DashProxy.run"):
        monkeypatch.setenv(GLOW_UI_PORT, "1111")
        monkeypatch.setenv(GLOW_API_URL, "http://localhost:2222")
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".env").write_text(
                f"{GLOW_UI_HOST}=0.0.0.0\n{GLOW_UI_PORT}=5678\n{GLOW_PORTAL_URL}=http://localhost:1234\n{GLOW_API_URL}=http://localhost:5555",
            )
            runner.invoke(cli, ["ui", "--solution", "tests.mocks.solution_with_ui.main"])
            settings = Settings()  # type: ignore
            assert str(settings.glow_ui_host) == "0.0.0.0"
            assert settings.glow_ui_port == 1111
            assert os.environ.get(GLOW_PORTAL_URL) == "http://localhost:1234"
            assert os.environ.get(GLOW_API_URL) == "http://localhost:2222"
            assert os.environ.get(GLOW_WS_EVENTS_ADDR) == "ws://localhost:2222"


def test_glow_engine_ui_cli_arg_override_env_var():
    with patch("dash_extensions.enrich.DashProxy.run"):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".env").write_text(
                f"{GLOW_UI_HOST}=0.0.0.0\n{GLOW_UI_PORT}=5678\n{GLOW_PORTAL_URL}=http://localhost:1234\n{GLOW_API_URL}=http://localhost:5555",
            )
            runner.invoke(
                cli,
                [
                    "ui",
                    "--solution",
                    "tests.mocks.solution_with_ui.main",
                    "--port",
                    "9999",
                    "--api-server-url",
                    "http://0.0.0.0:8080",
                ],
            )
            settings = Settings()  # type: ignore
            assert str(settings.glow_ui_host) == "0.0.0.0"
            assert settings.glow_ui_port == 9999
            assert os.environ.get(GLOW_PORTAL_URL) == "http://localhost:1234"
            assert os.environ.get(GLOW_API_URL) == "http://0.0.0.0:8080"
            assert os.environ.get(GLOW_WS_EVENTS_ADDR) == "ws://0.0.0.0:8080"


def test_glow_engine_ui_env_file_option_override_default_dotenv():
    with patch("dash_extensions.enrich.DashProxy.run"):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".env").write_text(f"{GLOW_UI_PORT}=5578\n{GLOW_API_URL}=http://localhost:1234")  # .env in cwd
            env_file = Path("dir") / ".env"
            env_file.parent.mkdir(exist_ok=True, parents=True)
            env_file.write_text(
                f"{GLOW_UI_HOST}=0.0.0.0\n{GLOW_PORTAL_URL}=http://localhost:3333\n{GLOW_API_URL}=http://localhost:5555",
            )
            runner.invoke(cli, ["ui", "--solution", "tests.mocks.solution_with_ui.main", "--env-file", "dir/.env"])
            assert os.environ.get(GLOW_UI_PORT) is None
            assert os.environ.get(GLOW_UI_HOST) == "0.0.0.0"
            assert os.environ.get(GLOW_PORTAL_URL) == "http://localhost:3333"
            assert os.environ.get(GLOW_API_URL) == "http://localhost:5555"
            assert os.environ.get(GLOW_WS_EVENTS_ADDR) == "ws://localhost:5555"


def test_glow_engine_ui_cli_arg_override_env_file():
    with patch("dash_extensions.enrich.DashProxy.run"):
        runner = CliRunner()
        with runner.isolated_filesystem():
            env_file = Path("dir") / ".env"
            env_file.parent.mkdir(exist_ok=True, parents=True)
            env_file.write_text(f"{GLOW_UI_PORT}=1111\n{GLOW_API_URL}=http://localhost:2222")
            runner.invoke(
                cli,
                [
                    "ui",
                    "--solution",
                    "tests.mocks.solution_with_ui.main",
                    "--env-file",
                    "dir/.env",
                    "--port",
                    "9090",
                    "--portal-ui-url",
                    "http://0.0.0.0:2323",
                ],
            )
            settings = Settings()  # type: ignore
            assert settings.glow_ui_port == 9090
            assert str(settings.glow_ui_host) == "127.0.0.1"
            assert os.environ.get(GLOW_PORTAL_URL) == "http://0.0.0.0:2323"
            assert os.environ.get(GLOW_API_URL) == "http://localhost:2222"
            assert os.environ.get(GLOW_WS_EVENTS_ADDR) == "ws://localhost:2222"


def test_glow_expose_fastapi_app():
    spec = importlib.util.find_spec("ansys.saf.glow.api")
    assert spec
    assert spec.origin
    tree = ast.parse(Path(spec.origin).read_text())
    app_found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "app":
            app_found = True
            break
    assert app_found
