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
import pickle
from typing import Any

_DATA_ESCAPED_CHARACTERS = ["0", "+", "/", "="]


def encode_data_for_hps(data: Any) -> str:
    try:
        byte_string = pickle.dumps(data)
    except (pickle.PicklingError, AttributeError, TypeError) as e:
        raise RuntimeError(
            f"The SAF HPS API does not support the serialization of {type(data)} objects.  In this case: {data}",
        ) from e
    base64_bytes = base64.b64encode(byte_string)
    base64_str = base64_bytes.decode("utf-8")
    for index, char in enumerate(_DATA_ESCAPED_CHARACTERS):
        base64_str = base64_str.replace(char, f"0{index}")
    return base64_str


def decode_data_from_hps(encoded_str: str) -> Any:
    base64_str = ""
    escaped = False
    for c in encoded_str:
        if escaped:
            escaped = False
            base64_str += _DATA_ESCAPED_CHARACTERS[int(c)]
        elif c == "0":
            escaped = True
        else:
            base64_str += c
    base64_bytes = base64_str.encode("utf-8")
    byte_string = base64.b64decode(base64_bytes)
    data = pickle.loads(byte_string)  # noqa: S301  #nosec
    return data


def encode_string_for_hps(s: str) -> str:
    encoded = ""
    for c in s:
        if c.isascii() and (c.isalnum() or c == " "):
            encoded += c
        else:
            # insert string hex value of c between two '_' characters
            encoded += f"_{ord(c):x}_"
    return encoded


def decode_string_from_hps(s: str) -> str:
    decoded = ""
    in_hexadecimal = False
    hexadecimal = ""
    for c in s:
        if c == "_":
            if in_hexadecimal:
                decoded += chr(int(hexadecimal, 16))
                hexadecimal = ""
                in_hexadecimal = False
            else:
                in_hexadecimal = True
        elif in_hexadecimal:
            hexadecimal += c
        else:
            decoded += c
    if in_hexadecimal:
        raise RuntimeError(f'When decoding from HPS string "{s}", it ends with an unmatched "_" character')
    return decoded
