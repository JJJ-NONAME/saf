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

from contextlib import contextmanager
from typing import Protocol

# IMPORTANT: Keep HPS dependencies out of here. These classes are imported in core, server...
from ansys.saf.glow._hps_auth.hps_authentication_type import HpsAuthenticationType


class IHpsAuthenticator(Protocol):
    _access_token: str = ""
    _refresh_token: str = ""
    _hps_user: str = ""
    _hps_pwd: str = ""

    @contextmanager
    def get_hps_client(  # pyright: ignore[reportUnknownParameterType]
        self,
        hps_server_url: str,
        client_id: str | None = None,
    ) -> "Client": ...  # noqa: F821  # pyright: ignore[reportUndefinedVariable]

    @property
    def auth_type(self) -> HpsAuthenticationType:
        if self._access_token != "":
            return HpsAuthenticationType.TOKEN_EXCHANGE

        if self._hps_user and self._hps_pwd:
            return HpsAuthenticationType.USER_PASSWORD

        return HpsAuthenticationType.KEYCLOAK_INTERACTIVE
