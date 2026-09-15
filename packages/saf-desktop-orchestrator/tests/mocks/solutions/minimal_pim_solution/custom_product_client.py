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
import time

import httpx2


class CustomProductClient:
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
            # On Windows, the httpx client raises a ReadError exception
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
