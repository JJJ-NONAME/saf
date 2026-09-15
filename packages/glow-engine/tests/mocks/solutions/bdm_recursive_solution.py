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

from pydantic import BaseModel

from ansys.saf.glow.solution import (
    NO_ENTITY,
    EntityHandle,
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    transaction,
)


class RecursiveThing(BaseModel):
    children: list["RecursiveThing"] = []
    handle: EntityHandle = NO_ENTITY


class BdmStep(StepModel):
    recursive_thing: RecursiveThing = RecursiveThing()

    @transaction(self=StepSpec(upload=["recursive_thing"]))
    def upload_recursive_thing(self) -> None:
        root_dir = self.storage_scope.get_storage_root()
        parent = root_dir / "parent.txt"
        parent.write_text("This is a parent")
        child = root_dir / "child.txt"
        child.write_text("This is a child")
        self.recursive_thing = RecursiveThing(
            handle=self.storage_scope.store(parent),
            children=[RecursiveThing(handle=self.storage_scope.store(child), children=[])],
        )

    @transaction(self=StepSpec(download=["recursive_thing"]))
    def download_child_from_recursive_thing(self) -> str:
        return self.storage_scope.get_text(self.recursive_thing.children[0].handle)


class Steps(StepsModel):
    bdm_step: BdmStep


class BdmSolution(Solution):
    display_name: str = "Bdm Solution"
    steps: Steps
