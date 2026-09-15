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

from typing import TypeVar

from pydantic import ConfigDict

from ansys.saf.glow._core.livehandles import LiveHandlesModel


class RecoveryStateInfo(LiveHandlesModel):
    """A base pydantic model that can be used to save and restore product instance state information.
    A good usage example is to store the values passed to the instance manager's ``initialized`` method
    so that the same values can be reused within the ``load_state_implement``.

    In order to store recovery state info within your instance manager implementation
    (the class inheriting from ``InstanceManager[T]``) you need to:
    - define a derived class from this model: ``MyRecoveryStateInfo(RecoveryStateInfo)``
    - call ``self.recovery_state_info = my_recovery_state_info`` where ``my_recovery_state_info`` is an instance
    of MyRecoveryStateInfo: ``my_recovery_state_info = MyRecoveryStateInfo(...)``

    To restore those information, simply use: ``my_state_info = self.recovery_state_info``

    Notes
    -----
    All fields in your custom RecoveryStateInfo class must have default values.
    The class must be instantiable without any arguments.
    This is required for mocking the custom product instance manager in tests using the ``saf-sdk-testing`` package.

    When set, the recovery state info is saved automatically after ``save_state_implement`` is being called.

    Examples
    --------
    >>> class MyRecoveryStateInfo(RecoveryStateInfo):
    >>>     project_file: EntityHandle = NO_ENTITY
    >>>     product_value: int = 0

    >>> class InternalInstanceManager(InstanceManager[Product]):
    >>>
    >>>     def initialize(
    >>>         self,
    >>>         product_value: int,
    >>>         project_file: EntityHandle,
    >>>     ):
    >>>         self.initialize_service(SERVICE_NAME, version)
    >>>         recovery_state_info = MyStateInfo(
    >>>             product_value=product_value,
    >>>             project_file=project_file
    >>>         )
    >>>         # Store the recovery state info model so that it can be reused
    >>>         # when restoring the product instance and upload the project file
    >>>         # onto the product instance's protected file system.
    >>>         self.recovery_state_info = restore_state_info
    >>>
    >>>     def load_state_implement(self) -> None:
    >>>         state_info = self.recovery_state_info
    >>>         # Re-opening the product instance with the values previously stored into the
    >>>         # recovery state info
    >>>         project_file_absolute_path = self.storage_scope.get_cached(state_info.project_file)
    >>>         self.instance.open(project_file_absolute_path, state_info.product_value)
    """

    product_instance_state_dirname: str = ""
    """Name of the directory where the product instance state files are stored."""

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        revalidate_instances="always",
    )


TRecoveryStateInfo = TypeVar("TRecoveryStateInfo", bound=RecoveryStateInfo)
