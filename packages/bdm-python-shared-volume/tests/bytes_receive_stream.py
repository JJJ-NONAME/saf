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

from anyio import EndOfStream
from anyio.abc import ByteReceiveStream


class BytesReceiveStream(ByteReceiveStream):
    """
    Implementation of ByteReceiveStream that returns the contents of in memory bytes.
    """

    def __init__(self, data: bytes) -> None:
        self._bytes = data
        self._eof = False
        super().__init__()

    async def receive(self, max_bytes: int = 65536) -> bytes:
        if self._eof:
            raise EndOfStream()
        self._eof = True
        # TODO: We are ignoring max_bytes
        return self._bytes

    # TODO: this should cause receive to show EOF.
    async def aclose(self) -> None:
        return await super().aclose()
