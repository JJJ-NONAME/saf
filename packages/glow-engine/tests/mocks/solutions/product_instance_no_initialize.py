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

from typing import Any

from ansys.saf.glow._core.instance.manager import ProductInstanceManager
from ansys.saf.glow.solution import (
    Solution,
    StepModel,
    StepsModel,
    create_instance,
    instance,
    transaction,
)
from tests.mocks.instance_managers.mock_product_manager import InternalMockGrpcProductInstanceManagerImpl, MockStateInfo
from tests.mocks.mock_products.client import MockGrpcProductClient


class MockProductInstanceManagerNoInitialize(
    ProductInstanceManager[MockGrpcProductClient, MockStateInfo],
    instance_manager_impl_type=InternalMockGrpcProductInstanceManagerImpl,
):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)


class ProductInstanceNoInitialize(StepModel):
    @transaction()
    @create_instance("x", MockProductInstanceManagerNoInitialize)
    def create(self, x: MockProductInstanceManagerNoInitialize) -> None:
        x.initialize()  # type: ignore

    @instance("x")  # type: ignore
    @transaction()
    def do_thing(self, x: MockProductInstanceManagerNoInitialize) -> None:
        print(x.instance.the_property)


class Steps(StepsModel):
    no_initialize_step: ProductInstanceNoInitialize


class InstanceManagerNoInitializeTransaction(Solution):
    display_name: str = "No initialize"
    steps: Steps
