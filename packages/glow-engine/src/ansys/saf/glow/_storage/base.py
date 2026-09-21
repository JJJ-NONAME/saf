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

from collections.abc import Iterator


class InvalidResourceException(Exception):  # noqa: N818
    pass


class AbstractStoragePath:
    """A base class for representing paths to folders, directories, files or blobs in a
    hierarchical storage scheme, such as an OS Filesystem or cloud storage."""

    def __str__(self) -> str:
        raise RuntimeError("Not Implemented")

    def __truediv__(self, other: str) -> "AbstractStoragePath":
        raise RuntimeError("Not Implemented")

    def is_dir(self) -> bool:
        """Return whether the path refers to a directory or folder.

        Returns
        -------
        bool
            Whether the path refers to a directory or folder."""
        raise RuntimeError("Not Implemented")

    def is_file(self) -> bool:
        """Return whether the path refers to a file or blob.

        Returns
        -------
        bool
            Whether the path refers to a file or blob."""
        raise RuntimeError("Not Implemented")

    def read_text(self) -> str:
        """Return the text content of the file or blob that the path refers to.

        Returns
        -------
        str
            The text content of the file or blob that the path refers to.
        """
        raise RuntimeError("Not Implemented")

    def write_text(self, text: str) -> None:
        """Replace the content of the file or blob that the path refers to or
        creates a new file or blob.

        Parameters
        ----------
        text : str
            The new content of the file or blob referenced by the path."""

        raise RuntimeError("Not Implemented")

    def write_bytes(self, data: bytes) -> None:
        """Replace the content of the file or blob that the path refers to or
        creates a new file or blob.

        Parameters
        ----------
        data : bytes
            The new content of the file or blob referenced by the path."""
        raise RuntimeError("Not Implemented")

    def write_text_with_new_dir(self, text: str) -> None:
        """Replace the content of the file or blob that the path refers to or
        creates a new file or blob. Creates the parent directory if it does not already exist.

        Parameters
        ----------
        text : str
            The new content of the file or blob referenced by the path."""

        raise RuntimeError("Not Implemented")

    def mkdir(self) -> None:
        """Create the directory referenced by the path including all the parent directories."""
        raise RuntimeError("Not Implemented")

    def remove(self) -> None:
        """Remove recursively the entire directory, folder, file or blob referenced by the path."""
        raise RuntimeError("Not Implemented")

    def iterdir(self) -> Iterator["AbstractStoragePath"]:
        """Return an iterator over the entities that exist on the directory or folder referenced by the path.

        Returns
        -------
        ``Iterator over AbstractStoragePath``
            The entities that exist on the directory or folder referenced by the path.
        """
        raise RuntimeError("Not Implemented")

    def as_uri(self) -> str:
        """Return a URI that refers to the entity referenced by the path.

        Returns
        -------
        str
            A URI that refers to the entity referenced by the path."""
        raise RuntimeError("Not Implemented")

    def resolve(self) -> "AbstractStoragePath":
        """Make the path absolute, resolving any symbolic links or ``..`` components. A new path object is returned.

        Returns
        -------
        ``AbstractStoragePath``
            A new reference to the same entity but removing symbolic links and ``..`` components.
        """
        raise RuntimeError("Not Implemented")

    @property
    def name(self) -> str:
        """The name of the entity referenced by the path.

        Returns
        -------
        str
            The name of the entity referenced by the path.
        """
        raise RuntimeError("Not Implemented")

    @property
    def stem(self) -> str:
        """The name of the entity referenced by the path with its suffix (file extension).

        Returns
        -------
        str
            The name of the entity referenced by the path with its suffix (file extension)."""
        raise RuntimeError("Not Implemented")

    @property
    def parent(self) -> "AbstractStoragePath":
        """The directory or folder that contains the entity referenced by the path.

        Returns
        -------
        ``AbstractStoragePath``
            The directory or folder that contains the entity referenced by the path.
        """
        raise RuntimeError("Not Implemented")

    @property
    def suffix(self) -> str:
        """The suffix for file extension of the entity referenced by the path.

        Returns
        -------
        str
            The suffix for file extension of the entity referenced by the path."""
        raise RuntimeError("Not Implemented")

    @property
    def exists(self) -> bool:
        """Whether the entity referenced by the path exists.

        Returns
        -------
        bool
            Whether the entity referenced by the path exists."""
        raise NotImplementedError("Not Implemented")

    def copyfileobj(self, fileobj) -> None:  # type: ignore
        """Create or replace of the referenced entity with the contents of the file-like object ``fileobj``.

        Parameters
        ----------
        fileobj : ``file like object``
            The object that is the source of data to become the content of the referenced entity."""
        raise NotImplementedError("Not Implemented")

    def glob(self, pattern: str) -> list["AbstractStoragePath"]:
        """Return the paths of entities with in the referenced fdirectory or folder that match the given
        pattern.

        Parameters
        ----------
        pattern : str
            The pattern that is used to match entities within the referenced directory.
            The pattern can include ``*`` as a wild match and ``**`` which matches directories recursively.

        Returns
        -------
        ``list of AbstractStoragePath``
               The paths of entities with in the referenced directory or folder that match the given pattern.
        """
        raise NotImplementedError()

    def copy(self, destination: "AbstractStoragePath") -> None:
        """Copy the referenced entity to the given destination directory or folder.
        The destination directory and any missing parents will be created if they do not exist.

        Parameters
        ----------
        destination : ``AbstractStoragePath``
            The directory or folder where the referenced entity will be copied."""
        raise NotImplementedError()


class AbstractStorage:
    def create_path_from_reference(self, reference: str) -> AbstractStoragePath:
        raise RuntimeError("Not Implemented")
