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

import contextlib
from enum import StrEnum
import logging
from pathlib import Path
import socket
import time
from typing import Protocol

from google.protobuf import empty_pb2
import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc
import httpx2

from tests.mocks.mock_products import grpc_mock_product_pb2, grpc_mock_product_pb2_grpc

logger = logging.getLogger(__name__)


class TransportMode(StrEnum):
    """Enum containing the different modes of connection."""

    INSECURE, UDS, MTLS, WNUA = ("insecure", "uds", "mtls", "wnua")


class IMockProductClient(Protocol):
    def healthy(self) -> bool: ...

    @property
    def the_property(self) -> str: ...

    @the_property.setter
    def the_property(self, value: str) -> None: ...

    def store_given_absolute_path(self, value: str) -> None: ...

    def restore_given_absolute_path(self, value: str) -> None: ...

    @property
    def server_version(self) -> str: ...

    def close(self): ...


class MockGrpcProductClient(IMockProductClient):
    def __init__(self, port: str | int, host: str = "localhost") -> None:
        self._channel = grpc.insecure_channel(f"{host}:{port}")
        self._mock_product_stub = grpc_mock_product_pb2_grpc.GrpcMockProductStub(self._channel)
        self._health_stub = health_pb2_grpc.HealthStub(self._channel)

    def healthy(self) -> bool:
        request = health_pb2.HealthCheckRequest(service="tests.mocks.grpc_mock_product.GrpcMockProduct")
        status = self._health_stub.Check(request, wait_for_ready=True).status  # type: ignore
        return status == 1  # type: ignore

    @property
    def the_property(self) -> str:
        return self._mock_product_stub.GetProperty(empty_pb2.Empty()).value  # type: ignore

    @the_property.setter
    def the_property(self, value: str) -> None:
        request = grpc_mock_product_pb2.StringMessage(value=value)  # type: ignore
        self._mock_product_stub.SetProperty(request)  # type: ignore

    def store_given_absolute_path(self, value: str) -> None:
        request = grpc_mock_product_pb2.StringMessage(value=value)  # type: ignore
        self._mock_product_stub.StoreStateGivenAbsoluteFilePath(request)  # type: ignore

    def restore_given_absolute_path(self, value: str) -> None:
        request = grpc_mock_product_pb2.StringMessage(value=value)  # type: ignore
        self._mock_product_stub.RestoreStateGivenAbsoluteFilePath(request)  # type: ignore

    @property
    def server_version(self) -> str:
        return self._mock_product_stub.GetVersion(empty_pb2.Empty()).value  # type: ignore

    def close(self):
        self._channel.close()


class MockSecureGrpcProductClient(MockGrpcProductClient):
    def __init__(
        self,
        port: str | int,
        host: str = "localhost",
        transport_mode: TransportMode = TransportMode.INSECURE,
        uds_dir: Path | None = None,
        uds_id: str | None = None,
        certs_dir: Path | None = None,
    ) -> None:
        match transport_mode:
            case TransportMode.WNUA:
                target = f"{host}:{port}"
                # Windows Named User Authentication: TCP localhost with special options
                options = (("grpc.default_authority", "localhost"),)
                self._channel = grpc.insecure_channel(target, options=options)

            case TransportMode.UDS:
                if uds_dir is None or uds_id is None:
                    raise ValueError("UDS transport requires both uds_dir and uds_id to be specified.")
                # Generate socket filename with optional ID
                socket_filename = f"mockproduct-{uds_id}.sock"
                target = f"unix:{uds_dir / socket_filename}"
                # If using UDS transport, set default authority to localhost
                # see https://github.com/grpc/grpc/issues/34305
                #
                # This is specially critical when running against the C# server
                options = (("grpc.default_authority", "localhost"),)
                self._channel = grpc.insecure_channel(target, options=options)

            # Create the gRPC channel
            case TransportMode.MTLS:
                target = f"{host}:{port}"
                # TLS setup using environment variables
                if certs_dir is None:
                    raise ValueError("certs_dir must be specified for MTLS transport mode.")

                cert_file = certs_dir / "client.crt"
                key_file = certs_dir / "client.key"
                ca_file = certs_dir / "ca.crt"

                missing = [f.as_posix() for f in (cert_file, key_file, ca_file) if not f.exists()]
                if missing:
                    raise RuntimeError(f"Missing required TLS file(s) for mutual TLS: {', '.join(missing)}")

                certificate_chain = cert_file.read_bytes()
                private_key = key_file.read_bytes()
                root_certificates = ca_file.read_bytes()

                creds = grpc.ssl_channel_credentials(
                    root_certificates=root_certificates,
                    private_key=private_key,
                    certificate_chain=certificate_chain,
                )
                self._channel = grpc.secure_channel(target, creds)
                logger.info(f"Using gRPC+mTLS on {target} (cert: {cert_file}, key: {key_file}, server CA: {ca_file})")

            case TransportMode.INSECURE:
                target = f"{host}:{port}"
                logger.warning(
                    f"Starting gRPC client without TLS on {target}. Modification of these configurations "
                    "is not recommended. Please see the documentation for your installed product "
                    "for additional information.",
                )
                self._channel = grpc.insecure_channel(target)

        logger.info(f"Connecting to MockProduct using: {transport_mode.value} -> {target}")
        self._mock_product_stub = grpc_mock_product_pb2_grpc.GrpcMockProductStub(self._channel)
        self._health_stub = health_pb2_grpc.HealthStub(self._channel)


