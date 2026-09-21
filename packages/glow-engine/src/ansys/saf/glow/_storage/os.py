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
import pathlib
import platform
import shutil
from urllib.parse import unquote, urlparse

from ansys.saf.glow._storage.base import AbstractStorage, AbstractStoragePath, InvalidResourceException

INVALID_CHARACTERS = ["\\", ":", "*", "?", "<", ">", "|"]


def is_filepath_invalid(filepath: str) -> bool:
    """Specifies whether a filepath contains any invalid
    characters."""
    return any(char in INVALID_CHARACTERS for char in filepath)


class OperatingSystemPath(AbstractStoragePath):
    """A path to a directory or file in a OS Filesystem which may or may not actually exist.

    Parameters
    ----------
    path : str or pathlib.Path
        A path to a directory or file in a OS Filesystem.
    """

    def __init__(self, path: str | pathlib.Path) -> None:
        if isinstance(path, str):
            self._path = pathlib.Path(path)
        else:
            self._path = path

    def __str__(self) -> str:
        return str(self._path.resolve())

    def __truediv__(self, other: str) -> "AbstractStoragePath":
        return OperatingSystemPath(self._path / other)

    def is_dir(self) -> bool:
        """Return whether the path refers to a directory or folder.

        Returns
        -------
        bool
            Whether the path refers to a directory or folder."""
        return self._path.is_dir()

    def is_file(self) -> bool:
        """Return whether the path refers to a file or blob.

        Returns
        -------
        bool
            Whether the path refers to a file or blob."""
        return self._path.is_file()

    def read_text(self) -> str:
        """Return the text content of the file or blob that the path refers to.

        Returns
        -------
        str
            The text content of the file or blob that the path refers to.
        """
        return self._path.read_text()

    def write_text(self, text: str) -> None:
        """Replace the content of the file or blob that the path refers to or
        creates a new file or blob.

        Parameters
        ----------
        text : str
            The new content of the file or blob referenced by the path."""

        self._path.write_text(text)

    def write_text_with_new_dir(self, text: str) -> None:
        """Replace the content of the file or blob that the path refers to or
        creates a new file or blob. Creates the parent directory if doesn't exist.

        Parameters
        ----------
        text : str
            The new content of the file or blob referenced by the path."""

        if not self._path.parent.is_dir():
            self._path.parent.mkdir(parents=True)
        self._path.write_text(text)

    def write_bytes(self, data: bytes) -> None:
        """Replace the content of the file or blob that the path refers to or
        creates a new file or blob.

        Parameters
        ----------
        data : bytes
            The new content of the file or blob referenced by the path."""
        self._path.write_bytes(data)

    def mkdir(self) -> None:
        """Create the directory referenced by the path including all the parent directories."""
        self._path.mkdir(parents=True, exist_ok=True)

    def remove(self) -> None:
        """Remove recursively the entire directory, folder, file or blob referenced by the path."""
        if self.is_file():
            self._path.unlink()
        else:
            shutil.rmtree(str(self._path.resolve()))

    def iterdir(self) -> Iterator[AbstractStoragePath]:
        """Return an iterator over the entities that exist on the directory or folder referenced by the path.

        Returns
        -------
        ``Iterator over AbstractStoragePath``
            The entities that exist on the directory or folder referenced by the path.
        """
        return (OperatingSystemPath(p) for p in self._path.iterdir())

    def as_uri(self) -> str:
        """Return a URI that refers to the entity referenced by the path.

        Returns
        -------
        str
            A URI that refers to the entity referenced by the path."""
        return self._path.as_uri()

    def resolve(self) -> AbstractStoragePath:
        """Make the path absolute, resolving any symbolic links or ``..`` components. A new path object is returned.

        Returns
        -------
        ``AbstractStoragePath``
            A new reference to the same entity but removing symbolic links and ``..`` components.
        """
        return OperatingSystemPath(self._path.resolve())

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def name(self) -> str:
        """The name of the entity referenced by the path.

        Returns
        -------
        str
            The name of the entity referenced by the path.
        """
        return self._path.name

    @property
    def stem(self) -> str:
        """The name of the entity referenced by the path with its suffix (file extension).

        Returns
        -------
        str
            The name of the entity referenced by the path with its suffix (file extension)."""
        return self._path.stem

    @property
    def parent(self) -> AbstractStoragePath:
        """The directory or folder that contains the entity referenced by the path.

        Returns
        -------
        ``AbstractStoragePath``
            The directory or folder that contains the entity referenced by the path.
        """
        return OperatingSystemPath(self._path.resolve().parent)

    @property
    def suffix(self) -> str:
        """The suffix for file extension of the entity referenced by the path.

        Returns
        -------
        str
            The suffix for file extension of the entity referenced by the path."""
        return self._path.suffix

    @property
    def exists(self):
        """Whether the entity referenced by the path exists.

        Returns
        -------
        bool
            Whether the entity referenced by the path exists."""
        return self._path.exists()

    def copyfileobj(self, fileobj) -> None:  # type: ignore
        """Create or replace of the referenced entity with the contents of the file-like object ``fileobj``.

        Parameters
        ----------
        fileobj : ``file like object``
            The object that is the source of data to become the content of the referenced entity."""
        with self._path.open("wb") as destination_buffer:
            shutil.copyfileobj(fileobj, destination_buffer)  # type: ignore

    def glob(self, pattern: str) -> list[AbstractStoragePath]:
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
        return [OperatingSystemPath(path) for path in self._path.glob(pattern)]

    def copy(self, destination: "AbstractStoragePath") -> None:
        """Copy the referenced entity to the given destination directory or folder.
        The destination directory and any missing parents will be created if they do not exist.

        Parameters
        ----------
        destination : ``AbstractStoragePath``
            The directory or folder where the referenced entity will be copied."""
        if not isinstance(destination, OperatingSystemPath):
            raise RuntimeError("copy of OperatingSystemPath to another type of storage path is not supported (yet)")
        dest_parent = destination.parent
        if not dest_parent.exists:
            dest_parent.mkdir()
        shutil.copy(self._path, destination._path)


class OperatingSystemStorage(AbstractStorage):
    """A factory for :py:class:`~ansys.saf.glow.client.OperatingSystemPath` objects."""

    def create_path_from_reference(self, reference: str) -> AbstractStoragePath:
        """Create a :py:class:`~ansys.saf.glow.client.OperatingSystemPath` object given a URL.

        Parameters
        ----------
        reference : str
            The URL of a file or directory.

        Returns
        -------
        AbstractStoragePath
            A object for accessing the file or directory.
        """
        file_url_parts = urlparse(reference)

        if file_url_parts.scheme != "file":
            raise InvalidResourceException(f"Expecting a file URL, but received '{reference}'.")

        if not file_url_parts.path:
            raise InvalidResourceException(f"Expecting a full-path file URL, but received '{reference}'.")

        if platform.system() == "Windows":
            if file_url_parts.netloc:
                file_path = f"//{file_url_parts.netloc}{file_url_parts.path}"
            else:
                file_path = file_url_parts.path[1:]
        else:
            file_path = file_url_parts.path

        return OperatingSystemPath(unquote(file_path))
