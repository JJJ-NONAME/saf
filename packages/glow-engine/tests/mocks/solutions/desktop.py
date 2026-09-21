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

from pathlib import Path
import time

from ansys.saf.glow.solution import (
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    long_running,
    transaction,
)


class DesktopStep(StepModel):
    """This is a step for testing purpose."""

    x: int = 99
    sleep_time: int = 500

    @transaction(self=StepSpec(download=["sleep_time"], upload=["x"]))
    @long_running
    def infinity_lr(self, signal_file: Path) -> None:
        """Run almost forever"""
        for _ in range(int(self.sleep_time / 10)):
            if signal_file.read_text() == "stop":
                break
            time.sleep(0.1)
        self.x = 100

    @transaction(self=StepSpec(download=["sleep_time"], upload=["x"]))
    def infinity(self, signal_file: Path) -> None:
        """Run almost forever"""
        for _ in range(int(self.sleep_time / 10)):
            if signal_file.read_text() == "stop":
                break
            time.sleep(0.1)
        self.x = 100


class Steps(StepsModel):
    desktop_step: DesktopStep


class DesktopSolution(Solution):
    display_name: str = "Desktop"
    steps: Steps
