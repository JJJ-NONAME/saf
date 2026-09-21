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

from concurrent import futures
from logging import Logger, getLogger
from pathlib import Path

import click
from google.protobuf import empty_pb2
import grpc

# Dependencies allowing to add Health Check
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from tests.mocks.mock_products import grpc_mock_product_pb2, grpc_mock_product_pb2_grpc


class MockProductServicer(grpc_mock_product_pb2_grpc.GrpcMockProductServicer):
    def __init__(self, version: str):
        self.logger: Logger = getLogger(__name__)  # Use default
        self.logger.info("Init MockProductServicer")
        self._property: str = "blue"
        self._version: str = version

    # method names are upper case to conform to gRPC norms
    def GetProperty(self, request, context):  # type: ignore  # noqa: N802
        return grpc_mock_product_pb2.StringMessage(value=self._property)  # pyright: ignore[reportCallIssue]

    def GetVersion(self, request, context):  # type: ignore  # noqa: N802
        return grpc_mock_product_pb2.StringMessage(value=self._version)  # pyright: ignore[reportCallIssue]

    def SetProperty(self, request, context):  # type: ignore  # noqa: N802
        self._property = request.value  # pyright: ignore[reportUnknownMemberType]
        return empty_pb2.Empty()

    def StoreStateGivenAbsoluteFilePath(self, request, context):  # type: ignore  # noqa: N802
        Path(request.value).parent.mkdir(  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            parents=True,
            exist_ok=True,
        )
        Path(request.value).write_text(  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            self._property,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        )
        return empty_pb2.Empty()

    def RestoreStateGivenAbsoluteFilePath(self, request, context):  # type: ignore  # noqa: N802
        self._property = Path(
            request.value,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        ).read_text()
        return empty_pb2.Empty()


def serve(addresses: list[str], version: str) -> tuple[grpc.Server, list[str]]:
    # addresses is a list of strings of the form <ipaddr>:<port>
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    grpc_mock_product_pb2_grpc.add_GrpcMockProductServicer_to_server(  # pyright: ignore[reportUnknownMemberType]
        MockProductServicer(version),
        server,
    )

    # Create a health check servicer. We use the non-blocking implementation
    # to avoid thread starvation.
    health_servicer = health.HealthServicer(
        experimental_non_blocking=True,
        experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=1),
    )
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)  # pyright: ignore[reportUnknownMemberType]

    mock_product_services = tuple(  # pyright: ignore[reportUnknownVariableType]
        service.full_name  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        for service in grpc_mock_product_pb2.DESCRIPTOR.services_by_name.values()  # pyright: ignore
    )
    services = mock_product_services + (health.SERVICE_NAME,)  # pyright: ignore[reportUnknownVariableType]
    overall_server_health = ""

    effective_address: list[str] = []
    for address in addresses:
        port = server.add_insecure_port(address)
        effective_address += ["{address}:{port}".format(address=address.split(":")[0], port=port)]

    server.start()

    for service in services + (overall_server_health,):  # pyright: ignore[reportUnknownVariableType]
        health_servicer.set(
            service,  # pyright: ignore[reportUnknownArgumentType]
            health_pb2.HealthCheckResponse.SERVING,
        )

    print("server listening on {addresses}".format(addresses=", ".join(effective_address)))
    return server, effective_address


@click.command()
@click.argument("port", type=int)
@click.option("--version", type=str, default="1")
@click.option("--host", type=str, default="0.0.0.0")
def main(port: int, version: str, host: str):
    if version not in ["1", "2", "222"]:
        raise ValueError("Version must be one of '1', '2', or '222'.")
    server, _ = serve([f"{host}:{port}"], version)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
