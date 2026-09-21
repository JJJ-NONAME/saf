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

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel

from ansys.saf.glow.solution import Solution, StepModel, StepsModel, StepSpec, transaction


class FutureAnnotationsPayload(BaseModel):
    rebuild_called: ClassVar[bool] = False
    path: Path = Path()

    @classmethod
    def model_rebuild(cls, *args: Any, **kwargs: Any):
        cls.rebuild_called = True
        return super().model_rebuild(*args, **kwargs)


class FutureAnnotationsStep(StepModel):
    value: int = 1
    payload: FutureAnnotationsPayload = FutureAnnotationsPayload()

    @transaction(self=StepSpec(download=["payload"]))
    def get_payload(self) -> FutureAnnotationsPayload:
        return self.payload


class FutureAnnotationsSteps(StepsModel):
    future_annotations_step: FutureAnnotationsStep


class FutureAnnotationsSolution(Solution):
    display_name: str = "Future Annotations"
    steps: FutureAnnotationsSteps
