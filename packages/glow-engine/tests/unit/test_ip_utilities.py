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
import pytest
import pytest_mock

from ansys.saf.glow._utilities.ip_utilities import try_response, wait_for_response


def test_response_tries_not_integrer():
    with pytest.raises(RuntimeError, match="tries is not an integer"):
        wait_for_response(url="", tries=3.5)  # type: ignore


def test_response_tries_less_than_one():
    with pytest.raises(RuntimeError, match="tries is less than one"):
        wait_for_response(url="", tries=-1)  # type: ignore


def test_response_interval_less_than_zero():
    with pytest.raises(RuntimeError, match="interval is less than zero"):
        wait_for_response(url="", interval=-1)  # type: ignore


def test_unable_to_reach_url():
    url_to_reach = "https://fakeurl"
    with pytest.raises(RuntimeError, match=f"Error: unable to reach {url_to_reach}"):
        wait_for_response(url=url_to_reach, tries=2, interval=1)  # type: ignore


@pytest.mark.parametrize(
    "exception_class",
    [
        httpx2.ConnectError,
        httpx2.ReadError,
        httpx2.TimeoutException,
        httpx2.NetworkError,
        httpx2.ProtocolError,
        httpx2.HTTPStatusError,
        httpx2.WriteError,
        httpx2.RemoteProtocolError,
    ],
)
def test_try_response_returns_false_on_http_errors(exception_class: type[Exception], mocker: pytest_mock.MockerFixture):
    test_url = "http://test.example.com"
    if exception_class != httpx2.HTTPStatusError:
        args = {"message": "Test error"}
    else:
        args = {
            "message": "Test error",
            "response": httpx2.Response(500),
            "request": httpx2.Request("GET", test_url),
        }
    mock_http_get = mocker.patch(
        "ansys.saf.glow._utilities.ip_utilities.httpx2.Client.get",
        side_effect=exception_class(**args),
    )
    assert try_response(test_url) is False
    mock_http_get.assert_called_once_with(test_url)
