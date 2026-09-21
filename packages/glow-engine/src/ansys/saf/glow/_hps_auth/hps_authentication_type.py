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

from enum import Enum

# IMPORTANT: Keep HPS dependencies out of here. These classes are imported in CRUD.


class HpsAuthenticationType(Enum):
    """The types of supported HPS authentication."""

    KEYCLOAK_INTERACTIVE = "KEYCLOAK_INTERACTIVE"
    """Triggers the interactive authenticator to acquire access tokens."""
    TOKEN_EXCHANGE = "TOKEN_EXCHANGE"  # noqa: S105  #nosec
    """Acquires new auth tokens from auth issuer using input access token."""
    USER_PASSWORD = "USER_PASSWORD"  # noqa: S105  #nosec
    """Uses user and password to authenticated."""
