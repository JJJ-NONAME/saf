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

import mimetypes
from pathlib import Path
import uuid

from ansys.bdm.api import EntityHandle


class IdentifierParser:
    _COLON_ESCAPE = ":COLON"
    _DELIMITER = ":_DELIMITER"

    def __init__(self, entity: EntityHandle):
        self._identifier = entity.opaque_identifier

    @classmethod
    def _escape_path(cls, path: Path) -> str:
        return str(path).replace(":", cls._COLON_ESCAPE)

    @classmethod
    def _unescape_path(cls, path_string: str) -> Path:
        return Path(path_string.replace(cls._COLON_ESCAPE, ":"))

    def _get_relative_path(self, index: int):
        return self._unescape_path(self._identifier.split(self._DELIMITER)[index])

    @property
    def relative_path_within_original_storage_root(self) -> Path:
        return self._get_relative_path(1)

    @property
    def relative_path_of_original_storage_root(self) -> Path:
        return self._get_relative_path(0)

    @property
    def relative_path(self) -> Path:
        return self._unescape_path(self._identifier.replace(self._DELIMITER, "/"))

    @classmethod
    def create_handle(
        cls,
        file_system_root: Path,
        storage_root: Path,
        path: Path,
        mime_type: str | None = None,
        encoding: str | None = None,
    ) -> EntityHandle:
        identifier = (
            cls._escape_path(storage_root.relative_to(file_system_root))
            + cls._DELIMITER
            + cls._escape_path(path.relative_to(storage_root))
        )
        is_blob = path.is_file()
        size: int | None = None
        if is_blob:
            if not mime_type:
                mime_type, _ = mimetypes.guess_type(path, False)
            size = path.stat().st_size
        return EntityHandle(
            is_blob=is_blob,
            original_name=path.name,
            entity_id=uuid.uuid4(),
            opaque_identifier=identifier,
            mime_type=mime_type,
            size=size,
            encoding=encoding,
        )
