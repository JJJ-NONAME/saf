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

from typing import Any

from fastapi.testclient import TestClient
from httpx2 import Response

from ansys.saf.glow._core.client_exceptions import raise_for_graphql_status
from ansys.saf.glow._core.gql import get_variable_values


class TestClientGqlMock:
    """Testing GraphQl with FastAPI's TestClient setup
    does not work. Instead, the /graphql endpoint is called
    directly, as it is done on Ariadne's tests
    (e.g. https://github.com/mirumee/ariadne/blob/main/tests/asgi/test_query_execution.py)
    """

    def __init__(self, client: TestClient):
        self._client = client

    def _execute(
        self,
        request_string: str,
        variable_values: dict[str, Any],
        access_token: str | None = None,
    ) -> Response:
        headers: dict[str, str] = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        response = self._client.post(
            "/graphql",
            json={"query": request_string, "variables": variable_values},
            headers=headers,
        )
        return response

    def run_query(
        self,
        request_string: str,
        payload: dict[str, Any],
        access_token: str | None = None,
    ) -> None:
        variable_values = get_variable_values(payload)
        result = self._execute(request_string, access_token=access_token, variable_values=variable_values)
        method = list(result.json()["data"].keys())[0]
        raise_for_graphql_status(result.json()["data"][method])
