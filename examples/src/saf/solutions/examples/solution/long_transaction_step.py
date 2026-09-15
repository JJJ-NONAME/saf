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

# ©2023, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Long transaction example step model."""
import datetime
import time

from ansys.saf.glow.solution import StepModel, StepSpec, long_running, transaction


class LongTransactionStep(StepModel):
    """Long transaction example step model."""

    status: str = "[]"
    processing: bool = False
    number_of_increments: int = 50
    current_increment: int = -1

    @long_running
    @transaction(
        self=StepSpec(
            download=["processing", "number_of_increments"],
            upload=["status", "current_increment"],
        )
    )
    def stream_updates(self) -> None:
        """Stream updates to the frontend."""
        for i in range(self.number_of_increments):
            self.status = f"Update {i} at  {_now()}"
            self.current_increment = i
            self.transaction.upload(["status", "current_increment"])
            time.sleep(1)
        self.status = f"Last updated at {_now()}"


def _now():
    return datetime.datetime.now().strftime("%H:%M:%S")
