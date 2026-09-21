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

import importlib
from pathlib import Path
from types import ModuleType

from ansys.saf.desktop.orchestrator._config.schema import DEPLOYMENT_DESKTOP


def get_config_file_from_deployment(  # noqa: C901
    container_name: str,
    deployment: str,
    solution_module: str | ModuleType | None = None,
    glow_logging_configs: str | None = None,
) -> Path:
    def get_solution_definition_path() -> Path | None:
        if solution_module is not None:
            if isinstance(solution_module, str):
                solution_module_obj = importlib.import_module(solution_module)
            else:
                solution_module_obj = solution_module

            solution_module_path_str = solution_module_obj.__file__
            if solution_module_path_str is not None:
                return Path(solution_module_path_str)
        return None

    def get_config_dir_from_settings() -> Path | None:
        return None if glow_logging_configs is None else Path(glow_logging_configs)

    def get_config_dir_from_solution() -> Path | None:
        solution_definition_path = get_solution_definition_path()
        if solution_definition_path is not None and solution_definition_path.parent.name == "solution":
            # assuming that the solution definition is located at
            # path with form **/<solution name>/solution/<solution definition>.py
            # derive config file at **/<solution name>/telemetry/<deployment>/<container name>_config.yaml
            return solution_definition_path.parent.parent / "telemetry" / deployment
        return None

    def get_config_dir_from_solutions() -> Path | None:
        solution_definition_path = get_solution_definition_path()
        if solution_definition_path is not None:
            solution_dirs = [p for p in solution_definition_path.parents if p.parent.name == "solutions"]
            if solution_dirs:
                solution_dir = solution_dirs[0]
                # assuming that the solution definition is located at
                # path with form **/solutions/<solution name>/**/<solution definition>.py
                # derive config file at
                # **/solutions/<solution name>/telemetry/<deployment>/<container name>_config.yaml
                return solution_dir / "telemetry" / deployment
        return None

    def get_config_dir_from_library() -> Path | None:
        ansys = Path(__file__).parent
        while ansys.name != "ansys":
            ansys = ansys.parent
        return ansys / "saf" / "desktop" / "orchestrator" / "_telemetry" / "configs"

    config_file = ""
    for source in [
        get_config_dir_from_settings,
        get_config_dir_from_solution,
        get_config_dir_from_solutions,
        get_config_dir_from_library,
    ]:
        config_dir = source()
        if config_dir is not None:
            config_file = config_dir / f"{container_name}_config.yaml"
            if config_file.is_file():
                return config_file

    raise RuntimeError(f"python logging config yaml file is not present at {config_file}")


def get_config_file(container_name: str, solution_module: str | ModuleType) -> Path:
    return get_config_file_from_deployment(
        container_name,
        DEPLOYMENT_DESKTOP.lower(),
        solution_module,
    )
