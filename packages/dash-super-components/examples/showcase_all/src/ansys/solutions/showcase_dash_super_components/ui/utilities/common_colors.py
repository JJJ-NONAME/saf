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


"""Common colors for the application."""

from enum import StrEnum


class CommonColors(StrEnum):
    """Enum containing common color specifiers used in the application."""

    MANTINE_TEXT = "var(--mantine-color-text)"
    MANTINE_BODY = "var(--mantine-color-body)"
    MANTINE_DIMMED = "var(--mantine-color-dimmed)"
    MANTINE_PRIMARY_COLOR = "var(--mantine-primary-color-filled)"

    WHITE = "var(--mantine-color-white)"
    BLACK = "var(--mantine-color-black)"
    VERY_LIGHT_GREY = "var(--mantine-color-gray-0)"
    LIGHT_GREY = "var(--mantine-color-gray-2)"
    MEDIUM_GREY = "var(--mantine-color-gray-5)"
    DARK_GREY = "var(--mantine-color-gray-7)"
    VERY_DARK_GREY = "var(--mantine-color-gray-9)"
    YELLOW = "var(--mantine-color-yellow-4)"
    VERY_LIGHT_YELLOW = "var(--mantine-color-yellow-1)"
    ORANGE = "var(--mantine-color-orange-5)"
    LIGHT_ORANGE = "var(--mantine-color-orange-3)"
    RED = "var(--mantine-color-red-6)"
    LIGHT_RED = "var(--mantine-color-red-4)"
    BLUE = "var(--mantine-color-blue-6)"
    GREEN = "var(--mantine-color-green-6)"
    VERY_LIGHT_GREEN = "var(--mantine-color-green-1)"