class MockDummyProductClient(MockGrpcProductClient):
    def healthy(self) -> bool:
        return True

    @property
    def the_property(self) -> str:
        return "blue"

    @the_property.setter
    def the_property(self, value: str) -> None: ...

    def store_given_absolute_path(self, value: str) -> None:
        Path(value).touch()

    def restore_given_absolute_path(self, value: str) -> None: ...


class MockHttpProductClient(IMockProductClient):
    def __init__(self, port: int, host: str = "localhost") -> None:
        self._client = httpx2.Client(base_url=f"http://{host}:{port}")

    def close(self) -> None:
        self._client.close()

    def healthy(self) -> bool:
        try:
            r = self._client.get("/health")
        except httpx2.ConnectError:
            return False
        return r.status_code == 200

    @property
    def the_property(self) -> str:
        return self._client.get("/property").json()["value"]

    @the_property.setter
    def the_property(self, value: str) -> None:
        self._client.post("/property", json={"value": value}).raise_for_status()

    def store_given_absolute_path(self, value: str) -> None:
        self._client.post("/property:store", json={"value": value}).raise_for_status()

    def restore_given_absolute_path(self, value: str) -> None:
        self._client.post("/property:restore", json={"value": value}).raise_for_status()

    @property
    def server_version(self) -> str:
        return self._client.get("/version").json()["value"]

    @property
    def pid(self) -> int:
        return self._client.get("/get_pid").json()["value"]

    def harakiri(self) -> None:
        with contextlib.suppress(httpx2.ReadError):
            # On Windows, the httpx2 client raises a ReadError exception
            self._client.post("/harakiri")
        # wait for product to die
        tries = 0
        while self.healthy() and tries < 10:
            tries += 1
            time.sleep(0.5)
        if self.healthy():
            raise RuntimeError("Failed to perform harakiri. Instance still healthy.")

    def be_healthy(self) -> None:
        self._client.post("/be_healthy")

    def be_unhealthy(self) -> None:
        self._client.post("/be_unhealthy")


class MockTcpProductClient(IMockProductClient):
    def __init__(self, port: int, host: str = "localhost") -> None:
        self._host = host
        self._port = port

    def _send_message(self, message: str) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((self._host, self._port))
            sock.sendall(bytes(message + "\n", "utf-8"))
            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            return received

    @property
    def the_property(self) -> str:
        received = self._send_message("get_property|")
        return received

    @the_property.setter
    def the_property(self, value: str) -> None:
        self._send_message(f"set_property|{value}")

    def store_given_absolute_path(self, value: str) -> None:
        self._send_message(f"store_given_absolute_path|{value}")

    def restore_given_absolute_path(self, value: str) -> None:
        self._send_message(f"restore_given_absolute_path|{value}")

    def healthy(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            try:
                sock.connect((self._host, self._port))
                return True
            except Exception:
                return False

    @property
    def server_version(self) -> str:
        received = self._send_message("get_property|")
        return received

    def close(self) -> None: ...


class MockSystemProductClient(IMockProductClient):
    def __init__(self, instance_file_path: Path) -> None:
        self._instance_file_path = instance_file_path

    @property
    def the_property(self) -> str:
        if not self._instance_file_path.is_file():
            raise FileNotFoundError("Instance file not found.")
        return "blue"

    def healthy(self) -> bool:
        return True

    @the_property.setter
    def the_property(self, value: str) -> None: ...

    def store_given_absolute_path(self, value: str) -> None: ...

    def restore_given_absolute_path(self, value: str) -> None: ...

    @property
    def server_version(self) -> str:
        return self._instance_file_path.stem.split("__")[-2]

    def close(self): ...
