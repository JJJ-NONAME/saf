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
    Migration,
    MigrationContext,
    MigrationTransformation,
    Solution,
    StepModel,
    StepsModel,
)


def _remove_old_fields(ctx: MigrationContext) -> None:
    del ctx.steps["first_step"]["always_no_entity_handle"]
    del ctx.steps["first_step"]["existing_entity_handle"]


class ExtractFromEntityHandle(MigrationTransformation):
    def migrate(self, ctx: MigrationContext) -> None:
        file_path = ctx.get_path_from_entity_handle(ctx.steps["first_step"]["existing_entity_handle"])
        assert file_path is not None, "Expected a valid file path from the entity handle"
        ctx.steps["first_step"]["extracted_file_content"] = file_path.read_text()
        _remove_old_fields(ctx)


class FirstStep(StepModel):
    x: int = 88
    extracted_file_content: str = ""


class Steps(StepsModel):
    first_step: FirstStep


class OriginalSolution(Solution):
    version: int = 2
    display_name: str = "Original for File Migration"
    steps: Steps
    migrations: list[Migration] = [Migration(version=1, migration_transformation=ExtractFromEntityHandle())]
