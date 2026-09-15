# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Common colors used internally by the Super Components for Dash library."""

from enum import StrEnum


class _CommonColors(StrEnum):
    """Internal enum containing common color specifiers used by this package."""

    MANTINE_TEXT = "var(--mantine-color-text)"
    MANTINE_DIMMED = "var(--mantine-color-dimmed)"
    MANTINE_PLACEHOLDER = "var(--mantine-color-placeholder)"
    MANTINE_BODY = "var(--mantine-color-body)"
    MANTINE_ERROR = "var(--mantine-color-error)"
    MANTINE_PRIMARY_COLOR = "var(--mantine-primary-color-filled)"

    MANTINE_GRAY = "var(--mantine-color-gray-6)"
    MANTINE_LIME = "var(--mantine-color-lime-6)"
    MANTINE_RED = "var(--mantine-color-red-6)"
    MANTINE_PINK = "var(--mantine-color-pink-6)"
    MANTINE_ORANGE = "var(--mantine-color-orange-6)"
    MANTINE_BLUE = "var(--mantine-color-blue-6)"
    MANTINE_GRAPE = "var(--mantine-color-grape-6)"
