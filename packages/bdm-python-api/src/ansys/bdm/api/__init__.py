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

"""
TODO: package documentation
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

__version__ = importlib_metadata.version(f"{__name__.replace('.', '-')}")  # type: ignore
# Ignore "module level import not at top of file" errors
from .entity_handle import NO_ENTITY as NO_ENTITY
from .entity_handle import EntityHandle as EntityHandle
from .iasync_entity_writer import IAsyncEntityWriter as IAsyncEntityWriter
from .iasync_storage_scope import IAsyncReadStorageScope as IAsyncReadStorageScope
from .iasync_storage_scope import IAsyncStorageScope as IAsyncStorageScope
from .ientity_writer import IEntityWriter as IEntityWriter
from .istorage_scope import IReadStorageScope as IReadStorageScope
from .istorage_scope import IStorageScope as IStorageScope
from .istorage_scope_factory import IReadStorageScopeFactory as IReadStorageScopeFactory
from .istorage_scope_factory import IStorageScopeFactory as IStorageScopeFactory
from .recursive_dictionary import (
    RecursiveDictionaryOfEntityHandles as RecursiveDictionaryOfEntityHandles,
)
from .recursive_dictionary import validate_path_component as validate_path_component
from .storage_exceptions import (
    CannotGenerateStreamForDirectoryError as CannotGenerateStreamForDirectoryError,
)
from .storage_exceptions import (
    EntityNotFoundInBlobStorageError as EntityNotFoundInBlobStorageError,
)
from .storage_exceptions import (
    EntityWriterHasNotCompletedWritingDataError as EntityWriterHasNotCompletedWritingDataError,
)
from .storage_exceptions import (
    EntityWriterHasWrittenDataError as EntityWriterHasWrittenDataError,
)
from .storage_exceptions import (
    EntityWriterIsNotWritingDataError as EntityWriterIsNotWritingDataError,
)
from .storage_exceptions import (
    InvalidContextError as InvalidContextError,
)
from .storage_exceptions import (
    NotFoundInLocalStorageRootError as NotFoundInLocalStorageRootError,
)
