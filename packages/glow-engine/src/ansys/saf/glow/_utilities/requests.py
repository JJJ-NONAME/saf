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

from fastapi import Request
from starlette.datastructures import URL


def build_api_url_for_internal_requests_from_request(
    request: Request,
    port: int,
    path: str,
) -> URL:
    return request.url.replace(hostname="localhost", port=port, path=path)


def build_params_for_hps_auth_request(
    hps_server_url: str | None = None,
    client_id: str | None = None,
) -> dict[str, str]:
    params: dict[str, str] = {}
    params.update({"hps_server_url": hps_server_url} if hps_server_url else {})
    params.update({"client_id": client_id} if client_id else {})
    return params
