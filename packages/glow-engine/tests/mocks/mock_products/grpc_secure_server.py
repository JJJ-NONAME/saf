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

import atexit
from concurrent import futures
from enum import StrEnum
from logging import Logger, getLogger
import os
from pathlib import Path

import click
from google.protobuf import empty_pb2
import grpc

# Dependencies allowing to add Health Check
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from tests.mocks.mock_products import grpc_mock_product_pb2, grpc_mock_product_pb2_grpc

_IS_WINDOWS = os.name == "nt"

# Global variable to track socket path for cleanup
_socket_path_to_cleanup: Path | None = None


def cleanup_socket():
    """Clean up the UDS socket file if it exists."""
    global _socket_path_to_cleanup
    if _socket_path_to_cleanup:
        try:
            _socket_path_to_cleanup.unlink(missing_ok=True)
            print(f"Cleaned up socket file: {_socket_path_to_cleanup}")
        except OSError as e:
            print(f"Warning: Could not remove socket file {_socket_path_to_cleanup}: {e}")
        _socket_path_to_cleanup = None


class TransportMode(StrEnum):
    """Enum containing the different modes of connection."""

    INSECURE, UDS, MTLS, WNUA = ("insecure", "uds", "mtls", "wnua")


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


def serve(  # noqa: C901
    transport_mode: TransportMode,
    version: str,
    host: str,
    port: int,
    certs_dir: str | None,
    uds_dir: str | None,
    uds_id: str | None,
) -> None:
    # addresses is a list of strings of the form <ipaddr>:<port>
    if transport_mode == TransportMode.WNUA:
        if not _IS_WINDOWS:
            raise RuntimeError("WNUA (Windows Named User Authentication) is only supported on Windows")

        # Import WNUA module only on Windows
        import tests.mocks.mock_products.wnua as wnua

        server = wnua.create_wnua_server(max_workers=10)  # type: ignore
    else:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    grpc_mock_product_pb2_grpc.add_GrpcMockProductServicer_to_server(  # pyright: ignore[reportUnknownMemberType]
        MockProductServicer(version),
        server,
    )

    # Configure the server based on transport mode
    match transport_mode:
        case TransportMode.WNUA:
            target = f"127.0.0.1:{port}"
            server.add_insecure_port(target)  # pyright: ignore[reportUnknownMemberType]
            print(f"Server listening on localhost TCP {target} with Windows Named User Authentication")

        case TransportMode.UDS:
            # Generate socket filename with optional ID
            if uds_dir:
                uds_path = Path(uds_dir)
                uds_path.mkdir(parents=True, exist_ok=True)
            else:
                raise RuntimeError("UDS directory must be specified for UDS transport mode.")
            socket_filename = f"mockproduct-{uds_id}.sock" if uds_id else "mock.sock"
            socket_path = uds_path / socket_filename

            # Check if socket file already exists (indicating another server is running)
            if socket_path.exists():
                raise RuntimeError(
                    f"UDS socket file already exists at {socket_path}. "
                    "Another server may already be running on this socket. "
                    "Please stop the existing server or use a different UDS ID. "
                    "See option --uds-id.",
                )

            # Track socket path for cleanup and register atexit handler
            global _socket_path_to_cleanup
            _socket_path_to_cleanup = socket_path
            atexit.register(cleanup_socket)

            target = f"unix:{socket_path}"
            server.add_insecure_port(target)  # pyright: ignore[reportUnknownMemberType]
            print(f"Server listening on Unix Domain Socket {socket_path}")

        case TransportMode.MTLS:
            if certs_dir is None:
                raise RuntimeError("Certificates directory must be specified for MTLS transport mode.")
            target = f"{host}:{port}"
            # TLS configuration
            cert_file = Path(certs_dir) / "server.crt"
            key_file = Path(certs_dir) / "server.key"
            ca_file = Path(certs_dir) / "ca.crt"

            # All three files are required for mutual TLS
            missing = [str(f) for f in (cert_file, key_file, ca_file) if not f.exists()]
            if missing:
                raise RuntimeError(f"Missing required TLS file(s) for mutual TLS: {', '.join(missing)}")

            certificate_chain = cert_file.read_bytes()
            private_key = key_file.read_bytes()
            root_certificates = ca_file.read_bytes()
            server_credentials = grpc.ssl_server_credentials(
                [(private_key, certificate_chain)],
                root_certificates=root_certificates,
                require_client_auth=True,
            )
            server.add_secure_port(target, server_credentials)  # pyright: ignore[reportUnknownMemberType]
            print(f"Server listening on gRPC+mTLS {target} (cert: {cert_file}, key: {key_file}, client CA: {ca_file})")

        case TransportMode.INSECURE:
            target = f"{host}:{port}"
            # Throw a warning for insecure connections...
            print(
                f"Starting gRPC client without TLS on {target}. Modification of these configurations "
                "is not recommended. Please see the documentation for your installed product "
                "for additional information.",
            )
            server.add_insecure_port(target)  # pyright: ignore[reportUnknownMemberType]
            print(f"Server listening on gRPC {target}")

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

    server.start()  # pyright: ignore[reportUnknownMemberType]

    for service in services + (overall_server_health,):  # pyright: ignore[reportUnknownVariableType]
        health_servicer.set(
            service,  # pyright: ignore[reportUnknownArgumentType]
            health_pb2.HealthCheckResponse.SERVING,
        )

    print(f"Server started with transport: {transport_mode.value} -> {target}")
    server.wait_for_termination()  # pyright: ignore[reportUnknownMemberType]


@click.command()
@click.argument("port", type=int)
@click.option("--version", type=str, default="1")
@click.option("--host", type=str, default="localhost", help="Host to connect to (default: localhost)")
@click.option("--uds-dir", type=str, help="Directory path for UDS socket files")
@click.option("--uds-id", type=str, help="Optional ID for UDS socket file naming (greeter-<id>.sock)")
@click.option(
    "--certs-dir",
    type=str,
    envvar="ANSYS_GRPC_CERTIFICATES",
    help="Directory path for certificate files (default: env var ANSYS_GRPC_CERTIFICATES)",
)
@click.option(
    "--transport-mode",
    default=TransportMode.INSECURE,
    type=click.Choice(TransportMode, case_sensitive=False),  # pyright: ignore[reportArgumentType]
    help="Transport mode to be used",
)
def main(
    port: int,
    version: str,
    host: str,
    uds_dir: str | None,
    uds_id: str | None,
    certs_dir: str | None,
    transport_mode: TransportMode,
):
    if version not in ["1", "2", "222"]:
        raise ValueError("Version must be one of '1', '2', or '222'.")
    serve(
        transport_mode=transport_mode,
        host=host,
        port=port,
        certs_dir=certs_dir,
        uds_dir=uds_dir,
        uds_id=uds_id,
        version=version,
    )


if __name__ == "__main__":
    main()
