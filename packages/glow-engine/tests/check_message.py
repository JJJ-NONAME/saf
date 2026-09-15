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

MATCH_ANYTHING = ">>>MATCH_ANYTHING<<<"


def check_message(expected: list[str], actual_string: str):
    """
    Check that the actual error message starts with the expected lines.
    Raise assert exceptions when lines do not match or if the actual
    number of lines is less than the number of expected lines.

    Parameters
    ==========
    expected: list[str]
        The expected lines at the start of actual_string.
        Entries that are equal to MATCH_ANYTHING will match with any line content.
    actual_string: str
        The actual error message string to be checked.
    """
    actual = [x.strip() for x in actual_string.splitlines()]

    assert len(expected) <= len(actual), (
        "Actual message has less lines than expected.\nExpected:\n"
        + "\n".join(expected)
        + "\nActual:\n"
        + "\n".join(actual)
    )

    expected_for_compare: list[str] = []
    actual_for_compare: list[str] = []
    for e, a in zip(expected, actual, strict=False):
        if e != MATCH_ANYTHING:
            expected_for_compare.append(e)
            actual_for_compare.append(a)
    assert expected_for_compare == actual_for_compare
