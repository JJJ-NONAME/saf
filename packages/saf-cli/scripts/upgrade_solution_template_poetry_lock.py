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

import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import venv

from dotenv import load_dotenv

from ansys.saf.cli._config.const import UI_FRAMEWORKS

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upgrade poetry.lock files for solution templates",
    )
    parser.add_argument(
        "-p",
        "--packages",
        type=str,
        default="",
        help=(
            "Comma-separated list of packages to explicitly update (e.g., 'package1,package2'). "
            "Use it for packages that weren't modified in the pyproject.toml."
        ),
    )
    args = parser.parse_args()
    packages_to_update = [pkg.strip() for pkg in str(args.packages).split(",") if pkg.strip()]

    saf_cli_src_dir = Path(__file__).parent.parent / "src" / "ansys" / "saf" / "cli"
    assert saf_cli_src_dir.is_dir()

    pyproject_file = (
        saf_cli_src_dir
        / "_solutions"
        / "templates"
        / "solution"
        / "{{cookiecutter.__solution_name}}"
        / "pyproject.toml"
    )
    assert pyproject_file.is_file()
    # can't use toml to load it because it contains cookiecutter variables
    poetry_version = [
        line.split(" = ")[-1].replace('"', "")
        for line in pyproject_file.read_text().splitlines()
        if line.startswith("build-system-version = ")
    ][0]
    assert poetry_version

    if platform.system() == "Windows":
        saf_exec = Path.cwd() / ".venv" / "Scripts" / "saf.exe"
        if not saf_exec.is_file():
            saf_exec = Path.cwd() / ".venv" / "Scripts" / "saf.cmd"
    else:
        saf_exec = Path.cwd() / ".venv" / "bin" / "saf"
    assert saf_exec.is_file()

    starting_working_directory = Path.cwd()

    poetry_lock_dest_dirs: dict[str, str] = {
        "dash": "dash",
        "awc-dash": "awc",
        "none": "no_ui",
    }

    for ui_framework in UI_FRAMEWORKS:
        print(f"Processing UI framework: {ui_framework}")

        poetry_lock_dest = (
            saf_cli_src_dir
            / "_solutions"
            / "templates"
            / "solution"
            / "{{cookiecutter.__solution_name}}"
            / "lock_files"
            / poetry_lock_dest_dirs[ui_framework]
            / "poetry.lock"
        )
        assert poetry_lock_dest.is_file()

        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                os.chdir(tmp_dir)

                solution_name = f"solution-{ui_framework}"
                print(f"Creating new solution {solution_name} at {tmp_dir}...")
                subprocess.check_output(
                    [
                        str(saf_exec),
                        "new",
                        "--solution-name",
                        solution_name,
                        "--solution-display-name",
                        "temp",
                        "--ui-framework",
                        ui_framework,
                        "--namespace",
                        "my_temp",
                    ],
                )
                solution_root_dir = Path(tmp_dir) / solution_name
                assert solution_root_dir.is_dir()
                os.chdir(solution_root_dir)

                solution_venv_dir = solution_root_dir / ".venv"
                print(f"Creating venv at {solution_venv_dir}...")
                solution_venv_dir.mkdir(parents=True)
                venv.EnvBuilder(with_pip=True).create(solution_venv_dir)
                os.environ["VIRTUAL_ENV"] = str(solution_venv_dir)

                pip_exec = (
                    (solution_venv_dir / "Scripts" / "pip.exe")
                    if platform.system() == "Windows"
                    else (solution_venv_dir / "bin" / "pip")
                )
                assert pip_exec.is_file()
                print(f"Installing poetry {poetry_version}...")
                subprocess.check_output([str(pip_exec), "install", f"poetry=={poetry_version}"])

                # load required poetry credentials for auth
                print(f"Loading .env file from {solution_root_dir / '.env'}...")
                load_dotenv(solution_root_dir / ".env")

                print("Upgrading poetry.lock....")
                poetry_exec = (
                    (solution_venv_dir / "Scripts" / "poetry.exe")
                    if platform.system() == "Windows"
                    else (solution_venv_dir / "bin" / "poetry")
                )
                assert poetry_exec.is_file()
                subprocess.check_output([str(poetry_exec), "lock"])

                # Update specific packages if provided
                if packages_to_update:
                    print(f"Updating packages: {packages_to_update}")
                    try:
                        subprocess.check_output([str(poetry_exec), "update"] + packages_to_update)
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to update packages {packages_to_update}:\n{e.output.decode()}")
                        raise e
                print(f"Copying poetry.lock to destination {poetry_lock_dest}...")
                solution_poetry_lock = solution_root_dir / "poetry.lock"
                assert solution_poetry_lock.is_file()
                shutil.copyfile(solution_poetry_lock, poetry_lock_dest)
            except Exception as e:
                print(e)
                sys.exit(1)
            finally:
                os.chdir(starting_working_directory)
