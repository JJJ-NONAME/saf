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

import uuid

from ansys.saf.glow.solution import (
    NO_ENTITY,
    EntityHandle,
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    transaction,
)


class BdmBenchmarkStep(StepModel):
    list_handles: list[EntityHandle] = []
    file_bdm: EntityHandle = NO_ENTITY

    @transaction(self=StepSpec(download=["list_handles"], upload=["list_handles"]))
    def modify_list_handles(self, start: int, end: int) -> None:
        for i in range(start, end):
            file = self.storage_scope.get_storage_root().joinpath(f"file_{i}.txt")
            file.write_text(str(uuid.uuid4()))
            handle = self.storage_scope.store(file)
            self.list_handles[i] = handle

    @transaction(self=StepSpec(upload=["list_handles"]))
    def initialize_list_handles(self, size: int) -> None:
        self.list_handles = [NO_ENTITY] * size

    @transaction(self=StepSpec(upload=["file_bdm"]))
    def populated_bdm_content(self) -> None:
        data = "a" * 100
        bdm_content = f"Dummy content bdm {data}."
        file_path = self.storage_scope.get_storage_root() / "bdm_file.txt"
        file_path.write_text(bdm_content)
        self.file_bdm = self.storage_scope.store(file_path)

    @transaction(self=StepSpec())
    def get_content_as_response(self) -> str:
        data = "a" * 100
        return data


class Steps(StepsModel):
    bdm_step: BdmBenchmarkStep


class BdmBenchmarkSolution(Solution):
    display_name: str = "Bdm Benchmark Solution"
    steps: Steps
