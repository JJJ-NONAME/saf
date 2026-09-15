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

import subprocess
from typing import Any


def run_and_capture_output(args: list[Any], **kwargs: Any):
    """
    Convenience function to execute an application in a new process,
    log its stdout/stderr and wait until the process completes.

    Parameters
    ----------

    args
        See args in subprocess.Popen

    **kwargs
        Allows you to pass keyword arguments to subprocess.Popen,
        except for stdout and stderr which are overridden as

        * stdout = subprocess.PIPE
        * stderr = subprocess.STDOUT

    """

    kwargs["stdout"] = subprocess.PIPE
    kwargs["stderr"] = subprocess.STDOUT

    print(f"Executing: {args}")
    print("-" * 90)
    with subprocess.Popen(args, **kwargs) as proc:
        if proc.stdout is not None:
            for line in proc.stdout:
                msg = line.decode("utf-8").rstrip()  # type: ignore
                print(msg)  # type: ignore
    print("-" * 90)

    if proc.returncode == 0:
        print("The application completed successfully.")
    else:
        print(f"The application exited with code {proc.returncode}.")
        raise Exception(f"The application exited with code {proc.returncode}")
