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

import logging
from pathlib import Path
from types import ModuleType

from ansys.saf.glow._config.const import PRODUCT_INSTANCE_CONFIGS_DIR_NAME

logger = logging.getLogger(__name__)


def find_product_instance_configs_dir(solution_module: ModuleType) -> Path | None:
    # Solutions may not require defining PIM/HPS instance configurations. Thus,
    # the absence of this directory is not considered an error.
    if not solution_module.__file__ or not Path(solution_module.__file__).is_file():
        raise RuntimeError(f"Cannot find source file for solution module {solution_module.__name__}.")

    # TODO: add safe stop? right now it goes down to the absolute root path
    for parent in Path(solution_module.__file__).parents:
        instance_configs_dir = parent / PRODUCT_INSTANCE_CONFIGS_DIR_NAME
        if instance_configs_dir.is_dir():
            logger.info(f"Found directory with product instance configurations: {instance_configs_dir}.")
            return instance_configs_dir
