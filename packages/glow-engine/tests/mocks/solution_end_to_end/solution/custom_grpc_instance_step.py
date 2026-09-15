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
import time

from ansys.hps.client import ClientError  # pyright: ignore[reportMissingTypeStubs]

from ansys.saf.glow.solution import (
    StepModel,
    StepSpec,
    create_instance,
    instance,
    long_running,
    transaction,
)
from tests.mocks.instance_managers.mock_product_manager import (
    MockGrpcCustomHostProductInstanceManager,
    MockGrpcProductInstanceManager,
    MockSecureGrpcCustomProductInstanceManager,
    MockSecureGrpcMtlsProductInstanceManager,
    MockSecureGrpcProductInstanceManager,
)

logger = logging.getLogger(__name__)


class CustomGrpcSharedInstanceStep(StepModel):
    value: str = "white"

    @transaction(self=StepSpec())
    @create_instance("custom_grpc_product_instance", MockGrpcProductInstanceManager)
    @long_running
    def initialize_custom_grpc_product_instance(
        self,
        custom_grpc_product_instance: MockGrpcProductInstanceManager,
    ) -> None:
        custom_grpc_product_instance.initialize(version="1")

    @transaction(self=StepSpec())
    @create_instance("custom_grpc_product_instance", MockGrpcProductInstanceManager)
    def initialize_custom_grpc_product_instance_sync(
        self,
        custom_grpc_product_instance: MockGrpcProductInstanceManager,
    ) -> None:
        custom_grpc_product_instance.initialize(version="1")

    @transaction(self=StepSpec())
    @create_instance("custom_grpc_product_instance", MockGrpcProductInstanceManager)
    def initialize_and_retrieve_properties_custom_grpc_product_instance(
        self,
        custom_grpc_product_instance: MockGrpcProductInstanceManager,
    ) -> list[str]:
        custom_grpc_product_instance.initialize(version="1")
        return custom_grpc_product_instance.instance.the_properties  # type: ignore

    @transaction(self=StepSpec())
    @create_instance("custom_grpc_product_secure_instance", MockSecureGrpcProductInstanceManager)
    @long_running
    def initialize_custom_grpc_product_secure_instance(
        self,
        custom_grpc_product_secure_instance: MockSecureGrpcProductInstanceManager,
    ) -> None:
        custom_grpc_product_secure_instance.initialize(version="1")

    @transaction(self=StepSpec())
    @create_instance("custom_grpc_product_secure_2_instance", MockSecureGrpcCustomProductInstanceManager)
    @long_running
    def initialize_custom_grpc_product_secure_2_instance(
        self,
        custom_grpc_product_secure_2_instance: MockSecureGrpcCustomProductInstanceManager,
    ) -> None:
        custom_grpc_product_secure_2_instance.initialize(version="1")

    @transaction(self=StepSpec())
    @create_instance("custom_grpc_product_secure_mtls_instance", MockSecureGrpcMtlsProductInstanceManager)
    @long_running
    def initialize_custom_grpc_product_secure_mtls_instance(
        self,
        custom_grpc_product_secure_mtls_instance: MockSecureGrpcMtlsProductInstanceManager,
    ) -> None:
        custom_grpc_product_secure_mtls_instance.initialize(version="1")

    @transaction(self=StepSpec())
    @create_instance("custom_host_grpc_product_instance", MockGrpcCustomHostProductInstanceManager)
    @long_running
    def initialize_custom_host_grpc_product_instance(
        self,
        custom_host_grpc_product_instance: MockGrpcCustomHostProductInstanceManager,
    ) -> None:
        custom_host_grpc_product_instance.initialize(version="1")

    @transaction(self=StepSpec(upload=["value"]))
    @instance("custom_grpc_product_instance")
    def retrieve_value_custom_grpc_product_instance(
        self,
        custom_grpc_product_instance: MockGrpcProductInstanceManager,
    ) -> None:
        self.value = custom_grpc_product_instance.instance.the_property

    @transaction(self=StepSpec(upload=["value"]))
    @instance("custom_grpc_product_instance")
    @long_running
    def query_instance_management_on_loop_lr(
        self,
        custom_grpc_product_instance: MockGrpcProductInstanceManager,
        timeout: int,
    ) -> None:
        # Using custom_grpc_product_instance.instance would actually not test any connection with the instance system,
        # and thus not verify if the connection with the system is still valid.
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                self.value = str(custom_grpc_product_instance.is_instance_healthy())
            except ClientError as e:
                # avoid race condition where HPS Client detects the expiration and fails to refresh before GLOW does.
                logger.warning(str(e))
            time.sleep(1)

    @transaction(self=StepSpec(upload=["value"]))
    @instance("custom_grpc_product_instance")
    def query_instance_management_on_loop(
        self,
        custom_grpc_product_instance: MockGrpcProductInstanceManager,
        timeout: int,
    ) -> None:
        # Using custom_grpc_product_instance.instance would actually not test any connection with the instance system,
        # and thus not verify if the connection with the system is still valid.
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                self.value = str(custom_grpc_product_instance.is_instance_healthy())
            except ClientError as e:
                # avoid race condition where HPS Client detects the expiration and fails to refresh before GLOW does.
                logger.warning(str(e))
            time.sleep(1)

    @transaction(self=StepSpec(upload=["value"]))
    @instance("custom_grpc_product_instance")
    @long_running
    def retrieve_value_custom_grpc_product_instance_long_running(
        self,
        custom_grpc_product_instance: MockGrpcProductInstanceManager,
    ) -> None:
        self.value = custom_grpc_product_instance.instance.the_property

    @transaction(self=StepSpec(download=["value"]))
    @instance("custom_grpc_product_instance")
    def change_value_custom_grpc_product_instance(
        self,
        custom_grpc_product_instance: MockGrpcProductInstanceManager,
    ) -> None:
        custom_grpc_product_instance.instance.the_property = "red"

    @transaction(self=StepSpec())
    @instance("custom_grpc_product_instance")
    def shutdown_custom_grpc_product_instance(
        self,
        custom_grpc_product_instance: MockGrpcProductInstanceManager,
    ) -> None:
        custom_grpc_product_instance.shutdown()

    @transaction(self=StepSpec())
    @instance("custom_grpc_product_secure_instance")
    def shutdown_custom_grpc_product_secure_instance(
        self,
        custom_grpc_product_secure_instance: MockSecureGrpcProductInstanceManager,
    ) -> None:
        custom_grpc_product_secure_instance.shutdown()

    @transaction(self=StepSpec())
    @instance("custom_grpc_product_secure_2_instance")
    def shutdown_custom_grpc_product_secure_2_instance(
        self,
        custom_grpc_product_secure_2_instance: MockSecureGrpcCustomProductInstanceManager,
    ) -> None:
        custom_grpc_product_secure_2_instance.shutdown()

    @transaction(self=StepSpec())
    @instance("custom_host_grpc_product_instance")
    def shutdown_custom_host_grpc_product_instance(
        self,
        custom_host_grpc_product_instance: MockGrpcCustomHostProductInstanceManager,
    ) -> None:
        custom_host_grpc_product_instance.shutdown()

    @transaction(self=StepSpec())
    @instance("custom_grpc_product_secure_mtls_instance")
    def shutdown_custom_grpc_product_secure_mtls_instance(
        self,
        custom_grpc_product_secure_mtls_instance: MockSecureGrpcMtlsProductInstanceManager,
    ) -> None:
        custom_grpc_product_secure_mtls_instance.shutdown()
