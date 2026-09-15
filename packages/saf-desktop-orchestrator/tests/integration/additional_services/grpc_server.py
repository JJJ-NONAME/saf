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
import time

import click
import grpc  # type: ignore
from grpc_health.v1 import (  # type: ignore
    health,
    health_pb2_grpc,  # type: ignore
)

from tests.integration.additional_services import greeter_pb2, greeter_pb2_grpc


class GreeterServicer(greeter_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):  # type: ignore  # noqa: N802
        response = greeter_pb2.HelloReply()  # type: ignore
        response.message = f"Hello, {request.name}!"  # type: ignore
        return response  # type: ignore


@click.command()
@click.option("--port", default=8888, type=int, help="The port serviced by the server.")
def main(port: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # type: ignore
    greeter_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)  # type: ignore
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)  # type: ignore
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    main()
