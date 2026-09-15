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

# this code is designed to be loadable into older versions of python in HPS
# hence disabling ruff and black


INNER_EXEC_PYTHON_CONTENT = """# ruff: noqa
# fmt: off
import argparse
import importlib
import inspect
import json
import shutil
import pickle
import base64
import json
import subprocess
from pathlib import Path
from typing import Type, Any

from ansys.saf.glow.hps_execution import HpsExecution, HpsProduct, HpsExecutionContext, HpsExecutionFunctionality

###############################################
# this is a duplication of the code at
# src/ansys/saf/glow/_hps_parametric_studies/serialization.py

_ESCAPED_CHARACTERS = ["0", "+", "/", "="]

def encode_data_for_hps(data: Any) -> str:
    try:
        byte_string = pickle.dumps(data)
    except AttributeError as e:
        raise RuntimeError(
            f"The SAF HPS API does not support the serialization of {type(data)} objects.  In this case: {data}",
        ) from e
    base64_bytes = base64.b64encode(byte_string)
    base64_str = base64_bytes.decode("utf-8")
    for index, char in enumerate(_ESCAPED_CHARACTERS):
        base64_str = base64_str.replace(char, f"0{index}")
    return base64_str

def decode_data_from_hps(encoded_str: str) -> Any:
    base64_str = ""
    escaped = False
    for c in encoded_str:
        if escaped:
            escaped = False
            base64_str += _ESCAPED_CHARACTERS[int(c)]
        elif c == "0":
            escaped = True
        else:
            base64_str += c
    base64_bytes = base64_str.encode("utf-8")
    byte_string = base64.b64decode(base64_bytes)
    data = pickle.loads(byte_string)
    return data

def encode_string_for_hps(s: str) -> str:
    encoded = ""
    for c in s:
        if c.isascii() and (c.isalnum() or c == " "):
            encoded += c
        else:
            # insert string hex value of c between two '_' characters
            encoded += f"_{ord(c):x}_"
    return encoded


def decode_string_from_hps(s: str) -> str:
    decoded = ""
    in_hexadecimal = False
    hexadecimal = ""
    for c in s:
        if c == "_":
            if in_hexadecimal:
                decoded += chr(int(hexadecimal, 16))
                hexadecimal = ""
                in_hexadecimal = False
            else:
                in_hexadecimal = True
        elif in_hexadecimal:
            hexadecimal += c
        else:
            decoded += c
    if in_hexadecimal:
        raise RuntimeError(f'When decoding from HPS string "{s}", it ends with an unmatched "_" character')
    return decoded

# end of duplicationed code
#########################################################################

class HpsProductImpl(HpsProduct):

    def __init__(self, data : Any) -> None:
        self._data = data

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def version(self) -> str:
        return self._data["version"]

    @property
    def executable(self) -> Path:
        return Path(self._data["executable"])


class HpsExecutionContextImpl(HpsExecutionContext):

    def __init__(self) -> None:
        self._input_parameters : dict[str, Any] = {}
        self._data : Any = None
        self._parse_data()
        self._parse_input_parameters()

    def _add_input_parameter(self, parameter_name: str, parameter_value_str: str):
        if parameter_name in self.pickled_parameters:
            parameter_value = decode_data_from_hps(parameter_value_str)
        elif parameter_value_str == "True":
            parameter_value = True
        elif parameter_value_str == "False":
            parameter_value = False
        elif parameter_value_str.startswith("'"):
            parameter_value = parameter_value_str[1:-1]
            if parameter_name not in self._data["input_file_keys"]:
                parameter_value = decode_string_from_hps(parameter_value)
        else:
            try:
                parameter_value = int(parameter_value_str)
            except Exception:
                try:
                    parameter_value = float(parameter_value_str)
                except Exception as e:
                    raise RuntimeError(message) from e
        self._input_parameters[parameter_name] = parameter_value

    def _parse_input_parameters(self):
        input_file = Path("input.txt")

        if not input_file.is_file():
            raise RuntimeError(f"input parameters file at {input_file} not found")

        content = input_file.read_text()

        if not content.strip():
            return

        for line_number, input_line in enumerate(content.splitlines(), 1):
            message = f"unable to parse line {line_number} in {input_file} got: {input_line}"
            line_parts = input_line.split("=", 1)
            if len(line_parts) != 2:
                raise RuntimeError(message)
            self._add_input_parameter(line_parts[0], line_parts[1])

    def _parse_data(self):
        data_file = Path("inner_context.json")

        if not data_file.is_file():
            raise RuntimeError(f"context file at {data_file} not found")

        self._data = json.loads(data_file.read_text())

    @property
    def pickled_parameters(self) -> list[str]:
        return self._data["pickled_parameters"]

    @property
    def input_parameters(self) -> dict[str, Any]:
        return self._input_parameters

    @property
    def required_output_parameters(self) -> list[str]:
        return self._data["required_output_parameters"]

    @property
    def required_output_files(self) -> dict[str, str]:
        return self._data["required_output_files"]

    @property
    def required_output_directories(self) -> dict[str, str]:
        return self._data["required_output_directories"]

    @property
    def products(self) -> list[HpsProduct]:
        return [HpsProductImpl(item) for item in self._data["products"]]


class HpsExecutionFunctionalityImpl(HpsExecutionFunctionality):

    def __init__(self) -> None:
        self._context = HpsExecutionContextImpl()

    def run_and_capture_output(self, args : list[Any], keyword_args: dict[str, Any]):

        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.STDOUT

        print(f"Executing: {args}")
        print("-" * 90)
        with subprocess.Popen(args, **kwargs) as proc:
            if proc.stdout is not None:
                for line in proc.stdout:
                    msg = line.decode("utf-8").rstrip()
                    print(msg)
        print("-" * 90)

        if proc.returncode == 0:
            print("The application completed successfully.")
        else:
            print(f"The application exited with code {proc.returncode}.")
            raise Exception(f"The application exited with code {proc.returncode}")

    @property
    def context(self) -> HpsExecutionContext:
        return self._context

def find_execution(module_name: str) -> Type[HpsExecution]:
    script_module = importlib.import_module(module_name)
    execution_classes = [
        value
        for _, value in inspect.getmembers(
            script_module, lambda x: inspect.isclass(x) and issubclass(x, HpsExecution) and x != HpsExecution
        )
    ]

    if not execution_classes:
        raise RuntimeError(f"{module_name} module does not define a 'HpsExecution' class.")

    if len(execution_classes) > 1:
        raise RuntimeError(f"{module_name} module defines more than one 'HpsExecution' class.")

    return execution_classes[0]

def archive_output_directories() -> None:
    context_file = Path("inner_context.json")
    context = json.loads(context_file.read_text())
    required_output_directories = context.get("required_output_directories", {})
    for output_name, output_path in required_output_directories.items():
        output_base_dir = output_path or output_name
        try:
            archive_name = Path(output_base_dir).name
            archive_path = Path(output_base_dir) / f"{archive_name}.zip"
            if archive_path.exists():
                raise RuntimeError(f"{archive_path} already exists.")
            shutil.make_archive(
                base_name=archive_name,
                format="zip",
                root_dir=output_base_dir,
                base_dir=".",
            )
        except Exception as e:
            raise RuntimeError(f"Error while packaging {output_base_dir} for transfer to solution: {e}")

def process_result(impl: HpsExecutionFunctionalityImpl, output_parameters: dict[str, Any]) -> None:
    output_content = ""
    for output_parameter, value in output_parameters.items():
        if output_parameter in impl.context.pickled_parameters:
            value = encode_data_for_hps(value)
        elif isinstance(value, str):
            value = f"'{encode_string_for_hps(value)}'"
        output_content += f"{output_parameter}={value}\\n"

    Path("output.txt").write_text(output_content)

    archive_output_directories()

def main():
    # parse arguments
    # using argparse because its builtin and we have no control over the local execution environment here

    parser = argparse.ArgumentParser()
    parser.add_argument("script_module")
    args = parser.parse_args()
    execution_class = find_execution(args.script_module)
    execution = execution_class()
    impl = HpsExecutionFunctionalityImpl()
    execution.load_impl(impl)
    result = execution.execute()
    process_result(impl, result)

if __name__ == "__main__":
    main()

# fmt: on
"""
