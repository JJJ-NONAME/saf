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

from ansys.saf.glow.solution import (
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    transaction,
)


class StepWithAssets(StepModel):
    content_of_asset: str = ""

    @transaction(self=StepSpec(upload=["content_of_asset"]))
    def retrieve_always_decrypted_assets(self):
        self.content_of_asset = self.storage_scope.get_text(
            self.transaction.get_asset_entity_handle("asset_always_decrypted.txt"),
        )

    @transaction(self=StepSpec(upload=["content_of_asset"]))
    def retrieve_decrypted_for_debug_assets(self):
        self.content_of_asset = self.storage_scope.get_text(
            self.transaction.get_asset_entity_handle("asset_decrypted_for_debug.txt"),
        )

    @transaction(self=StepSpec(upload=["content_of_asset"]))
    def retrieve_encrypted_assets(self):
        self.content_of_asset = self.storage_scope.get_text(
            self.transaction.get_asset_entity_handle("asset_encrypted.txt"),
        )

    @transaction(self=StepSpec(upload=["content_of_asset"]))
    def retrieve_asset_dir(self):
        dir_handle = self.transaction.get_asset_entity_handle("dir")
        asset_handle = self.storage_scope.get_child(entity=dir_handle, child_name="asset_decrypted.txt")
        self.content_of_asset = self.storage_scope.get_text(asset_handle)


class Steps(StepsModel):
    step_with_assets: StepWithAssets


class SolutionAssetsWithAutoKey(Solution):
    display_name: str = "Solution with auto key assets"
    steps: Steps
