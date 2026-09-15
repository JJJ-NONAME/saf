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

from ansys.saf.glow._core.instance.manager import InstanceManager, ProductInstanceManager
from ansys.saf.glow._core.instance.recoverystate import RecoveryStateInfo


class MyProduct:
    @property
    def result(self) -> int:
        return 99

    def change_state(self) -> None:
        pass


class InternalEmptyInstanceManager(InstanceManager[MyProduct, RecoveryStateInfo]):
    def initialize(self): ...


class EmptyInstanceManager(
    ProductInstanceManager[MyProduct, RecoveryStateInfo],
    instance_manager_impl_type=InternalEmptyInstanceManager,
):
    def initialize(self):
        pass


class OtherInstanceManager(
    ProductInstanceManager[MyProduct, RecoveryStateInfo],
    instance_manager_impl_type=InternalEmptyInstanceManager,
):
    def initialize(self):
        pass
