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

from io import BufferedIOBase, RawIOBase
from pathlib import Path, PurePath
import shutil
from typing import TYPE_CHECKING, final

from ansys.bdm.api import EntityHandle, IStorageScope, RecursiveDictionaryOfEntityHandles
from ansys.bdm.api.ientity_writer import IEntityWriter

if TYPE_CHECKING:
    from os import PathLike


@final
class ProductStorageScope:
    """The storage scope of the remote product.
    Its methods use file paths that are only valid in the context of the product.
    For example the ``store`` method expects file paths returned by the product api and the ``get_cached``
    method returns file paths that can be passed to the product api.

    Since the product instance manager itself is running within the solution,
    the product storage scope cannot be used to create files and directories on the remote product itself.
    """

    def __init__(
        self,
        storage_scope: IStorageScope,
        project_directory_path_on_solution: PurePath,
        project_directory_path_on_product: PurePath,
        state_directory_name: str,
    ):
        self._storage_scope_on_solution = storage_scope
        self._project_directory_path_on_solution = project_directory_path_on_solution
        self._project_directory_path_on_product = project_directory_path_on_product
        self._state_directory_name = state_directory_name

    def _exit(  # pyright: ignore[reportUnusedFunction]
        self,
    ) -> None:
        self._storage_scope_on_solution.__exit__(None, None, None)

    def get_storage_root(self) -> PurePath:
        """
        The remote product filesystem directory path as seen by the product itself.
        This cannot be used to create files and directories on the remote product itself.

        Notes
        -----
        If you need to create a file from the transaction method that is to be used by the remote product,
        you can do the following:
        - use the method storage scope to create the file:
          >>> my_method_file = self.storage_scope.get_storage_root() / "my_file.txt"
          >>> my_method_file.write_text("data")
        - store the file as entity handle on the method storage scope
          >>> my_file_handle = self.storage_scope.store(my_method_file)
        - access the file handle from the remote product using the product storage scope
          >>> my_file_on_product = my_product_manager.storage_scope.get_cached(my_file_handle)
          >>> my_product_manager.instance.use_file(my_file_on_product)
        """
        storage_root_on_solution = self._storage_scope_on_solution.get_storage_root()
        relative_path = storage_root_on_solution.relative_to(self._project_directory_path_on_solution)
        return PurePath(self._project_directory_path_on_product / relative_path)

    def get_cached(self, entity: EntityHandle) -> PurePath:
        """
        Realize the data to the remote product filesystem if needed
        and returns a path to the cached or original file on the remote file system.

        The :class:`EntityHandle` is intended to represent an immutable value. The file
        returned by this call may point to a cached or even the original file. Callers
        must not modify the file on disk or undefined behavior, including class 3 errors,
        may occur. If the caller needs to modify the file, consider using
        :func:`get_copy()`, or copying the file before modifying it.

        Parameters
        ----------
        entity: EntityHandle
            The handle to the data to realize

        Returns
        -------
        PurePath
            The path to the contents of the EntityHandle as realized locally. The caller
            MUST NOT modify the returned path.
        """
        absolute_path_on_solution = self._storage_scope_on_solution.get_cached(entity)
        if absolute_path_on_solution.is_relative_to(self._project_directory_path_on_solution):
            relative_path = absolute_path_on_solution.relative_to(self._project_directory_path_on_solution)
            return self._project_directory_path_on_product / relative_path
        else:
            # handle resolves to something outside of the shared file system, let's copy it into
            # a cache folder accessible from the product.
            # (this is typically the case for asset entity handles that are stored within the solution itself )
            product_cache_relative_path = (
                Path(self._state_directory_name)
                / ".product_cache"
                / str(entity.entity_id)
                / (entity.original_name or "file")
            )
            product_cache = Path(self._project_directory_path_on_solution) / product_cache_relative_path
            product_cache.parent.mkdir(exist_ok=True, parents=True)
            if entity.is_blob:
                shutil.copy(absolute_path_on_solution, product_cache)
            else:
                shutil.copytree(absolute_path_on_solution, product_cache)
            return self._project_directory_path_on_product / product_cache_relative_path

    def get_copy(self, entity: EntityHandle, destination: PurePath) -> None:
        """
        Realize the data to the remote product filesystem by writing to a specified file.

        The caller is free to modify the written file. The caller is responsible
        for deleting the generated file. If the destination path is within the storage root
        then the copy at that location will be deleted when the storage scope context is closed.

        Parameters
        ----------
        entity: EntityHandle
            The handle to the data to realize
        destination: PurePath
            The path to the file to write
        """

        storage_root_on_product = self.get_storage_root()
        if not destination.is_relative_to(storage_root_on_product):
            raise ValueError(f"The destination path '{str(destination)}' is not inside the product storage root.")

        relative_path = destination.relative_to(storage_root_on_product)
        storage_root_on_solution = self._storage_scope_on_solution.get_storage_root()
        self._storage_scope_on_solution.get_copy(entity, storage_root_on_solution / relative_path)

    def get_stream(self, entity: EntityHandle) -> RawIOBase:
        """
        Open the EntityHandle contents for reading as a stream.

        The returned stream MUST NOT be writable. The returned stream MAY be seekable.

        Parameters
        ----------
        entity: EntityHandle
            The handle to the data to realize

        Returns
        -------
        RawIOBase
            The stream which, when read, will return the contents of the EntityHandle.

        Raises
        ------

        CannotGenerateStreamForDirectoryError
            If the entity requested is a collection
        """
        return self._storage_scope_on_solution.get_stream(entity)

    def get_bytes(self, entity: EntityHandle) -> bytes:
        """
        Return the content of the referenced blob

        Parameters
        ----------
        entity: EntityHandle
            The handle to the data to realize

        Returns
        -------
        bytes
            the contents of the EntityHandle.

        Raises
        ------

        CannotGenerateStreamForDirectoryError
            If the entity requested is a collection
        """
        return self._storage_scope_on_solution.get_bytes(entity)

    def get_text(self, entity: EntityHandle, encoding: str | None = None) -> str:
        """
        Return the content of the referenced blob

        Parameters
        ----------
        entity: EntityHandle
            The handle to the data to realize
        encoding: Optional[str]
            The name of an encoding. When this argument is not None the bytes
            of ``entity`` will be read using that encoding.

        Returns
        -------
        str
            the contents of the EntityHandle in text form with the encoding determined
            in order of preference by:
            - the encoding argument if not None
            - the encoding field of the entity argument if set
            - the BOM of the referenced entity if it contains one; or
            - UTF-8

        Raises
        ------

        CannotGenerateStreamForDirectoryError
            If the entity requested is a collection
        """
        return self._storage_scope_on_solution.get_text(entity, encoding)

    def store(self, from_: "PathLike[str]", mime_type: str | None = None, encoding: str | None = None) -> EntityHandle:
        """
        Create an :class:`EntityHandle` from a file on disk.

        Many blob handler implementations will try to optimize performance and the file contents
        may not be immediately read from disk. To avoid class 3 type errors, the file MUST NOT be
        externally modified after calling this method.

        Parameters
        ----------

        from_: PathLike[str]
            The local file on disk which contains the contents for the generated :class:`EntityHandle`
        mime_type: Optional[str]
            Mime type of this file, if known. If None is passed in, the IAsyncStorageScope SHOULD
            use file extension to determine the mime type.
        encoding: Optional[str]
            The Internet Assigned Numbers Authority (IANA) registered encoding name used for textual data.
            This MAY be None if not known and SHOULD NOT be set for binary mime types.

        Returns
        -------
            An :class:`EntityHandle` that rerpesents the contents of the read file at the moment
            this method is invoked
        """
        relative_path = PurePath(from_).relative_to(self._project_directory_path_on_product)
        filepath_on_solution = self._project_directory_path_on_solution / relative_path
        return self._storage_scope_on_solution.store(filepath_on_solution, mime_type, encoding)

    def store_from_state_directory(
        self,
        from_: "PathLike[str]",
        mime_type: str | None = None,
        encoding: str | None = None,
    ) -> EntityHandle:
        """
        Create an :class:`EntityHandle` from a path within the product instance state directory.

        Many blob handler implementations will try to optimize performance and the file contents
        may not be immediately read from disk. To avoid class 3 type errors, the file MUST NOT be
        externally modified after calling this method.

        Parameters
        ----------

        from_: PathLike[str]
            The file or directory within the product instance state directory which contains the contents
            for the generated :class:`EntityHandle`
        mime_type: Optional[str]
            Mime type of this file, if known. If None is passed in, the IAsyncStorageScope SHOULD
            use file extension to determine the mime type.
        encoding: Optional[str]
            The Internet Assigned Numbers Authority (IANA) registered encoding name used for textual data.
            This MAY be None if not known and SHOULD NOT be set for binary mime types.

        Returns
        -------
            An :class:`EntityHandle` that represents the contents of the read file at the moment
            this method is invoked
        """
        if not PurePath(from_).is_relative_to(
            PurePath(self._project_directory_path_on_product / self._state_directory_name),
        ):
            raise ValueError(f"The file '{str(from_)}' is not inside the product state directory.")

        # file is in the product state directory, and may be overwritten by the product, thus breaking
        # BDM immutability -> let's copy it to the product storage scope.
        relative_path = PurePath(from_).relative_to(
            self._project_directory_path_on_product / self._state_directory_name,
        )
        filepath_on_solution = self._project_directory_path_on_solution / self._state_directory_name / relative_path
        target = self._storage_scope_on_solution.get_storage_root() / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if Path(filepath_on_solution).is_dir():
            shutil.copytree(filepath_on_solution, target)
        else:
            shutil.copy(filepath_on_solution, target)

        return self._storage_scope_on_solution.store(target, mime_type, encoding)

    def store_stream(
        self,
        from_: RawIOBase | BufferedIOBase | bytes,
        relative_location: Path | None = None,
        mime_type: str | None = None,
        encoding: str | None = None,
    ) -> EntityHandle:
        """
        Fully reads a passed in stream and returns a handle for the given content.

        Parameters
        ----------

        from_ : Union[RawIOBase, BufferedIOBase, bytes]
            The stream or in-memory bytes from which the new entity will be created
        relative_location : Optional[Path]
            The nominal relative path of the entity. The path is relative to the storage_root of
            the scope. No data is expected at this location.
            The filename from this path will be used as the original name of the entity.
            If this parameter is not set then the implementation will generate a unique location.
        mime_type: Optional[str]
            Mime type of this file, if known. If None is passed in, the IAsyncStorageScope SHOULD
            use file extension to determine the mime type.
        encoding: Optional[str]
            The Internet Assigned Numbers Authority (IANA) registered encoding name used for textual data.
            This MAY be None if not known and SHOULD NOT be set for binary mime types.

        Returns
        -------

        EntityHandle
            The :class:`EntityHandle` that represents the passed in data.
        """
        return self._storage_scope_on_solution.store_stream(from_, relative_location, mime_type, encoding)

    def begin_store(
        self,
        relative_location: Path | None = None,
        mime_type: str | None = None,
        encoding: str | None = None,
    ) -> IEntityWriter:
        """
        Create an :class:`IEntityWriter` by writing to a stream object.

        Parameters
        ----------

        relative_location : Optional[Path]
            The nominal relative path of the entity. The path is relative to the storage_root of
            the scope. No data is expected at this location.
            The filename from this path will be used as the original name of the entity.
            If this parameter is not set then the implementation will generate a unique location.
        mime_type: Optional[str]
            Mime type of this file, if known. If None is passed in, the IAsyncStorageScope SHOULD
            use file extension to determine the mime type.
        encoding: Optional[str]
            The Internet Assigned Numbers Authority (IANA) registered encoding name used for textual data.
            This MAY be None if not known and SHOULD NOT be set for binary mime types.

        Returns
        -------

        IEntityWriter
            An object which allows you to write to a stream and retrieve the handle.
        """
        return self._storage_scope_on_solution.begin_store(relative_location, mime_type, encoding)

    @property
    def stored_entities(self) -> list[EntityHandle]:
        """
        The set of :class:`EntityHandle` instances that have been stored via this scope
        """
        return self._storage_scope_on_solution.stored_entities

    def destroy(self, *entity: EntityHandle) -> None:
        """
        Delete the entities referenced by the handle.

        As :class:`EntityHandle` instances are intended to be simple immutable structures
        that can be passed across process and service boundaries, their lifespan must be managed
        by an external system. This call allows the resources associated with a BlobHandle
        to be removed.

        Parameters
        ----------

        *entity: EntityHandle
            The entities to delete
        """
        return self._storage_scope_on_solution.destroy(*entity)

    def get_children(self, entity: EntityHandle) -> list[EntityHandle]:
        """
        Return the entities contained in this entity.

        Parameters
        ----------

        entity: EntityHandle
            The entity to query


        Returns
        -------

        List[EntityHandle]
            The list of entities that are children of the provided entity

        Raises
        ------

        NotADirectoryError
            If the requested entity is not a directory

        """
        return self._storage_scope_on_solution.get_children(entity)

    def get_child(self, entity: EntityHandle, child_name: str) -> EntityHandle:
        """
        Return the entity contained in this entity with a given name.

        Parameters
        ----------

        entity: EntityHandle
            The entity to query
        child_name: str
            The child to search for

        Returns
        -------

        EntityHandle
            The :class:`EntityHandle` requested

        Raises
        ------

        NotADirectoryError
            If the requested entity is not a directory
        EntityNotFoundInBlobStorageError
            If the requested entity is not found
        """
        return self._storage_scope_on_solution.get_child(entity, child_name)

    def get_parent(self, entity: EntityHandle) -> EntityHandle | None:
        """
        Return the entity containing in this entity.

        Parameters
        ----------

        entity: EntityHandle
            The entity to query

        Returns
        -------

        Optional[EntityHandle]
            The :class:`EntityHandle` requested, or None if the entity is stored at the root of its scope.

        Raises
        ------

        EntityNotFoundInBlobStorageError
            If the requested entity is not found.
        """
        return self._storage_scope_on_solution.get_parent(entity)

    def get_copy_from_dictionary(
        self,
        root: PurePath,
        source: RecursiveDictionaryOfEntityHandles,
        glob: str | None = None,
    ) -> None:
        self._storage_scope_on_solution.get_copy_from_dictionary(root, source, glob)

    def store_to_dictionary(
        self,
        root: PurePath,
        glob: str | None = None,
    ) -> RecursiveDictionaryOfEntityHandles:
        return self._storage_scope_on_solution.store_to_dictionary(root, glob)
