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

from ansys.saf.product_manager.fluent import Fluent2DDPSolverInternalManager, Fluent2DDPSolverManager


class InternalCustomFluent2DDPSolverManager(Fluent2DDPSolverInternalManager):
    PRODUCT_NAME = "custom-fluent-2ddp-solver"


class CustomFluent2DDPSolverManager(
    Fluent2DDPSolverManager,
    instance_manager_impl_type=InternalCustomFluent2DDPSolverManager,
): ...
