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

"""Mock gRPC secure server with customized CLI flags and env-var-driven configuration.

Thin adapter around ``grpc_secure_server.serve()`` that matches the flag style and
environment variables defined in ``MockSecureGRPCCustomInstanceVersionConfiguration``:

* ``-transport <mode>`` instead of ``--transport-mode=<mode>``
* Port from ``MOCK_PORT`` env var (no positional CLI arg).
* Host from ``MOCK_HOST`` env var (no ``--host`` CLI arg).
* UDS directory from ``MOCK_UDS_DIR`` env var (no ``--uds-dir`` CLI arg).
* Certificates from ``ANSYS_GRPC_CERTIFICATES`` env var (no ``--certs-dir`` CLI arg).
* UDS socket filename is not configurable and follows the ``mockproduct-<PORT>.sock`` pattern.
"""

import os

import click

from tests.mocks.mock_products.grpc_secure_server import TransportMode, serve


@click.command()
@click.option("--version", type=str, default="1")
@click.option(
    "-transport",
    "transport_mode",
    default=TransportMode.INSECURE,
    type=click.Choice(TransportMode, case_sensitive=False),  # pyright: ignore[reportArgumentType]
    help="Transport mode to be used",
)
def main(
    version: str,
    transport_mode: TransportMode,
) -> None:
    port_str = os.environ.get("MOCK_PORT")
    if not port_str:
        raise RuntimeError("MOCK_PORT environment variable must be set.")
    port = int(port_str)

    if version not in ["1", "2", "222"]:
        raise ValueError("Version must be one of '1', '2', or '222'.")

    serve(
        transport_mode=transport_mode,
        version=version,
        host=os.environ.get("MOCK_HOST", "localhost"),
        port=port,
        certs_dir=os.environ.get("ANSYS_GRPC_CERTIFICATES"),
        uds_dir=os.environ.get("MOCK_UDS_DIR"),
        uds_id=str(port),
    )


if __name__ == "__main__":
    main()
