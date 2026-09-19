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

"""Backend for basic solution example."""

import time
from typing import Any
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont
from ansys.bdm.api import NO_ENTITY, EntityHandle
from ansys.saf.glow.solution import StepModel, StepSpec, long_running, transaction

from saf.solutions.examples.solution.scripts import parametric_curves
from saf.solutions.examples.solution.scripts.table_logic import generate_table_data


class BasicStep(StepModel):
    """Definition of the basic step."""

    result_files: list[EntityHandle] = []
    log_file: EntityHandle = NO_ENTITY
    data_dict: dict[str, Any] = {}
    table_flag: bool = False
    x_coords: list[float] = []
    y_coords: list[float] = []
    distance: list[float] = []
    selected_curve: str = "windmill"

    @transaction(self=StepSpec())
    def simple_blocking_process(self, wait_time: float) -> None:
        """Trigger a blocking process that waits for some time."""
        start_time = time.time()
        while (time.time() - start_time) < wait_time:
            time.sleep(0.5)

    @transaction(self=StepSpec())
    @long_running
    def simple_long_running_process(self, force_failure: bool, wait_time: float) -> None:
        """Trigger a non-blocking process that waits for some time and can be set to fail."""
        start_time = time.time()
        while (time.time() - start_time) < wait_time:
            time.sleep(0.5)
        if force_failure:
            raise Exception("This is a forced failure.")

    @transaction(self=StepSpec(download=["log_file"], upload=["log_file"]), enable_termination_event=True)
    @long_running
    def generate_process_logs(self, wait_time: float) -> None:
        """Write the current time to a file every second for a certain amount of time."""
        try:
            log_file = self.storage_scope.get_cached(self.log_file)
            existing_logs = log_file.read_bytes()
        except Exception:
            existing_logs = b""
        start_time = time.time()
        while (time.time() - start_time) < wait_time:
            current_time = f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n"
            existing_logs += current_time.encode()
            self.log_file = self.storage_scope.store_stream(existing_logs)
            self.transaction.raise_event(message=current_time, stream_name="generate-process-logs-update")
            time.sleep(1)

    @transaction(self=StepSpec(upload=["log_file"]))
    def clear_logs(self) -> None:
        """Clear the log file."""
        self.log_file = NO_ENTITY

    @transaction(self=StepSpec(upload=["result_files"]))
    def create_images(self) -> None:
        """Mimic the creation of 3 png files by using pillow library."""
        images_path = self.storage_scope.get_storage_root() / "images"
        images_path.mkdir()

        self.result_files = []
        for _ in range(3):
            image_name = f"Image_{str(uuid4())}.png"
            image_path = images_path / image_name
            image_with_background = Image.new("RGB", (400, 300), "grey")
            ImageDraw.Draw(image_with_background).text(  # pyright: ignore[reportUnknownMemberType]
                (20, 150), image_name, font=ImageFont.truetype("arial.ttf", size=20)
            )
            image_with_background.save(image_path)
            image_handle = self.storage_scope.store(image_path)
            self.result_files.append(image_handle)

    @transaction(self=StepSpec(upload=["data_dict", "table_flag"]))
    def generate_data(self) -> None:
        """Generate the data for the table."""
        data_dict = generate_table_data()
        self.data_dict = data_dict
        self.table_flag = True

    @transaction(self=StepSpec(upload=["x_coords", "y_coords", "distance"], download=["selected_curve"]))
    def compute_parametric_curve(self) -> None:
        """Compute a parametric curve based on the selected curve type."""
        self.x_coords, self.y_coords, self.distance = parametric_curves.compute_rd_curve(self.selected_curve)
