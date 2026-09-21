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

from ansys.saf.glow.runtime._solution_entry_point import glow_main

# This file is used for executing the CLI through the solution module.
# Example: python -m ansys.solutions.my_solution.main api or my_solution_exec api,
# where my_solution_exec is an script defined in the solution's pyproject.toml that
# points to ansys.solutions.my_solution.main:main

__all__ = ["glow_main"]
