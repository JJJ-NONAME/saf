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

import multiprocessing
import subprocess
import sys
import time

import click
from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/health")
def health():
    return "I am healthy"


@app.get("/multiprocessing-pid")
def pid():
    mp_context = multiprocessing.get_context("spawn")
    p = mp_context.Process(target=time.sleep, args=(30,))
    p.start()
    # Need some time before returning to be sure the process is fully started
    time.sleep(0.5)
    return p.pid


@app.get("/subprocess-pid")
def subprocess_pid():
    child_process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    return child_process.pid


def launch_server(host: str, port: int):
    uvicorn.run(app, host=host, port=port)  # type: ignore


@click.command()
@click.option("--host", default="127.0.0.1", help="The host where the server runs.")
@click.option("--port", default=8888, type=int, help="The port serviced by the server.")
def main(host: str, port: int):
    launch_server(host, port)


if __name__ == "__main__":
    main()
