# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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
from enum import Enum, auto
import os
from pathlib import Path
import platform
import shutil
import tempfile
from tempfile import mkdtemp
from time import sleep
import typing
from unittest.mock import patch

import psutil

from ansys.saf.testing._common.network import get_random_free_port
from ansys.saf.testing.process import Process

PIM_LOCALHOSTS = ["localhost", "127.0.0.1"]
FLAGSHIPS_EXE = ["ansysedt.exe", "ansyswbu.exe"]


class TransportMode(Enum):
    """Enum containing the different modes of connection."""

    UNKNOWN = auto()
    INSECURE = auto()
    UDS = auto()
    MTLS = auto()
    WNUA = auto()


class PimProcess(Process):
    _PIM_DEFINITIONS_CONFIG_PATH_ENV = "AENEID_ROOT"
    _GLOW_PIM_SOCKET_PATH = "GLOW_PIM_SOCKET_PATH"
    _GLOW_PRODUCT_BINDING_HOST = "GLOW_PRODUCT_BINDING_HOST"

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int | None = None,
        certs_dir: str | None = None,
        uds_dir: Path | None = None,
        uds_id: str | None = None,
        insecure: bool = False,
        product_configs_dir: Path | None = None,
        product_binding_host: str | None = None,
    ) -> None:
        self._is_windows = platform.system() == "Windows"
        self._transport_mode = TransportMode.UNKNOWN
        self._ip = host
        self._port = port
        self._uds_dir = uds_dir
        self._uds_id = uds_id
        self._socket_path: Path | None = None
        self._certs_dir = certs_dir
        self._health_route = ""
        self._insecure = insecure
        self._definitions_dir: Path | None = None
        self._product_configs_dir = product_configs_dir
        self._product_binding_host = product_binding_host

        self._assign_transport_mode()
        args = self._configure_args()

        super().__init__(args, bg=True)

    def _assign_transport_mode(self) -> None:
        if self._insecure:
            if not self._port:
                self._port = get_random_free_port()
            self._transport_mode = TransportMode.INSECURE
        elif self._is_windows:
            if not self._port:
                self._port = get_random_free_port()
            self._transport_mode = TransportMode.WNUA if self._ip in PIM_LOCALHOSTS else TransportMode.MTLS
        else:
            if self._ip in PIM_LOCALHOSTS:
                self._port = None
                if not self._uds_dir:
                    self._uds_dir = Path(tempfile.gettempdir())
                socket_filename = f"pim-{self._uds_id}.sock" if self._uds_id is not None else "pim.sock"
                self._socket_path = self._uds_dir / socket_filename
                self._transport_mode = TransportMode.UDS
            else:
                if not self._port:
                    self._port = get_random_free_port()
                self._transport_mode = TransportMode.MTLS

    def _configure_args(self) -> list[str]:
        # conditional import to keep pim-light-server as optional dependency
        try:
            from ansys.saf.pim_light_server.locate import (  # pyright: ignore[reportMissingImports]
                get_pim_light_exe_and_args,  # pyright: ignore[reportUnknownVariableType]
            )
        except ModuleNotFoundError as ex:
            raise ModuleNotFoundError(
                "The package 'ansys-saf-pim-light-server' is not installed or could not be found.",
            ) from ex

        args: list[str] = typing.cast(list[str], get_pim_light_exe_and_args())
        args.append(f"--transport-mode={self._transport_mode.name}")
        if self._insecure:
            # insecure mode, always basic http with host and port.
            args.append(f"--urls=http://{self._ip}:{self._port}")
        elif not self._socket_path:
            # non-socket mode
            scheme = "http" if self._transport_mode != TransportMode.MTLS else "https"
            args.append(f"--urls={scheme}://{self._ip}:{self._port}")
        else:
            # socket mode
            if self._uds_dir:
                args.append(f"--uds-dir={self._uds_dir}")
            if self._uds_id:
                args.append(f"--uds-id={self._uds_id}")
        if self._certs_dir:
            args.append(f"--certs-dir={self._certs_dir}")

        return args

    @property
    def port(self) -> int | None:
        return self._port

    @property
    def socket_path(self) -> Path | None:
        return self._socket_path

    @property
    def uri(self) -> str:
        return f"unix:{self._socket_path.as_posix()}" if self._socket_path else f"{self._ip}:{self._port}"

    def get_pim_output(self) -> list[str]:
        return self.output

    def _generate_pim_configs(self) -> None:
        # conditional import to keep saf-product-configuration as optional dependency
        from ansys.saf.product_configuration.manager.configurations_manager import ProductInstanceConfigurationsManager
        from ansys.saf.product_configuration.pim.config_writer import PimLightConfigWriter

        instance_config_mgr = ProductInstanceConfigurationsManager()
        if self._product_configs_dir and self._product_configs_dir.is_dir():
            instance_config_mgr.load_configurations(self._product_configs_dir)
        self._definitions_dir = Path(mkdtemp())
        configurations_dir = self._definitions_dir / "Configurations"
        configurations_dir.mkdir()
        print(f"Pim product configurations directory: {configurations_dir}")

        modified_env = os.environ.copy()
        if self._product_binding_host:
            modified_env[self._GLOW_PRODUCT_BINDING_HOST] = self._product_binding_host
        else:
            modified_env.pop(self._GLOW_PRODUCT_BINDING_HOST, None)
        with patch.dict(os.environ, modified_env):
            for config in instance_config_mgr.list_configurations():
                PimLightConfigWriter().write_config(configurations_dir, config)

    def start(self) -> None:
        self._generate_pim_configs()
        if not self._definitions_dir:
            raise RuntimeError("PIM definitions directory was not set.")
        self._env[self._PIM_DEFINITIONS_CONFIG_PATH_ENV] = self._definitions_dir.as_posix()
        if self._socket_path:
            self._env[self._GLOW_PIM_SOCKET_PATH] = self._socket_path.as_posix()

        print(f"Launching PIM Light Server with args: {self._cmd}")
        super().start()
        self._wait_for_healthy()

    def stop(self) -> None:
        super().stop()
        if self._definitions_dir:
            shutil.rmtree(self._definitions_dir, ignore_errors=True)

    def _terminate(self, process: psutil.Process, timeout: int = 0) -> None:
        try:
            if process.name() in FLAGSHIPS_EXE and platform.system() == "Linux":
                # The ansysedt.exe process on Linux is spawned by the ansysedt wrapper.
                # Killing it with process.terminate() does not kill ansysedt.exe, which
                # if not killed properly when pim is restarted, it makes the new ansysedt
                # instance behave very slowly.
                process.kill()
            else:
                process.terminate()
            if timeout > 0:
                process.wait(timeout)
        except psutil.NoSuchProcess:
            pass

    def _wait_for_healthy(self):
        # conditional imports to keep grpcio and grpcio-health-checking as optional dependencies
        import grpc
        from grpc_health.v1 import (
            health_pb2,
            health_pb2_grpc,
        )

        def _create_channel() -> grpc.Channel:
            match self._transport_mode:
                case TransportMode.INSECURE:
                    return grpc.insecure_channel(f"{self._ip}:{self._port}{self._health_route}")
                case TransportMode.MTLS:
                    if self._certs_dir is None:
                        raise ValueError("MTLS cannot be used without certs_dir")
                    certificates_dir = Path(self._certs_dir)
                    creds = grpc.ssl_channel_credentials(
                        root_certificates=(certificates_dir / "ca.crt").read_bytes(),
                        private_key=(certificates_dir / "client.key").read_bytes(),
                        certificate_chain=(certificates_dir / "client.crt").read_bytes(),
                    )
                    return grpc.secure_channel(f"{self._ip}:{self._port}{self._health_route}", creds)
                case TransportMode.UDS:
                    target = f"unix:{self._socket_path}"
                    options = (("grpc.default_authority", "localhost"),)
                    return grpc.insecure_channel(target=target, options=options)
                case TransportMode.WNUA:
                    options = (("grpc.default_authority", "localhost"),)
                    return grpc.insecure_channel(f"{self._ip}:{self._port}{self._health_route}", options=options)
                case _:
                    raise ValueError(f"Invalid PIM transport mode: {self._transport_mode.name}")

        tries = 250
        with _create_channel() as channel:
            request = health_pb2.HealthCheckRequest()
            stub = health_pb2_grpc.HealthStub(channel)
            status = health_pb2.HealthCheckResponse.NOT_SERVING
            while status != health_pb2.HealthCheckResponse.SERVING and tries > 0:
                try:
                    resp = stub.Check(request)  # type: ignore
                    status = resp.status  # type: ignore
                except grpc.RpcError:
                    ...  # pim gRPC server not ready yet.
                finally:
                    sleep(0.1)
                    tries = tries - 1
            if status != health_pb2.HealthCheckResponse.SERVING:
                raise RuntimeError("unable to connect to healthy PIM server after PIM startup")
            else:
                print("Pim is healthy!")
