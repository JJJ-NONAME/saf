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
from random import randrange
import time

from ansys.saf.glow.solution import (
    NO_ENTITY,
    EntityHandle,
    StepModel,
    StepSpec,
    long_running,
    transaction,
)

"""Backend of my_step."""


class MyStep(StepModel):
    """Step definition of my_step."""

    logfile: EntityHandle = NO_ENTITY

    # attributes used to store values on the "InputForm" example
    project_name: str = ""
    max_iterations: int = 100

    @transaction(self=StepSpec())
    @long_running
    def my_method(self) -> None:
        """Simulate a long-running method by sleeping for 5 seconds."""
        time.sleep(5)

    @transaction(self=StepSpec())
    @long_running
    def my_method_2(self) -> None:
        """Simulate a long-running method by sleeping for 5 seconds."""
        time.sleep(5)

    @transaction(self=StepSpec())
    def my_method_synchronous(self) -> None:
        """Simulate a synchronous method by sleeping for 5 seconds."""
        time.sleep(5)

    @transaction(self=StepSpec())
    def my_method_synchronous_2(self) -> None:
        """Simulate a synchronous method by sleeping for 5 seconds."""
        time.sleep(5)

    # [generate-logs-start]
    @transaction(self=StepSpec(upload=["logfile"]))
    @long_running
    def generate_random_logs(self) -> None:
        """Generate random log messages and periodically upload the log file as an EntityHandle.

        Emits random log messages at the DEBUG, INFO, WARNING, ERROR, and CRITICAL levels for
        30 seconds. After each message the current log file content is stored as a new
        EntityHandle and uploaded so that listening clients can display the latest entries.
        Old EntityHandle files are not explicitly removed here; they are garbage-collected
        automatically once the transaction completes.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Create a temporary file used by the logger. Its contents will be copied
        # into immutable EntityHandle files for upload.
        dynamic_log_file = self.storage_scope.get_storage_root() / "dynamic_log.log"

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

            # Copy the current dynamic log file into a new file and store it
            # as a fresh EntityHandle. Files stored as EntityHandle are immutable,
            # so we create a new file each iteration.
            bytes_content = dynamic_log_file.read_bytes()
            self.logfile = self.storage_scope.store_stream(bytes_content)

            # Upload the new logfile handle so clients can access the updated log.
            self.transaction.upload(["logfile"])

            time.sleep(0.5)

        logger.removeHandler(file_handler)
        file_handler.close()

    # [generate-logs-end]
