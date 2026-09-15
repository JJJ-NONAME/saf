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

from typing import Any

import numpy as np
from pydantic import BaseModel

from ansys.saf.glow.solution import (
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    long_running,
    transaction,
)


class CustomField(BaseModel):
    x: int
    y: int
    z: int


class EventsStep(StepModel):
    message: CustomField | Any = None
    stream_name: str | None = None

    @transaction(self=StepSpec(download=["message", "stream_name"]))
    def raise_event(self) -> None:
        self.transaction.raise_event(self.message, self.stream_name)

    @transaction(self=StepSpec(download=["message", "stream_name"]))
    @long_running
    def raise_event_long(self) -> None:
        self.transaction.raise_event(self.message, self.stream_name)

    @transaction(self=StepSpec(download=["stream_name"]))
    def raise_other_event(self) -> None:
        self.transaction.raise_event({"message": "other event"}, self.stream_name)

    @transaction(self=StepSpec(download=["stream_name"]))
    def raise_multiple_events(self) -> None:
        for i in range(3):
            self.transaction.raise_event({"message": i}, self.stream_name)

    @transaction(self=StepSpec(download=["stream_name"]))
    def raise_invalid_event(self) -> None:
        array = np.array([[1, 2], [3, 4]])
        self.transaction.raise_event(array, self.stream_name)  # type: ignore

    @transaction(enable_termination_event=True)
    def raise_termination_event(self) -> None:
        return

    @transaction(enable_termination_event=True)
    @long_running
    def raise_termination_event_long_running(self) -> None:
        return

    @transaction(enable_termination_event=True)
    def raise_failed_termination_event(self) -> None:
        raise ValueError("This transaction was forced to fail.")

    @transaction(enable_termination_event=True)
    @long_running
    def raise_failed_termination_event_long_running(self) -> None:
        raise ValueError("This transaction was forced to fail.")

    @transaction()
    def dont_raise_termination_event(self) -> None:
        return


class Steps(StepsModel):
    events_step: EventsStep


class EventsSolution(Solution):
    display_name: str = "Events"
    steps: Steps
