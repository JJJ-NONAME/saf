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

import random
import uuid

from ansys.saf.glow.solution import (
    Migration,
    MigrationContext,
    MigrationTransformation,
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    transaction,
)


class MigrateToVersion2(MigrationTransformation):
    def migrate(self, ctx: MigrationContext) -> None:
        ctx.steps["first_step"]["x"] = 100


class MigrateToVersion3(MigrationTransformation):
    def migrate(self, ctx: MigrationContext) -> None:
        ctx.steps["first_step"]["my_string"] = "not_my_string"


class MigrateToVersion4(MigrationTransformation):
    def migrate(self, ctx: MigrationContext) -> None:
        ctx.steps["first_step"]["my_string"] = "my_string"


class FirstStep(StepModel):
    x: int = 100
    my_string: str = "my_string"
    unused_value: float = 0.5
    str_int: str = "1"
    is_new_field: bool = True

    @transaction(self=StepSpec(download=["x"], upload=["my_string"]))
    def copy_x_to_string(self) -> None:
        self.my_string = str(self.x)

    @transaction(self=StepSpec(upload=["my_string"]))
    def generate_random_string(self) -> None:
        self.my_string = str(random.randint(0, 10))


class SecondStep(StepModel):
    x: int = 88
    my_string: str = "my_string"

    @transaction(self=StepSpec(download=["x"], upload=["my_string"]))
    def copy_x_to_string(self) -> None:
        self.my_string = str(self.x)

    @transaction(self=StepSpec(upload=["my_string"]))
    def generate_random_string(self) -> None:
        self.my_string = str(uuid.uuid4())


class Steps(StepsModel):
    first_step: FirstStep
    second_step: SecondStep


class OriginalSolution(Solution):
    version: int = 3
    display_name: str = "Original"
    steps: Steps
    migrations: list[Migration] = [
        Migration(version=1, migration_transformation=MigrateToVersion2()),
        Migration(version=2, migration_transformation=MigrateToVersion3()),
        Migration(version=3, migration_transformation=MigrateToVersion4()),
    ]
