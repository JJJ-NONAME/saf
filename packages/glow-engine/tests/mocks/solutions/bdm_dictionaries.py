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

import logging
from pathlib import Path

from ansys.saf.glow.solution import (
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
from tests.mocks.instance_managers.mock_product_manager import (
    MockGrpcProductInstanceManager,
)

logger = logging.getLogger(__name__)


class BdmDictionariesStep(StepModel):
    my_entities: RecursiveDictionaryOfEntityHandles = RecursiveDictionaryOfEntityHandles()
    my_entities_simple_syntax: RecursiveDictionaryOfEntityHandles = {}  # pyright: ignore[reportAssignmentType]

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

    @transaction(self=StepSpec(upload=["my_entities_simple_syntax"]))
    def manually_create_entities_dict_simple_syntax(self) -> None:
        root_dir = self.storage_scope.get_storage_root()
        txt_file = root_dir / "root_file.txt"
        txt_file.write_text("This is a file in the root directory")
        json_subdir_file = root_dir / "level1_file.json"
        json_subdir_file.write_text('{"key": "value"}')
        self.my_entities_simple_syntax = {
            "root_file.txt": self.storage_scope.store(txt_file),
            "subdir1": {
                "level1_file.json": self.storage_scope.store(json_subdir_file),
            },  # pyright: ignore[reportAttributeAccessIssue]
        }

    @transaction(self=StepSpec(upload=["my_entities"]))
    def upload_directory_to_entities_dict(self, glob: str | None = None) -> None:
        root_dir = self.storage_scope.get_storage_root()
        txt_file = root_dir / "root_file.txt"
        txt_file.write_text("This is a file in the root directory")
        json_subdir_file = root_dir / "subdir1" / "level1_file.json"
        json_subdir_file.parent.mkdir()
        json_subdir_file.write_text('{"key": "value"}')
        self.my_entities = self.storage_scope.store_to_dictionary(root_dir, glob)

    @transaction(self=StepSpec(upload=["my_entities"]))
    @long_running
    def upload_directory_to_entities_dict_lr(self, glob: str | None = None) -> None:
        root_dir = self.storage_scope.get_storage_root()
        txt_file = root_dir / "root_file.txt"
        txt_file.write_text("This is a file in the root directory")
        json_subdir_file = root_dir / "subdir1" / "level1_file.json"
        json_subdir_file.parent.mkdir()
        json_subdir_file.write_text('{"key": "value"}')
        self.my_entities = self.storage_scope.store_to_dictionary(root_dir, glob)

    @transaction(self=StepSpec(download=["my_entities"]))
    def download_directory_from_entities_dict(self, glob: str | None = None) -> list[Path]:
        output_dir = self.storage_scope.get_storage_root() / "output_dir"
        self.storage_scope.get_copy_from_dictionary(output_dir, self.my_entities, glob)
        return [path.relative_to(output_dir) for path in output_dir.rglob("*")]

    @transaction(self=StepSpec(download=["my_entities_simple_syntax"]))
    def download_directory_from_entities_dict_simple_syntax(self, glob: str | None = None) -> list[Path]:
        output_dir = self.storage_scope.get_storage_root() / "output_dir"
        self.storage_scope.get_copy_from_dictionary(output_dir, self.my_entities_simple_syntax, glob)
        return [path.relative_to(output_dir) for path in output_dir.rglob("*")]

    @transaction(self=StepSpec(download=["my_entities"]))
    @long_running
    def download_directory_from_entities_dict_lr(self, glob: str | None = None) -> list[Path]:
        output_dir = self.storage_scope.get_storage_root() / "output_dir"
        self.storage_scope.get_copy_from_dictionary(output_dir, self.my_entities, glob)
        return [path.relative_to(output_dir) for path in output_dir.rglob("*")]

    @transaction(self=StepSpec())
    @create_instance("x_y", MockGrpcProductInstanceManager)
    def launch_product(self, x_y: MockGrpcProductInstanceManager) -> None:
        x_y.initialize()

    @transaction(self=StepSpec(download=["my_entities"]))
    @instance("x_y")
    def download_directory_into_product_space(self, x_y: MockGrpcProductInstanceManager) -> list[Path]:
        product_dir = x_y.storage_scope.get_storage_root() / "product_dir"
        x_y.storage_scope.get_copy_from_dictionary(product_dir, self.my_entities)
        return [path.relative_to(product_dir) for path in Path(product_dir).rglob("*")]

    @transaction(self=StepSpec(upload=["my_entities"]))
    @instance("x_y")
    def upload_directory_from_product_space(self, x_y: MockGrpcProductInstanceManager) -> None:
        product_dir = x_y.storage_scope.get_storage_root() / "product_dir"
        project_file = product_dir / "root_file.txt"
        x_y.instance.store_given_absolute_path(str(project_file))
        another_file = product_dir / "subdir1" / "level1_file.json"
        x_y.instance.store_given_absolute_path(str(another_file))
        self.my_entities = x_y.storage_scope.store_to_dictionary(product_dir)

    @transaction(self=StepSpec(download=["my_entities"], upload=["my_entities"]))
    @instance("x_y")
    def extend_directory_from_product_space(self, x_y: MockGrpcProductInstanceManager) -> None:
        product_dir = x_y.storage_scope.get_storage_root() / "product_dir"
        project_file = product_dir / "product_system_file.txt"
        x_y.instance.store_given_absolute_path(str(project_file))
        self.my_entities["product_system"] = x_y.storage_scope.store_to_dictionary(product_dir)

    @transaction(self=StepSpec())
    @instance("x_y")
    def shutdown_product(self, x_y: MockGrpcProductInstanceManager) -> None:
        x_y.shutdown()


class Steps(StepsModel):
    bdm_dicts_step: BdmDictionariesStep


class BdmDictionariesSolution(Solution):
    display_name: str = "Bdm Dictionaries Solution"
    steps: Steps
