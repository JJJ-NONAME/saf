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

import time

from opentelemetry.metrics import Counter, Histogram, Meter  # type: ignore
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class MetricsMiddleware:
    def __init__(self, app: ASGIApp, app_name: str, meter: Meter) -> None:
        self.app = app
        self._app_name = app_name
        self._meter = meter
        self._register_metrics()

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        async def send_wrapper(message: Message):
            if message["type"] == "http.response.start":
                labels["status_code"] = message["status"]
                self.request_status_code.add(1, labels)  # type: ignore
            return await send(message)

        method = scope.get("method")
        path = scope.get("path")

        labels = {
            "path": path,
            "http_method": method,
        }

        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        try:
            before_time = time.perf_counter()
            response = await self.app(scope, receive, send_wrapper)
        except BaseException as e:
            labels["status_code"] = str(HTTP_500_INTERNAL_SERVER_ERROR)
            self.request_status_code.add(1, labels)  # type: ignore
            raise e from None
        else:
            after_time = time.perf_counter()
            request_duration = after_time - before_time
            self.request_duration.record(request_duration, labels)  # type: ignore

        return response

    def _register_metrics(self) -> None:
        self.request_status_code: Counter = self._meter.create_counter(
            name="http.server.status_code",
            description="the status code of the API requests",
        )

        self.request_duration: Histogram = self._meter.create_histogram(
            name="http.server.duration",
            description="measures the duration of the inbound HTTP request",
            unit="ms",
        )
