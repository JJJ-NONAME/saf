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

import httpx2
from opentelemetry import propagate


class InjectTraceTransport(httpx2.HTTPTransport):
    """
    Custom httpx transport that injects trace headers into the HTTP request and then passes the request
    to the default transport (httpx2.HTTPTransport) for further handling.

    Since httpx currently does not allow to modify the request object through event hooks, this is the
    recommended way of doing it. For more information: https://httpx2.pydantic.dev/advanced/event-hooks/
    """

    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        propagate.inject(request.headers)
        return super().handle_request(request)


class AsyncInjectTraceTransport(httpx2.AsyncHTTPTransport):
    """
    Custom httpx transport that injects trace headers into the HTTP request and then passes the request
    to the default transport (httpx2.AsyncHTTPTransport) for further handling.

    Since httpx currently does not allow to modify the request object through event hooks, this is the
    recommended way of doing it. For more information: https://httpx2.pydantic.dev/advanced/event-hooks/
    """

    async def handle_async_request(
        self,
        request: httpx2.Request,
    ) -> httpx2.Response:
        propagate.inject(request.headers)
        return await super().handle_async_request(request)
