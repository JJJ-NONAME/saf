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
    InstanceManager,
    ProductInstanceManager,
    RecoveryStateInfo,
    Solution,
    StepModel,
    StepsModel,
    transaction,
)
from tests.mocks.mock_products.client import MockGrpcProductClient


class InvalidRecoveryStateInfo(RecoveryStateInfo):
    required_field: str  # No default value - even if this isn't used in the solution, it will fail during import
    default_field: str = "default value"


class InternalInvalidInstanceManager(InstanceManager[MockGrpcProductClient, InvalidRecoveryStateInfo]):
    def initialize(self, required_value: str) -> None:
        self.initialize_service("grpc")
        self.recovery_state_info = InvalidRecoveryStateInfo(required_field=required_value)

    def get_client_object_implement(self, hostname: str, port: int) -> MockGrpcProductClient:
        return MockGrpcProductClient(port, hostname)

    def close_client_object_implement(self) -> None:
        pass

    def save_state_implement(self) -> None:
        pass

    def load_state_implement(self) -> None:
        pass

    def shutdown_implement(self) -> None:
        pass

    @classmethod
    def get_product_name_implement(cls) -> str:
        return "mock-grpc-product"


class InvalidInstanceManager(
    ProductInstanceManager[MockGrpcProductClient, InvalidRecoveryStateInfo],
    instance_manager_impl_type=InternalInvalidInstanceManager,
):
    def initialize(self, required_value: str) -> None:
        pass


class InvalidRecoveryStateInfoNotUsedStep(StepModel):
    @transaction()
    def create_instance_with_invalid_recovery_state(self) -> str:
        return "test value"


class Steps(StepsModel):
    valid_step: InvalidRecoveryStateInfoNotUsedStep


class InvalidRecoveryStateInfoNotUsedSolution(Solution):
    display_name: str = "Invalid Recovery State Info Not Used Solution"
    steps: Steps
