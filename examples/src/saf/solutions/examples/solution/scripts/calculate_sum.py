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

# ©2026, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Module containing function that is executed on HPS by the hps_job_submission_step."""

import json
from pathlib import Path


def calculate_sum(
    first_arg: float,  # arg passed directly
    second_arg: float,  # arg passed directly
    persisted_input_file: Path,  # args passed as file which a copy of a file referenced by an EntityHandle
    persisted_input_directory: Path,  # args passed as file inside a directory which is a copy of a referenced directory
    transient_input_file: Path,  # args passed as file which a copy of a file referenced by a Path
    transient_input_redirected_file: Path,  # args passed as file inside a renamed directory
    transient_input_directory: Path,  # args passed as file inside a directory which is a copy of a directory
):
    """Calculate the sum of two arguments, demonstrating various input and output mechanisms."""
    result = first_arg + second_arg

    input_content = {
        "first_arg": first_arg,
        "second_arg": second_arg,
    }
    input_content_str = json.dumps(input_content)

    # check that the various inputs have the expected values
    assert input_content_str == persisted_input_file.read_text()
    assert input_content_str == (persisted_input_directory / "inputs.json").read_text()
    assert input_content_str == transient_input_file.read_text()
    assert input_content_str == transient_input_redirected_file.read_text()
    assert input_content_str == (transient_input_directory / "inputs.json").read_text()

    # check that the redirected file has the correct name
    assert "redirected_input.json" == transient_input_redirected_file.name

    # generate output files
    output_content_str = json.dumps(result)

    # write output to location specified in the HpsOutputFileSpecification evaluation_path
    Path("output_for_redirection.json").write_text(output_content_str)

    # write output directory named according to the outputs dictionary key
    # because HpsOutputFileSpecification not present
    output_directory_path = Path("output_directory")
    output_directory_path.mkdir()
    (output_directory_path / "nested_output.json").write_text(output_content_str)

    # output dictionary contains data that is not contained in output files or directories
    # using the same key as that used in the output dictionary
    return {"result": result}
