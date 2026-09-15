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

import base64
import binascii


def encode_base64_token(token: str) -> str:
    """Encode a token using base64 encoding.

    Parameters
    ----------
    token: str
        The token to encode.

    Returns
    -------
    str
        The base64-encoded token.

    """
    # We use URL-safe base64 encoding without padding for safety. It's not clear if it's really needed, at least for
    # passing the encoded token as a websocket subprotocol (which is the main use of this method). The WebSocket RFC
    # (https://datatracker.ietf.org/doc/html/rfc6455#page-18) says U+0021 to U+007E, which should cover the default
    # Base64, but other implementations also do this transformation.
    encoded_token = base64.urlsafe_b64encode(token.encode("utf-8")).decode("utf-8")
    return encoded_token.replace("=", "")  # Remove padding for URL safety


def decode_base64_token(encoded_token: str) -> str:
    """Decode a base64-encoded token.

    Parameters
    ----------
    encoded_token: str
        The base64-encoded token to decode.

    Returns
    -------
    str
        The decoded token.

    Raises
    ------
    ValueError
        If the token cannot be decoded.

    """
    try:
        if missing_chars := len(encoded_token) % 4:
            encoded_token += "=" * (4 - missing_chars)  # Add necessary padding back
        return base64.urlsafe_b64decode(encoded_token.encode("utf-8")).decode("utf-8")
    except (binascii.Error, ValueError, UnicodeDecodeError, UnicodeEncodeError) as e:
        # expected exceptions from https://docs.python.org/3/library/base64.html and method docstrings
        msg = f"Token cannot be decoded: {e!s}"
        raise ValueError(msg) from None
