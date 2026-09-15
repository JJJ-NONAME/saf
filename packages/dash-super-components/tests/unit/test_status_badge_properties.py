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

"""Unit tests for status badge properties module."""

from ansys.solutions.dash_super_components.utils.status_badge_properties import (
    TRANSACTION_STATUS_BADGE_PROPERTIES,
)


def test_status_badge_properties_all_entries_are_dicts():
    """Test that all entries in STATUS_BADGE_PROPERTIES are dictionaries."""
    for key, value in TRANSACTION_STATUS_BADGE_PROPERTIES.items():
        assert isinstance(value, dict), f"Value for '{key}' is not a dict: {value}"


def test_status_badge_properties_all_entries_have_color_key():
    """Test that all entries in STATUS_BADGE_PROPERTIES contain the 'color' key."""
    for key, value in TRANSACTION_STATUS_BADGE_PROPERTIES.items():
        assert "color" in value, f"'color' key missing for '{key}'"


def test_status_badge_properties_color_values_are_str():
    """Test that all 'color' values are strings."""
    for key, value in TRANSACTION_STATUS_BADGE_PROPERTIES.items():
        color = value.get("color")
        assert isinstance(color, str), f"Color for '{key}' is not a string: {color}"


def test_status_badge_properties_no_empty_color_values():
    """Test that no 'color' value is an empty string."""
    for key, value in TRANSACTION_STATUS_BADGE_PROPERTIES.items():
        color = value.get("color")
        assert color != "", f"Color for '{key}' is empty string"
