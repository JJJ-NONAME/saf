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
import shutil
from typing import TypeVar

from ansys.saf.glow._config.const import ProductInstanceSystemType
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._core.instance.iinstance_system import IProductInstanceSystem
from ansys.saf.glow._core.instance.null_system import NullSystem
from ansys.saf.glow._core.instance.recoverystate import RecoveryStateInfo
from ansys.saf.glow._hps_auth.hps_authentication_type import HpsAuthenticationType

logger = logging.getLogger(__name__)
TRecoveryStateInfo = TypeVar("TRecoveryStateInfo", bound=RecoveryStateInfo)


def shutdown_instance(
    instance_pim_name: str,
    instance_system: IProductInstanceSystem,
    settings: Settings,
) -> None:
    if isinstance(instance_system, NullSystem):
        logger.debug(
            "The product instance system is not configured. Skipping the deletion of the product instance.",
        )
        return
    if settings.glow_product_instance_system == ProductInstanceSystemType.HPS:
        # deliberate conditional import because REP/HPS is an optional dependency
        from ansys.saf.glow._core.instance.hps_system import HpsSystem

        if (
            isinstance(instance_system, HpsSystem)
            and instance_system.auth_type == HpsAuthenticationType.KEYCLOAK_INTERACTIVE
        ):
            # Known issue: triggering the interactive authorization does a GET request to the API server that
            # timeouts when done from the same API server proc (like this DELETE request).
            logger.warning("HPS system un-authenticated. Cannot shutdown product instance.")
            return
    # This is safe just because pim_name is unique. Otherwise, we could be interfering with instances of other
    # users when using the same HPS service.
    product_instance = instance_system.get_instance(instance_pim_name)
    if product_instance:
        product_instance.delete()


def delete_instance_state_directory(
    project_files_directory: Path,
    project_id: str,
    state_directory_name: str,
) -> None:
    project_directory = (project_files_directory / project_id).resolve()
    state_directory = (project_directory / state_directory_name).resolve()

    # Guard against path traversal: only allow deleting a strict subdirectory of this project's directory.
    if state_directory.parent != project_directory:
        logger.warning(
            "Skipping state directory deletion because path is not a subdirectory of the project directory: %s",
            state_directory,
        )
        return

    if state_directory.is_dir():
        try:
            shutil.rmtree(state_directory)
        except OSError as e:
            logger.warning(f"Failed to remove instance state directory {state_directory}: {e}")
