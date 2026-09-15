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

from pathlib import Path
import socketserver

import click

_property: str = "blue"  # type: ignore
_version: str = "1"


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        message = self.request.recv(1024).strip()
        print(f"Received from: {self.client_address[0]}")
        print(message)
        if not message:
            return
        method_name, value = message.decode().split("|")
        method = getattr(self, method_name)
        return_value: str | None
        return_value = method() if value == "" else method(value)

        if return_value is not None:
            self.request.sendall(bytes(return_value, "utf-8"))

    def get_property(self):
        return _property

    def set_property(self, data: str):
        global _property
        _property = data

    def store_given_absolute_path(self, absolute_path: str):
        Path(absolute_path).write_text(_property)

    def restore_given_absolute_path(self, absolute_path: str):
        global _property
        _property = Path(absolute_path).read_text()

    def get_version(self):
        return _version


@click.command()
@click.argument("port", type=int)
@click.option("--version", type=str, default="1")
def main(port: int, version: str):
    if version not in ["1", "2", "222"]:
        raise ValueError("Version must be one of '1', '2', or '222'.")
    # Create the server, binding to localhost on given port
    with socketserver.TCPServer(("0.0.0.0", port), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        print("Connecting...")
        global _version
        _version = version
        server.serve_forever()


if __name__ == "__main__":
    main()
