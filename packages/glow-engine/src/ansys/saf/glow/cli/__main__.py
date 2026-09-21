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

from ansys.saf.glow.cli._cli_entry_point import SolutionModule, cli

# This file is used for executing the CLI through the glow_engine module.
# Example: python -m ansys.saf.glow.cli api or glow_engine api
# where glow_engine is an script defined in the pyproject.toml that
# points to ansys.saf.glow.cli.__main__:entry_point


def entry_point():
    cli(obj=SolutionModule())


if __name__ == "__main__":
    entry_point()
