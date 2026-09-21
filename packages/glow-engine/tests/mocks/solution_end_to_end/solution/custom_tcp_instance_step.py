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

from ansys.saf.glow.solution import (
    StepModel,
    StepSpec,
    create_instance,
    instance,
    long_running,
    transaction,
)
from tests.mocks.instance_managers.mock_product_manager import MockTcpProductInstanceManager


class CustomTcpSharedInstanceStep(StepModel):
    value: str = "white"

    @transaction(self=StepSpec())
    @create_instance("custom_tcp_product_instance", MockTcpProductInstanceManager)
    @long_running
    def initialize_custom_tcp_product_instance(
        self,
        custom_tcp_product_instance: MockTcpProductInstanceManager,
    ) -> None:
        custom_tcp_product_instance.initialize(version="1")

    @transaction(self=StepSpec(upload=["value"]))
    @instance("custom_tcp_product_instance")
    def retrieve_value_custom_tcp_product_instance(
        self,
        custom_tcp_product_instance: MockTcpProductInstanceManager,
    ) -> None:
        self.value = custom_tcp_product_instance.instance.the_property

    @transaction(self=StepSpec(download=["value"]))
    @instance("custom_tcp_product_instance")
    def change_value_custom_tcp_product_instance(
        self,
        custom_tcp_product_instance: MockTcpProductInstanceManager,
    ) -> None:
        custom_tcp_product_instance.instance.the_property = "red"

    @transaction(self=StepSpec())
    @instance("custom_tcp_product_instance")
    def shutdown_custom_tcp_product_instance(self, custom_tcp_product_instance: MockTcpProductInstanceManager) -> None:
        custom_tcp_product_instance.shutdown()
