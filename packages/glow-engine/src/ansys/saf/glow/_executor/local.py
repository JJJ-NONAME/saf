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

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from ansys.saf.glow._bdm.multiplexor import SafMultiplexorStorageScopeFactory
    from ansys.saf.glow._config.settings import Settings
    from ansys.saf.glow._core.blob_managers import HpsBlobManager
    from ansys.saf.glow._core.instance.iinstance_system import IProductInstanceSystemFactory
    from ansys.saf.glow._core.step_model import StepModel


class MethodLocal(threading.local):
    """Thread-local object used to pass thread-local data to transactions.

    This is used in case like the following, where the unshared product instance manager
    needs to to have access to thread-local data, such as project directory and method directory,
    so that it can be created properly.

    >>>    @transaction(self=StepSpec(download=["x"]))
    >>>    def unshared_instance_transaction(self):
    >>>        with Mechanical():  # needs to have access to project directory, method directory etc...
    >>>            ...

    (Indeed, a product instance manager needs to know the project directory, the temp method directory etc...
    but since the constructor of the unshared product instance does not take those values in, we need a way to
    access those in a thread-safe manner.)
    """

    project_directory: Path
    """The absolute path of the directory containing the current project as seen by the solution.
    For example: %APPDATA%/ansys/glow/<solution_name>/project_files/<project_id>"""

    instance_system_factory: IProductInstanceSystemFactory
    """A factory creating a product instance system (HPS os PIM)."""

    settings: Settings
    """GLOW configuration variables read from the environment variables."""

    project_display_name: str
    """The project display name used for a human-friendly project directory name in Minerva"""

    hps_blob_manager: HpsBlobManager
    """The HPS blob manager used for creating HPS storage scopes."""

    access_token: str | None = None
    """The access token used for authentication."""

    multiplexor_storage_factory: SafMultiplexorStorageScopeFactory
    """The BDM Multiplexor storage scope factory that can create storage scopes."""

    step_type: type[StepModel]
    """The type of the step model containing the transaction method being executed."""


transaction_local = MethodLocal()
