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

"""IAM OIDC package.

This package provides OAuth2 and OpenID Connect (OIDC) capabilities,
enabling seamless integration of authentication and authorization features.

The package is built on top of Authlib and provides both synchronous and asynchronous
OIDC clients, FastAPI dependencies for token validation, and utility functions for
token handling.
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # pyright: ignore[reportMissingImports]

__version__ = importlib_metadata.version(  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    f"{__name__.replace('.', '-')}",
)
# Ignore "module level import not at top of file" errors
from ansys.iam.oidc._client import AsyncOidcClient, OidcClient
from ansys.iam.oidc._exceptions import NoIssuerError, NoIssuerOrAudienceError
from ansys.iam.oidc._fastapi import (
    DEFAULT_SUBPROTOCOL_PREFIX,
    OidcDependency,
    OidcWebSocketDependency,
    get_websocket_subprotocol,
)
from ansys.iam.oidc._userinfo import UserInfo
from ansys.iam.oidc._utilities import decode_base64_token, encode_base64_token

__all__ = [
    "DEFAULT_SUBPROTOCOL_PREFIX",
    "AsyncOidcClient",
    "NoIssuerError",
    "NoIssuerOrAudienceError",
    "OidcClient",
    "OidcDependency",
    "OidcWebSocketDependency",
    "UserInfo",
    "decode_base64_token",
    "encode_base64_token",
    "get_websocket_subprotocol",
]
