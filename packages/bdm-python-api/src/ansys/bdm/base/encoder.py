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

from ansys.bdm.api.entity_handle import EntityHandle


def decode_bom(bom: bytes) -> tuple[str | None, int]:
    """
    Return a tuple consisting of
    1) the name of the encoding stored in the BOM prefix of the given byte data; and
    2) the length of BOM in bytes.

    If the byte data does not contain a BOM then a tuple ``(None, 0)`` is returned.

    Parameters
    ----------
    bom: bytes
        byte data that may or may not be prefixed with a BOM

    Returns
    -------
    Tuple[Optional[str], int]
        a tuple consisting of
        1) the name of the encoding stored in the BOM prefix of the given byte data; and
        2) the length of BOM in bytes.

        If the byte data does not contain a BOM then a tuple ``(None, 0)`` is returned.
    """
    if bom[0] == 0xEF and bom[1] == 0xBB and bom[2] == 0xBF:
        return ("utf-8", 3)
    if bom[0] == 0xFF and bom[1] == 0xFE and bom[2] == 0 and bom[3] == 0:
        return ("utf-32-le", 4)
    if bom[0] == 0xFF and bom[1] == 0xFE:
        return ("utf-16-le", 2)
    if bom[0] == 0xFE and bom[1] == 0xFF:
        return ("utf-16-be", 2)
    if bom[0] == 0 and bom[1] == 0 and bom[2] == 0xFE and bom[3] == 0xFF:
        return ("utf-32-be", 4)
    return (None, 0)


def encode_text(data: bytes, handle: EntityHandle, encoding: str | None = None) -> str:
    """
    Return a string which is derived from the given byte data

    Parameters
    ----------
    data: bytes
        byte data that may or may not be prefixed with a BOM that provides the data for the returned string
    handle: EntityHandle
        the entity handle that refers to the object that contains the given data
    encoding: Optional[str]
        The name of an encoding.  When this argument is not None the returned
        string will be decoded using the given encoding.

    Returns
    -------
    str
        a string containing the byte data with the encoding determined
        in order of preference by:
        - the encoding argument if not None
        - the encoding field of the entity argument if set
        - the BOM of the referenced entity if it contains one; or
        - UTF-8
    """
    if encoding is None:
        if handle.encoding is not None:
            encoding = handle.encoding
        else:
            encoding, bom_length = decode_bom(data)

            if encoding is not None:
                data = data[bom_length:]
            else:
                encoding = "utf-8"
    return str(data, encoding=encoding)
