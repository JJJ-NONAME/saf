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


class HpsAuthInfo:
    def __init__(self) -> None:
        self._access_token: str = ""
        self._refresh_token: str = ""

    def get_auth_data(self) -> dict[str, str]:
        if self._access_token == "":  # nosec
            self._refresh_token = ""  # nosec

        return {"access_token": self._access_token, "refresh_token": self._refresh_token}

    def set_auth_data(self, access_token: str, refresh_token: str) -> None:
        self._access_token = access_token
        self._refresh_token = refresh_token
