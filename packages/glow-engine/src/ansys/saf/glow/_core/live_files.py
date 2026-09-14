# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.
from __future__ import annotations

from pathlib import Path
import shutil
from typing import TYPE_CHECKING, Any, BinaryIO, Literal

from pydantic_core import core_schema

from ansys.saf.glow._storage.os import INVALID_CHARACTERS, is_filepath_invalid

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
    from pydantic.json_schema import JsonSchemaValue


BinaryWriteMode = Literal["wb", "ab"]
TextWriteMode = Literal["w", "a"]


class LiveFile(str):
    """Relative path to a mutable file in a GLOW project.

    This class represents a file that can be read while being written.
    """

    def __new__(
        cls,
        value: str,
    ):
        return super().__new__(cls, value)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(cls._validate, handler(str))

    @classmethod
    def _validate(cls, value: str):
        if not isinstance(value, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("String is required.")
        if ".." in value:
            raise ValueError(f".. is not allowed inside a {cls.__name__} field.")
        if Path(value).is_absolute():
            raise ValueError(f"Absolute path: '{value}' is not allowed in a {cls.__name__} field.")
        if value in {"", "."}:
            raise ValueError(f"A {cls.__name__} must refer to a file path.")
        if value.endswith(("/", "\\")):
            raise ValueError(f"A {cls.__name__} must refer to a file and cannot end with a path separator.")
        if is_filepath_invalid(value):
            raise ValueError(
                f"A {cls.__name__} can't contain any of the following characters: {' '.join(INVALID_CHARACTERS)}",
            )
        # LiveFile targets a single file only, so wildcard/group patterns are not allowed.
        if any(char in value for char in "*?[]"):
            raise ValueError(f"A {cls.__name__} cannot contain wildcard characters like '*', '?', '[' or ']'.")
        return cls(value)

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        json_schema = handler(schema)
        json_schema.update(
            type="string",
            examples=["logs/runtime.log", "outputs/convergence.csv"],
        )
        return json_schema

    def __repr__(self):
        return f"LiveFile({super().__repr__()})"

    @property
    def _relative_path(self) -> Path:
        return Path(str(self))

    @property
    def name(self) -> str:
        return self._relative_path.name

    @property
    def _absolute_path(self) -> Path:
        raise NotImplementedError()

    def read_text(self, encoding: str = "utf-8") -> str:
        return self._absolute_path.read_text(encoding=encoding)

    def read_bytes(self) -> bytes:
        return self._absolute_path.read_bytes()

    @property
    def path(self) -> Path:
        raise NotImplementedError()


class TransactionLiveFile(LiveFile):
    """Transaction-scoped mutable file for the current project.

    The relative path is resolved from ``project_files_dir / project_id``.
    This class supports both reading and writing file content.
    """

    def __new__(cls, value: str, project_files_dir: Path):
        self = super().__new__(cls, value)
        self._project_files_dir = project_files_dir
        return self

    @property
    def _absolute_path(self) -> Path:
        return self._project_files_dir / self._relative_path

    @property
    def path(self) -> Path:
        return self._absolute_path

    def _ensure_parent_directory(self, absolute_path: Path) -> None:
        absolute_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, binary_fileobj: BinaryIO, mode: BinaryWriteMode = "wb") -> None:
        self._ensure_parent_directory(self._absolute_path)
        with self._absolute_path.open(mode) as destination_buffer:
            shutil.copyfileobj(binary_fileobj, destination_buffer)

    def write_from_file(self, data_file: str | Path | LiveFile, mode: BinaryWriteMode = "wb") -> None:
        if isinstance(data_file, LiveFile):
            source_bytes = data_file.read_bytes()
        else:
            source = Path(data_file)
            if not source.is_file():
                raise FileNotFoundError(f"The source file '{source}' does not exist.")
            source_bytes = source.read_bytes()

        self._ensure_parent_directory(self._absolute_path)
        with self._absolute_path.open(mode) as destination_buffer:
            destination_buffer.write(source_bytes)

    def write_text(self, text: str, encoding: str = "utf-8", mode: TextWriteMode = "w") -> None:
        self._ensure_parent_directory(self._absolute_path)
        with self._absolute_path.open(mode, encoding=encoding) as destination_buffer:
            destination_buffer.write(text)

    def write_bytes(self, data: bytes, mode: BinaryWriteMode = "wb") -> None:
        self._ensure_parent_directory(self._absolute_path)
        with self._absolute_path.open(mode) as destination_buffer:
            destination_buffer.write(data)

    def delete(self) -> None:
        if self._absolute_path.exists():
            self._absolute_path.unlink()

    def exists(self) -> bool:
        return self._absolute_path.exists()


class LiveFileProxy(LiveFile):
    """Client-side read-only view of a LiveFile.

    The relative path is resolved from ``project_files_dir / project_id``.
    This class allows reading file content while blocking all mutation operations.
    """

    def __new__(cls, value: str, project_files_dir: Path):
        self = super().__new__(cls, value)
        self._project_files_dir = project_files_dir
        return self

    @property
    def _absolute_path(self) -> Path:
        return self._project_files_dir / self._relative_path

    def _raise_read_only(self) -> None:
        raise PermissionError("The content of a LiveFile cannot be mutated from the Client scope.")

    def write(self, binary_fileobj: BinaryIO, mode: BinaryWriteMode = "wb") -> None:
        self._raise_read_only()

    def write_from_file(self, data_file: str | Path | LiveFile, mode: BinaryWriteMode = "wb") -> None:
        self._raise_read_only()

    def write_text(self, text: str, encoding: str = "utf-8", mode: TextWriteMode = "w") -> None:
        self._raise_read_only()

    def write_bytes(self, data: bytes, mode: BinaryWriteMode = "wb") -> None:
        self._raise_read_only()

    def delete(self) -> None:
        self._raise_read_only()

    def exists(self) -> bool:
        return self._absolute_path.exists()
