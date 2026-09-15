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

from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Any, Protocol, Self, TypeVar


class SolutionProtocol(Protocol):
    @property
    def url(self) -> str: ...

    @property
    def project_display_name(self) -> str: ...

    def delete(self) -> None: ...


T_co = TypeVar("T_co", bound=SolutionProtocol, covariant=True)


class ClientProtocol(Protocol[T_co]):
    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None: ...

    def import_project(self, safx_path: Path, display_name: str) -> T_co: ...

    def get_project(self, name: str) -> T_co: ...

    def create_project(self, display_name: str) -> T_co: ...

    def get_schema(self) -> dict[str, Any]: ...

    @property
    def http_client(self) -> Any: ...
