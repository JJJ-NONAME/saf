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

"""Module containing function that is executed on HPS by the hps_job_submission_step."""

from pathlib import Path


def calculate_sum(
    first_arg: float,  # arg passed directly
    second_arg: float,  # arg passed directly
):
    """Calculate the sum of two arguments, demonstrating various input and output mechanisms."""
    result = first_arg + second_arg

    with open("logs.txt", "a") as log_file:
        log_file.write(f"Calculation performed with first_arg={first_arg} and second_arg={second_arg}\n")

    # generate output files
    output_content_str = f"result({first_arg}, {second_arg}) = {result}"

    # write output to location specified in the HpsOutputFileSpecification evaluation_path
    Path("output.txt").write_text(output_content_str)

    with open("logs.txt", "a") as log_file:
        log_file.write(f"Calculation done, result={result}\n")

    return {"result": result}
