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

from pathlib import Path
import shutil
import time
from typing import Dict, List, Tuple  # noqa: UP035 (for testing)

from pydantic import BaseModel

from ansys.saf.glow.solution import (
    NO_ENTITY,
    EntityHandle,
    RecursiveDictionaryOfEntityHandles,
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    create_instance,
    instance,
    long_running,
    transaction,
)
from tests.mocks.instance_managers.mock_product_manager import MockGrpcProductInstanceManager


class InnerSubModel(BaseModel):
    s: str = "inner"
    inner_sub_handle: EntityHandle = NO_ENTITY
    inner_sub_no_entity: EntityHandle = NO_ENTITY


class SubModel(BaseModel):
    i: int = 1
    sub_handle: EntityHandle = NO_ENTITY
    sub_no_entity: EntityHandle = NO_ENTITY
    inner_sub: InnerSubModel = InnerSubModel()
    untyped_dict: Dict = {}  # pyright: ignore  # noqa: UP006
    untyped_list: List = ["untyped"]  # pyright: ignore  # noqa: UP006


class BdmStep(StepModel):
    my_entity: EntityHandle = NO_ENTITY
    no_entity: EntityHandle = NO_ENTITY
    other: int = 0
    result: EntityHandle = NO_ENTITY
    another_result: EntityHandle = NO_ENTITY
    directory: EntityHandle = NO_ENTITY
    file: EntityHandle = NO_ENTITY
    list_handles: list[EntityHandle] = []
    dict_handles: dict[str, EntityHandle] = {}
    dict_int: dict[str, int] = {}
    sub: SubModel = SubModel()
    my_entities: RecursiveDictionaryOfEntityHandles = RecursiveDictionaryOfEntityHandles()
    untyped_dict: Dict = {}  # pyright: ignore  # noqa: UP006
    untyped_list: List = ["untyped"]  # pyright: ignore  # noqa: UP006
    untyped_tuple: Tuple = (1, 2)  # pyright: ignore  # noqa: UP006

    @transaction(self=StepSpec())
    def store_file_but_no_upload(self) -> EntityHandle:
        my_file_txt = self.storage_scope.get_storage_root() / "my_file.txt"
        my_file_txt.write_text("hello world!")
        return self.storage_scope.store(my_file_txt)

    @transaction(self=StepSpec())
    @long_running
    def store_file_but_no_upload_long_running(self) -> EntityHandle:
        my_file_txt = self.storage_scope.get_storage_root() / "my_file.txt"
        my_file_txt.write_text("hello world!")
        return self.storage_scope.store(my_file_txt)

    @transaction(self=StepSpec(upload=["my_entity"]))
    def store_my_entity(self) -> None:
        self.my_entity = self.storage_scope.store_stream(b"hello world!")

    @transaction(self=StepSpec(upload=["result"]))
    def store_stream(self) -> None:
        self.result = self.storage_scope.store_stream(b"hello world!")

    @transaction(self=StepSpec(upload=["result"]))
    def begin_store_no_relative_location(self) -> None:
        with self.storage_scope.begin_store() as writer:
            writer.stream.write(b"hello world!")
        self.result = writer.handle

    @transaction(self=StepSpec(upload=["result"]))
    def begin_store_result(self) -> None:
        with self.storage_scope.begin_store(Path("result.txt")) as writer:
            writer.stream.write(b"hello world!")
        self.result = writer.handle

    @transaction(self=StepSpec(upload=["result"]))
    def overwrite_result(self) -> None:
        result_txt = self.storage_scope.get_storage_root() / "result.txt"
        result_txt.write_text("another hello world!")
        self.result = self.storage_scope.store(result_txt)

    @transaction(self=StepSpec(upload=["result"]))
    @long_running
    def overwrite_result_long_running(self) -> None:
        result_txt = self.storage_scope.get_storage_root() / "result.txt"
        result_txt.write_text("another hello world!")
        self.result = self.storage_scope.store(result_txt)

    @transaction(self=StepSpec(upload=["result"]))
    def store_result(self) -> None:
        result_txt = self.storage_scope.get_storage_root() / "result.txt"
        result_txt.write_text("hello world!")
        self.result = self.storage_scope.store(result_txt)

    @transaction(self=StepSpec(upload=["result"]))
    def store_file(self, filename: Path) -> None:
        storage_root = self.storage_scope.get_storage_root()
        target = storage_root / filename.name
        shutil.copyfile(filename, target)
        self.result = self.storage_scope.store(target)

    @transaction(self=StepSpec(upload=["list_handles"]))
    def store_list_handles(self) -> None:
        f = self.storage_scope.get_storage_root() / "list_handles.txt"
        f.write_text("list_handles.txt")
        self.list_handles = [self.storage_scope.store(f)]

    @transaction(self=StepSpec(upload=["list_handles"]))
    def remove_list_handles(self) -> None:
        self.list_handles = []

    @transaction(self=StepSpec(download=["list_handles"], upload=["list_handles"]))
    def pop_list_handles(self) -> None:
        self.list_handles.pop()

    @transaction(self=StepSpec())
    def get_text_from_input_handle_no_download(self, handle: EntityHandle) -> str:
        return self.storage_scope.get_text(handle)

    @transaction(self=StepSpec(download=["list_handles"]))
    def get_text_first_item_list_handles(self) -> str:
        return self.storage_scope.get_text(self.list_handles[0])

    @transaction(self=StepSpec(download=["dict_handles"]))
    def get_text_handle_item_dict_handles(self) -> str:
        return self.storage_scope.get_text(self.dict_handles["dict_handle"])

    @transaction(self=StepSpec(download=["sub"]))
    def get_text_sub_handle(self) -> str:
        return self.storage_scope.get_text(self.sub.sub_handle)

    @transaction(self=StepSpec(download=["sub"]))
    def get_text_inner_sub_handle(self) -> str:
        return self.storage_scope.get_text(self.sub.inner_sub.inner_sub_handle)

    @transaction(self=StepSpec(upload=["dict_handles"]))
    def store_dict_handles(self) -> None:
        f = self.storage_scope.get_storage_root() / "dict_handles.txt"
        f.write_text("dict_handles.txt")
        self.dict_handles = {"dict_handle": self.storage_scope.store(f)}

    @transaction(self=StepSpec(upload=["dict_handles"]))
    def store_handle_in_dictionary_with_key_containing_multiple_forward_slashes(self) -> None:
        f = self.storage_scope.get_storage_root() / "dict_handles.txt"
        f.write_text("stored with complex key")
        self.dict_handles = {"a/b/c": self.storage_scope.store(f)}

    @transaction(self=StepSpec(upload=["dict_handles"]))
    def store_handle_in_dictionary_with_key_containing_characters_requiring_backslash_escape(self) -> None:
        f = self.storage_scope.get_storage_root() / "dict_handles.txt"
        f.write_text("stored with back slash escaped key")
        self.dict_handles = {"a\\/b": self.storage_scope.store(f)}

    @transaction(self=StepSpec(upload=["my_entities"]))
    def store_handle_in_nested_dictionary_with_key_containing_characters_requiring_backslash_escape(self) -> None:
        f = self.storage_scope.get_storage_root() / "dict_handles.txt"
        f.write_text("stored nested with back slash escaped key")
        self.my_entities = RecursiveDictionaryOfEntityHandles(
            {"ab a\\b a\\": RecursiveDictionaryOfEntityHandles({"b": self.storage_scope.store(f)})},
        )

    @transaction(self=StepSpec(upload=["dict_handles"]))
    def store_handle_in_dictionary_with_key_containing_characters_requiring_url_escape(self) -> None:
        f = self.storage_scope.get_storage_root() / "dict_handles.txt"
        f.write_text("stored with escaped key")
        self.dict_handles = {" ()+[]{}%*<>?-_": self.storage_scope.store(f)}

    @transaction(self=StepSpec(upload=["sub"]))
    def store_sub_model(self) -> None:
        sub_file = self.storage_scope.get_storage_root() / "sub.txt"
        sub_file.write_text("sub")
        sub_handle = self.storage_scope.store(sub_file)
        inner_sub_file = self.storage_scope.get_storage_root() / "inner_sub.txt"
        inner_sub_file.write_text("inner_sub")
        inner_sub_handle = self.storage_scope.store(inner_sub_file)
        self.sub = SubModel(sub_handle=sub_handle, inner_sub=InnerSubModel(inner_sub_handle=inner_sub_handle))

    @transaction(self=StepSpec(upload=["result"]))
    def store_result_and_return_stored_entities(self) -> list[EntityHandle]:
        result_txt = self.storage_scope.get_storage_root() / "result.txt"
        result_txt.write_text("hello world!")
        self.result = self.storage_scope.store(result_txt)
        return self.storage_scope.stored_entities

    @transaction(self=StepSpec(upload=["result"]))
    @long_running
    def store_result_long_running(self) -> None:
        result_txt = self.storage_scope.get_storage_root() / "result.txt"
        result_txt.parent.mkdir(exist_ok=True, parents=True)
        result_txt.write_text("hello world!")
        self.result = self.storage_scope.store(result_txt)

    @transaction(self=StepSpec(upload=["another_result"]))
    def store_another_result(self) -> None:
        result_txt = self.storage_scope.get_storage_root() / "another_result.txt"
        result_txt.write_text("hello other worlds!")
        self.another_result = self.storage_scope.store(result_txt)

    @transaction(self=StepSpec(upload=["result", "another_result"]))
    def store_two_results(self) -> None:
        result_txt = self.storage_scope.get_storage_root() / "result.txt"
        result_txt.write_text("hello world!")
        handle = self.storage_scope.store(result_txt)
        self.result = handle
        self.another_result = handle

    @transaction(self=StepSpec(upload=["directory"]))
    def store_directory_in_entity_handle(self) -> None:
        root = self.storage_scope.get_storage_root()
        top = root / "top"
        top.mkdir()
        (top / "empty").mkdir()
        subtop = top / "subtop"
        subtop.mkdir()
        leaf = subtop / "leaf.txt"
        leaf.write_text("hello world!")
        self.directory = self.storage_scope.store(top)

    @transaction(self=StepSpec(upload=["file"]))
    def store_file_in_entity_handle(self) -> None:
        root = self.storage_scope.get_storage_root()
        tree = root / "tree"
        tree.mkdir()
        leaf = tree / "leaf.txt"
        leaf.write_text("hello world!")
        self.file = self.storage_scope.store(leaf)

    @transaction(self=StepSpec(download=["result"]))
    def get_copy_result(self, destination: str) -> None:
        self.storage_scope.get_copy(self.result, Path(destination))

    @transaction(self=StepSpec(download=["result"]))
    def get_cached_result(self) -> Path:
        path = self.storage_scope.get_cached(self.result)
        return path

    @transaction(self=StepSpec(download=["result"]))
    @long_running
    def get_cached_result_long_running(self) -> Path:
        path = self.storage_scope.get_cached(self.result)
        return path

    @transaction(self=StepSpec(download=["result"]))
    def get_text_result(self) -> str:
        result_text = self.storage_scope.get_text(self.result)
        return result_text

    @transaction(self=StepSpec(download=["result"]))
    @long_running
    def get_text_result_long_running(self) -> str:
        result_text = self.storage_scope.get_text(self.result)
        return result_text

    @transaction(self=StepSpec(download=["result"]))
    def get_stream_result(self) -> str:
        stream_bytes = self.storage_scope.get_stream(self.result).readall()
        return stream_bytes.decode()

    @transaction(self=StepSpec(download=["directory"]))
    def get_directory_children(self) -> list[EntityHandle]:
        return self.storage_scope.get_children(self.directory)

    @transaction(self=StepSpec(download=["directory"]))
    def get_directory_child(self) -> EntityHandle:
        return self.storage_scope.get_child(self.directory, "empty")

    @transaction(self=StepSpec(download=["file"], upload=["directory"]))
    def get_directory_parent(self) -> None:
        self.directory = self.storage_scope.get_parent(self.file) or NO_ENTITY

    @transaction(self=StepSpec(upload=["result"]))
    def delete_result(self) -> None:
        self.result = NO_ENTITY

    @transaction(self=StepSpec(download=["file"]))
    @long_running
    def wait_for_signal_file(self, signal_file: Path) -> None:
        signal_file.write_text("inside transaction")
        signal_received = False
        for _ in range(500):
            try:
                signal_received = signal_file.read_text() == "stop"
            except PermissionError:
                continue
            if signal_received:
                return
            time.sleep(0.1)

    @transaction(self=StepSpec())
    @create_instance("x_y", MockGrpcProductInstanceManager)
    def launch_product(self, x_y: MockGrpcProductInstanceManager) -> None:
        x_y.initialize()

    @transaction(self=StepSpec())
    @instance("x_y")
    def close_product(self, x_y: MockGrpcProductInstanceManager) -> None:
        x_y.shutdown()

    @transaction(self=StepSpec(download=["result"]))
    @long_running
    def raise_not_a_directory_error_long_running(self) -> None:
        self.storage_scope.get_children(self.result)

    @transaction(self=StepSpec(upload=["my_entities"]))
    def manually_create_entities_dict(self) -> None:
        root_dir = self.storage_scope.get_storage_root()
        txt_file = root_dir / "root_file.txt"
        txt_file.write_text("This is a file in the root directory")
        json_subdir_file = root_dir / "level1_file.json"
        json_subdir_file.write_text('{"key": "value"}')
        my_dict = RecursiveDictionaryOfEntityHandles()
        my_dict["root_file.txt"] = self.storage_scope.store(txt_file)
        my_subdir_1 = RecursiveDictionaryOfEntityHandles()
        my_subdir_1["level1_file.json"] = self.storage_scope.store(json_subdir_file)
        my_dict["subdir1"] = my_subdir_1
        self.my_entities = my_dict

    @transaction(self=StepSpec(download=["other"]))
    def duplicate_other(self) -> int:
        return self.other * 2

    @transaction(self=StepSpec(upload=["other"]))
    def upload_other(self, other: int) -> None:
        self.other = other

    @transaction(self=StepSpec(upload=["my_entities"]))
    def upload_directory_to_recursive_dict(self, glob: str | None = None) -> None:
        root_dir = self.storage_scope.get_storage_root()
        txt_file = root_dir / "root_file.txt"
        txt_file.write_text("This is a file in the root directory")
        json_subdir_file = root_dir / "subdir1" / "level1_file.json"
        json_subdir_file.parent.mkdir()
        json_subdir_file.write_text('{"key": "value"}')
        self.my_entities = self.storage_scope.store_to_dictionary(root_dir, glob)

    @transaction(self=StepSpec(download=["my_entities"]))
    def download_directory_from_recursive_dict(self, glob: str | None = None) -> list[Path]:
        output_dir = self.storage_scope.get_storage_root() / "output_dir"
        self.storage_scope.get_copy_from_dictionary(output_dir, self.my_entities, glob)
        return [path.relative_to(output_dir) for path in output_dir.rglob("*")]


class OtherBdmStep(StepModel):
    @transaction(self=StepSpec(), bdm_step=StepSpec(download=["file"]))
    def get_text_from_handle_from_other_step(self, bdm_step: BdmStep) -> str:
        return self.storage_scope.get_text(bdm_step.file)


class Steps(StepsModel):
    bdm_step: BdmStep
    other_bdm_step: OtherBdmStep


class BdmSolution(Solution):
    display_name: str = "Bdm Solution"
    steps: Steps
