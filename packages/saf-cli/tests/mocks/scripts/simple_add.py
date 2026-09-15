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

"""Simple addition function for HPS job execution."""


def simple_add(a: float, b: float) -> dict[str, float]:
    """Add two floats and return the result as a dictionary.

    Args:
        a: First float to add.
        b: Second float to add.

    Returns:
        Dictionary containing the sum result.
    """
    return {"result": a + b}
