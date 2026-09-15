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

from unittest.mock import MagicMock

import pytest_mock

from ansys.saf.product_manager.visor._visor_manager import InternalVisorManager


def test_initialize_payload_does_not_send_port(mocker: pytest_mock.MockerFixture) -> None:
    post_mock = mocker.patch(
        "ansys.saf.product_manager.visor._visor_manager.httpx2.post",
        return_value=MagicMock(),
    )
    manager = object.__new__(InternalVisorManager)

    manager._initialize_visor(hostname="example-host", port=8080)  # pyright: ignore[reportPrivateUsage]

    initialize_payload = post_mock.call_args_list[0].kwargs["json"]
    assert initialize_payload == {"host": "example-host", "standalone": False}
