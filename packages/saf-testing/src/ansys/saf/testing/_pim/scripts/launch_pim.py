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
import time

import click

from ansys.saf.testing._pim.process.pim_process import PimProcess


@click.command()
@click.option("--host", type=str, default="127.0.0.1", help="Bind socket to this host. [default: 127.0.0.1]")
@click.option("--port", type=int, default=None, help="Bind socket to this port. [default: None]")
def main(host: str, port: int | None):
    pim_proc = PimProcess(host=host, port=port)
    try:
        pim_proc.start()
        while True:
            time.sleep(0.5)
    finally:
        pim_proc.stop()


if __name__ == "__main__":
    main()
