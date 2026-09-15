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
from ansys.saf.glow._core.instance.recoverystate import RecoveryStateInfo
from ansys.saf.glow.solution import (
    Solution,
    StepModel,
    StepsModel,
    create_instance,
    instance,
    transaction,
)
from tests.mocks.instance_managers.mock_product_manager import InternalMockGrpcProductInstanceManagerImpl
from tests.mocks.mock_products.client import MockGrpcProductClient


class MockStateInfo(RecoveryStateInfo): ...


class MockProductInstanceManagerWrongParameter(  # pyright: ignore
    ProductInstanceManager[MockGrpcProductClient, MockStateInfo],
    instance_manager_impl_type=InternalMockGrpcProductInstanceManagerImpl,  # pyright: ignore
):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def initialize(self, wrong_parameter: int):
        super().start(wrong_parameter)


class ProductInstanceNoImplStep(StepModel):
    @transaction()
    @create_instance("x", MockProductInstanceManagerWrongParameter)
    def create(self, x: MockProductInstanceManagerWrongParameter) -> None:
        x.initialize(wrong_parameter=2)

    @instance("x")  # type: ignore
    @transaction()
    def do_thing(self, x: MockProductInstanceManagerWrongParameter) -> None:
        print(x.instance.the_property)


class Steps(StepsModel):
    no_impl_step: ProductInstanceNoImplStep


class InstanceManagerWrongParamTransaction(Solution):
    display_name: str = "No impl"
    steps: Steps
