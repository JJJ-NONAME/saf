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


class NotFoundInLocalStorageRootError(Exception):
    """Exception raised when attempting to access object that doesn't exist within the local storage root."""


class EntityNotFoundInBlobStorageError(Exception):
    """Exception raised when attempting to access entity using handle where the referenced entity does not exist."""


class CannotGenerateStreamForDirectoryError(Exception):
    """Exception raised when attempting to generate a stream for a directory entity."""


class EntityWriterHasNotCompletedWritingDataError(Exception):
    """Exception raised when attempting to get handle from EntityWriter before the writing context is closed."""


class EntityWriterIsNotWritingDataError(Exception):
    """Exception raised when attempting to access stream from EntityWriter
    after the writing context is closed or before it is opened."""


class EntityWriterHasWrittenDataError(Exception):
    """Exception raised when attempting to write to stream from EntityWriter
    after the writing context is closed."""


class InvalidContextError(Exception):
    """Exception raised when unknown context when creating a scope."""
