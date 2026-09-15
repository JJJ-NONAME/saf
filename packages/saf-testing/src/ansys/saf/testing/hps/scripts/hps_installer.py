# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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

from ansys.saf.testing._hps.scripts.hps_installer import HPS_DEPLOYMENTS_DIRECTORY, HPS_SCALING_CONFIG_FILE, cli

__all__ = [
    "cli",
    "HPS_DEPLOYMENTS_DIRECTORY",
    "HPS_SCALING_CONFIG_FILE",
]

# Add this block to enable CLI execution with -m
if __name__ == "__main__":
    cli()
