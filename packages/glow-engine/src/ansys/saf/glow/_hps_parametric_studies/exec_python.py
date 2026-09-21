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

# type: ignore

"""
GLOW parametric study execution script for python.
"""

EXEC_PYTHON_CONTENT = """import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution


class PythonExecution(ApplicationExecution):

    def _get_exe_path_from_venv(self, exe: str, venv: Path) -> Path:
        return venv / "Scripts" / f"{exe}.exe" if platform.system() == "Windows" else venv / "bin" / exe

    def _try_get_uv_executable(self) -> str | None:
        saf_product_environment = os.getenv("SAF_PRODUCT_ENVIRONMENT")
        log.info(f"SAF_PRODUCT_ENVIRONMENT is {saf_product_environment}")
        if saf_product_environment:
            saf_product_environment_path = Path(saf_product_environment)
            if saf_product_environment_path.is_dir():
                versions = []
                for subdir in saf_product_environment_path.iterdir():
                    if subdir.is_dir():
                        name_parts = subdir.name.split(".")
                        integer_name_parts = []
                        garbage = False
                        for name_part in name_parts:
                            try:
                                integer_name_part = int(name_part)
                            except ValueError:
                                garbage = True
                                break
                            integer_name_parts.append(integer_name_part)
                        if not garbage:
                            versions.append(tuple(integer_name_parts))
                        else:
                            log.info(f"Skipping non-version SAF product environment subdirectory {subdir}")
                versions.sort(reverse=True)

                for version in versions:
                    sub_dir = saf_product_environment_path / ".".join(map(str, version))
                    uv_exe = self._get_exe_path_from_venv("uv", sub_dir / ".venv")
                    if Path(uv_exe).is_file():
                        log.info(f"Found uv executable: {uv_exe}")
                        return uv_exe

        return None

    def _get_python_from_venv(self) -> Path:
        return self._get_exe_path_from_venv("python", Path("venv"))

    def _get_input_file_path(self, name: str) -> Path:
        inp_file = next((f for f in self.context.input_files if f["name"] == name), None)
        assert inp_file, "Input file script missing"

        inp_path_str = str(inp_file["path"])
        return Path(inp_path_str)

    def _generate_python_from_uv_tools_cache(
        self,
        python_exe: str,
        uv_exe: str,
        requirements_path: Path,
        inner_exec_python_path: Path,
        python_version: str,
        env,
    ):
        # The objective is to reuse virtual environments containing the job requirements by installing them as uv tools.
        # A hash of the requirements file and Python version determines a unique tool name, enabling venv reuse
        # across requests with identical dependencies. Random temporary directories combined with uv's built-in
        # tool management handles concurrent requests for the same requirements safely, while also caching venvs
        # for future requests.

        # Set (overriding if needed) UV_PYTHON. Using --python instead causes conflicts if UV_PYTHON is set in the
        # existing environment, because UV will ignore a local path passed through --python if it's not compatible with
        # the version specified in UV_PYTHON.
        env["UV_PYTHON"] = python_exe

        # compute a hash from the requirements file and python version to use as the name of a uv tool
        hash_source_string = requirements_path.read_text() + python_version
        m = hashlib.sha1()
        m.update(hash_source_string.encode())
        tool_name = f"saftool{m.hexdigest()}"

        # determine if the tool already exists
        tools = subprocess.check_output([uv_exe, "tool", "list"], shell=False, env=env).decode("utf-8")
        log.info(f"checking existence of tool {tool_name}")
        log.info(f"tools: {tools}")
        if tool_name not in tools:
            tool_bin = tempfile.mkdtemp()
            env["UV_TOOL_BIN_DIR"] = tool_bin
            log.info(f"Creating uv tool {tool_name} and installing it in {tool_bin}")
            with tempfile.TemporaryDirectory() as tool_project_parent_dir_str:

                # create a project for the tool
                self.run_and_capture_output(
                    [uv_exe, "init", "--package", tool_name],
                    shell=False,
                    env=env,
                    cwd=tool_project_parent_dir_str,
                )
                tool_project_dir = Path(tool_project_parent_dir_str) / tool_name

                # add the requirements file to the tool project
                self.run_and_capture_output(
                    [uv_exe, "add", "-r", str(requirements_path.absolute())],
                    shell=False,
                    env=env,
                    cwd=tool_project_dir,
                )

                # revise tool script to output the python exe path
                tool_script_path = tool_project_dir / "src" / tool_name / "__init__.py"
                assert tool_script_path.is_file(), f"tool script {tool_script_path} not found"

                log.info(f"Overwriting tool script to {tool_script_path}")
                with tool_script_path.open("w") as tool_script_file:
                    print("import sys", file=tool_script_file)
                    print("def main() -> None:", file=tool_script_file)
                    print("    print(sys.executable)", file=tool_script_file)
                log.info(f"new content of tool script {tool_script_path} is:")
                log.info(tool_script_path.read_text())

                # build a wheel containing the tool
                self.run_and_capture_output([uv_exe, "build"], shell=False, env=env, cwd=tool_project_dir)
                wheel_path = tool_project_dir / "dist" / f"{tool_name}-0.1.0-py3-none-any.whl"
                assert wheel_path.is_file(), f"wheel {wheel_path} not found"

                # install the tool into the uv tool registry
                self.run_and_capture_output(
                    [uv_exe, "tool", "install", "--force", str(wheel_path)],
                    shell=False,
                    env=env,
                    cwd=tool_project_dir,
                )

        # use uvx to return the path of the python executable that is in venv for the tool in the tool registry
        uvx_exe = Path(uv_exe).parent / ("uvx.exe" if platform.system() == "Windows" else "uvx")
        assert uvx_exe.is_file(), f"uvx executable {uvx_exe} not found"
        python_path_str = subprocess.check_output([uvx_exe, tool_name], shell=False, env=env).decode("utf-8")
        python_path = Path(python_path_str.strip())
        assert python_path.is_file(), f"python executable {python_path} not found"
        return python_path

    def execute(self):
        log.info("Starting Python execution script")

        # read and update the context with the required software
        inner_context_path = self._get_input_file_path("inner_context")
        context = json.loads(inner_context_path.read_text())
        context["products"] = self.context.software
        inner_context_path.write_text(json.dumps(context))

        # substitute the file input placeholders with the paths of the required files

        inp_path = self._get_input_file_path("input")
        inp_content = inp_path.read_text()
        for f in self.context.input_files:
            name = str(f["name"])
            # TODO - checking these are the file key names for what is builtin
            if name not in [
                "inner_context",
                "input",
                "output.txt",
                "script",
                "execution",
                "requirements",
                "inner_script_file",
                "inner_exec_python",
            ]:
                path_str = str(f["path"])
                if (
                    "directory_inputs" in context
                    and name in context["directory_inputs"]
                    and Path(path_str).absolute().exists()
                ):
                    # Create temporary extraction dir. This is needed since the zipped input directory name
                    # does not end on .zip, so the directory name already exists as a file.
                    # Extract the input directory contents on a temporary dir
                    temp_extraction_dir = Path.cwd() / "__SAF_GLOW_EXTRACTION_DIR"
                    shutil.unpack_archive(
                        (Path.cwd() / path_str).absolute().as_posix(),
                        extract_dir=temp_extraction_dir,
                        format="zip",
                    )
                    absolute_path = Path(path_str).absolute()

                    # Remove the original zipped directory file
                    absolute_path.unlink()

                    # Move the extracted files to the expected directory
                    shutil.move(temp_extraction_dir, absolute_path)

                inp_content = inp_content.replace(
                    f"__SAF_GLOW_PLACEHOLDER:{name}__",
                    Path(path_str).absolute().as_posix(),
                )
        inp_path.write_text(inp_content)

        # Identify application
        assert len(self.context.software) > 0, "unexpected software configuration"
        app = self.context.software[0]["executable"]

        # Pass env vars correctly
        env = dict(os.environ)
        env.update(self.context.environment)

        # convert script path into a module path
        script_path = self._get_input_file_path("script")
        script_name = (
            script_path.stem
            if len(script_path.parts) == 1
            else f'{".".join(script_path.parts[:-1])}.{script_path.stem}'
        )

        inner_exec_python_path = self._get_input_file_path("inner_exec_python")

        if any(f["name"] == "requirements" for f in self.context.input_files):
            # assuming that saf product environment does not contain the packages required by the job
            requirements_path = self._get_input_file_path("requirements")
            uv_exe = self._try_get_uv_executable()

            if uv_exe is None:
                log.info("using python to install requirements")
                # create virtual environment
                self.run_and_capture_output([app, "-m", "venv", "venv"], shell=False)
                app = self._get_python_from_venv()
                self.run_and_capture_output([app, "-m", "pip", "install", "-r", requirements_path], shell=False)
            else:
                log.info("using uv tool")
                python_version = self.context.software[0]["version"]
                app = self._generate_python_from_uv_tools_cache(
                    app,
                    uv_exe,
                    requirements_path,
                    inner_exec_python_path,
                    python_version,
                    env,
                )

        # Execute inner exec python which loads script.py

        if not Path(app).is_file():
            raise RuntimeError(f"python executable {app} not found")

        if not inner_exec_python_path.is_file():
            raise RuntimeError(f"inner exec python script {inner_exec_python_path} not found")

        self.run_and_capture_output([app, inner_exec_python_path, script_name], shell=False, env=env)
        log.info("End Python execution script")
"""
