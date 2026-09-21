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
from time import sleep

from ansys.saf.glow.solution import (
    BadRequestError,
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    long_running,
    transaction,
)

logger = logging.getLogger(__name__)


class AnotherStep(StepModel):
    x: int = 88


class MethodStep(StepModel):
    """This is a step for testing purpose."""

    x: int = 99

    @transaction(self=StepSpec(upload=["x"]))
    def increment(self) -> None:
        """Increment x by one."""
        self.x = 100

    @transaction(self=StepSpec(download=["x"]))
    def bang(self) -> None:
        """Raise an exception."""
        raise RuntimeError("BANG!")

    @transaction(self=StepSpec(upload=["x"]))
    @long_running
    def slow(self) -> None:
        sleep(1)
        self.x = 103

    @transaction(self=StepSpec())
    @long_running
    def one_second(self) -> None:
        sleep(1)

    @transaction(self=StepSpec())
    def one_second_sync(self) -> None:
        logger.info("STARTING one_second_sync")
        sleep(1)
        logger.info("LEAVING one_second_sync")

    @transaction(self=StepSpec())
    @long_running
    def two_seconds(self) -> None:
        sleep(2)

    @transaction(self=StepSpec(download=["x"]))
    @long_running
    def slow_exception(self) -> None:
        sleep(1)
        raise BadRequestError("Bang! Bang!")

    def hidden(self) -> None:
        self.x = 0

    @transaction(self=StepSpec(download=["x"]))
    def empty_return(self):
        """Return nothing."""
        return

    @transaction(self=StepSpec(upload=["x"]))
    def do_underscore(self) -> None:
        """Increments x by two."""
        self.x = 102

    @transaction(self=StepSpec(upload=["x"]), another_step=StepSpec(download=["x"]))
    @long_running
    def act_on_another_step(self, another_step: AnotherStep) -> None:
        self.x = another_step.x + 1


class OtherStep(StepModel):
    id: int = 1234


class Steps(StepsModel):
    method_step: MethodStep
    another_step: AnotherStep
    other_step: OtherStep


class HasMethods(Solution):
    display_name: str = "Has Methods"
    steps: Steps
