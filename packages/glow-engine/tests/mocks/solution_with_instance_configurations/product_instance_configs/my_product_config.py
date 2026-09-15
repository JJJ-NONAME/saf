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
import platform

from ansys.saf.glow.solution.products.config import (
    IProductInstanceConfiguration,
    IProductInstanceVersionConfiguration,
    ISoftware,
    ServiceType,
    Software,
)


class MyProductInstanceVersionConfiguration(IProductInstanceVersionConfiguration):
    def __init__(self, version: str) -> None:
        self._version = version

    @property
    def service_name(self) -> str:
        return "grpc"

    @property
    def execution_command(self) -> str:
        return "${EXECUTABLE} -ng -grpcsrv ${PORT}"

    @property
    def exe_path_for_pim(self) -> str:
        for var_name, path in os.environ.items():
            ansys_var_name_prefix = "AWP_ROOT"
            if var_name.startswith(ansys_var_name_prefix):
                version_str = var_name[len(ansys_var_name_prefix) :]
                try:
                    int(version_str)
                except Exception:
                    continue
                # we don't support any version preceding 222
                # because that was the version that introduced gRPC support
                if version_str != self._version or int(self._version) < 222:
                    continue
                bin_folder = Path(path) / "Framework" / "bin"
                if platform.system() == "Windows":
                    return str(bin_folder / "Win64" / "RunWB2.exe")
                return str(bin_folder / "Linux64" / "runwb2")
        raise ValueError(f"Ansys Mechanical version {self._version} cannot be found")

    @property
    def environment(self) -> dict[str, str]:
        return {}

    @property
    def software_requirements(self) -> list[ISoftware]:
        return [Software(name="Ansys Mechanical", version=f"20{self._version[0:2]} R{self._version[2:]}")]

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.GRPC


class MyProductInstanceConfiguration(IProductInstanceConfiguration):
    @property
    def product_name(self) -> str:
        return "my_product"

    @property
    def versions(self) -> list[str]:
        return ["222", "231"]

    def get_version_configuration(self, version: str) -> IProductInstanceVersionConfiguration:
        return MyProductInstanceVersionConfiguration(version)
