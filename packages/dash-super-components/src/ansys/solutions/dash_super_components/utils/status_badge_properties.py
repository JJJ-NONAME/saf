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


"""Shared transaction status badge color mappings."""

from ansys.solutions.dash_super_components.utils._common_colors import _CommonColors as CommonColors

TRANSACTION_STATUS_BADGE_PROPERTIES = {
    "run-required": {
        "color": CommonColors.MANTINE_GRAY,
    },
    "running": {
        "color": CommonColors.MANTINE_BLUE,
    },
    "completed": {
        "color": CommonColors.MANTINE_LIME,
    },
    "failed": {
        "color": CommonColors.MANTINE_RED,
    },
}
