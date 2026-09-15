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


"""Backend of the first step."""

import contextlib
import logging
from pathlib import Path
from random import randrange
import time
from typing import ClassVar

from ansys.saf.glow.solution import (
    NO_ENTITY,
    EntityHandle,
    StepModel,
    StepSpec,
    long_running,
    transaction,
)
from pydantic import BaseModel


class ExpiringEntityHandle(BaseModel):
    """Stores an entity handle with its expiry time."""

    expiry_time: float = 0.0
    entity_handle: EntityHandle = NO_ENTITY


class SimpleStep(StepModel):
    """Step definition of the first step."""

    # time after which log file entity handles are considered outdated and can be deleted from BDM
    # must be longer than the maximum expected duration of a callback accessing the log file to
    # avoid deletion of log files which are still in use
    EXPIRY_TIME_SECONDS: ClassVar[int] = 3

    # attributes used by ``compute_sum`` method
    input_1: float = 0
    input_2: float = 0
    output_1: float | None = None
    force_failure: bool = False

    # attribute used by ``generate_random_logs_with_cleanup`` method
    logfile: EntityHandle = NO_ENTITY

    # attribute used to store the selected folder on the "FolderSelector" page
    selected_folder: str | None = None

    # attributes used to store values on the "InputForm" page
    sim_job_name: str | None = None
    sim_job_solver: str = "Fluent"
    sim_job_output_fields: list[str] = ["Velocity", "Pressure"]
    sim_job_mesh_resolution_x: float = 0.05
    sim_job_mesh_resolution_y: float = 0.05
    sim_job_max_runtime: float = 4
    sim_job_save_checkpoints: bool = True
    sim_job_email_notification: bool = False
    sim_job_cpu_allocation: float = 50
    sim_job_hpc_token: str | None = None

    # tree selected item
    selected_tree_item: str | None = None

    @transaction(
        self=StepSpec(
            upload=["output_1"],
            download=["input_1", "input_2", "force_failure"],
        ),
    )
    def compute_sum(self) -> None:
        """Compute the sum of two numbers."""
        self.output_1 = None  # reset output before starting computation
        self.transaction.upload(
            ["output_1"]
        )  # upload reset output to notify clients that computation has started
        time.sleep(10)
        if self.force_failure:
            raise Exception("Forced failure.")
        self.output_1 = self.input_1 + self.input_2

    @transaction(self=StepSpec(), enable_termination_event=True)
    @long_running
    def long_running_1(self) -> None:
        """Simulate a long-running method by sleeping for 5 seconds."""
        time.sleep(5)

    @transaction(self=StepSpec(), enable_termination_event=True)
    @long_running
    def long_running_2(self) -> None:
        """Simulate a long-running method by sleeping for 5 seconds."""
        time.sleep(5)

    @transaction(self=StepSpec(), enable_termination_event=True)
    @long_running
    def long_running_3(self) -> None:
        """Simulate a long-running method by sleeping for 5 seconds."""
        time.sleep(5)

    @transaction(self=StepSpec(upload=["logfile"]), enable_termination_event=True)
    @long_running
    def generate_random_logs_with_cleanup(self) -> None:
        """Generate random log messages, upload the log file, and clean up outdated entity handles.

        Emits random log messages at the DEBUG, INFO, WARNING, ERROR, and CRITICAL levels for
        30 seconds. After each message the current log file content is stored as a new
        EntityHandle and uploaded so that listening clients can display the latest entries.
        EntityHandle files that are no longer needed are explicitly deletedonce their expiry time
        has elapsed, preventing unbounded storage growth while the long-running transaction is
        active.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        logfiles_pending_deletion: list[ExpiringEntityHandle] = []

        # Create a temporary file used by the logger. Its contents will be copied
        # into immutable EntityHandle files for upload.
        dynamic_log_file = self.storage_scope.get_storage_root() / "dynamic_log.log"
        dynamic_log_file.write_text("starting log file\n")

        # File handler that writes to the dynamic log file.
        file_handler = logging.FileHandler(str(dynamic_log_file))

        # Log message format.
        formatter = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
        file_handler.setFormatter(logging.Formatter(formatter))

        # Attach the handler to the logger.
        logger.addHandler(file_handler)

        start_time = time.time()

        while (time.time() - start_time) < 30:
            # Emit a random log message.
            index = randrange(5)
            if index == 0:
                logger.info("This is an info message.")
            elif index == 1:
                logger.warning("This is a warning message.")
            elif index == 2:
                logger.error("This is an error message.")
            elif index == 3:
                logger.critical("This is a critical message.")
            elif index == 4:
                logger.debug("This is a debug message.")

            # Save the previously uploaded logfile handle so it can be deleted later.
            self._store_logfile_entity_handle_as_outdated(self.logfile, logfiles_pending_deletion)

            # Copy the current dynamic log file into a new file and store it
            # as a fresh EntityHandle. Files stored as EntityHandle are immutable,
            # so we create a new file each iteration.
            self.logfile = self._store_dynamic_log_file_content_in_fresh_entity_handle(
                dynamic_log_file
            )

            # Upload the new logfile handle so clients can access the updated log.
            self.transaction.upload(["logfile"])

            # Remove any expired uploaded log files to free storage. While this long-running
            # transaction is active, old files are not automatically garbage-collected, so
            # we manage their lifecycle explicitly here.
            self._cleanup_expired_logfiles(logfiles_pending_deletion)

            time.sleep(0.5)

        logger.removeHandler(file_handler)
        file_handler.close()

    def _store_logfile_entity_handle_as_outdated(
        self,
        old_logfile_handle: EntityHandle,
        logfiles_pending_deletion: list[ExpiringEntityHandle],
    ) -> None:
        """Store current logfile entity handle in the outdated logfiles list for later deletion."""
        if old_logfile_handle != NO_ENTITY:
            timed_old_handle = ExpiringEntityHandle(
                expiry_time=time.time() + self.EXPIRY_TIME_SECONDS,
                entity_handle=old_logfile_handle,
            )
            logfiles_pending_deletion.append(timed_old_handle)

    def _store_dynamic_log_file_content_in_fresh_entity_handle(
        self, dynamic_log_file: Path
    ) -> EntityHandle:
        """Store the current content of the dynamic log file in a new entity handle."""
        bytes_content = dynamic_log_file.read_bytes()
        return self.storage_scope.store_stream(bytes_content)

    def _cleanup_expired_logfiles(
        self, logfiles_pending_deletion: list[ExpiringEntityHandle]
    ) -> None:
        """Cleanup expired log files."""
        current_time = time.time()
        for logfile in list(logfiles_pending_deletion):
            if current_time >= logfile.expiry_time:
                # file has expired and can be deleted
                logfiles_pending_deletion.remove(logfile)
                with contextlib.suppress(Exception):
                    self.storage_scope.destroy(logfile.entity_handle)
