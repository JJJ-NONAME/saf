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

from enum import StrEnum


class FieldState(StrEnum):
    """Indicates the state of a given field in a given project.
    Notes
    -----
    :ref:`This section of the user guide <saf-docs:field_states>` explains the field state concept in more
    detail.
    """

    UPTODATE = "UPTODATE"
    """Indicates that the current value of the given field is correct
    (consistent with the values of fields of which it is
    directly and indirectly dependent)."""

    OUTOFDATE = "OUTOFDATE"
    """Indicates that the current value of the given field is
    potentially incorrect (inconsistent with the values of
    fields of which it is directly and indirectly dependent)."""

    def __eq__(self, other: object) -> bool:
        return str(self.value) == other

    def __hash__(self) -> int:
        return hash(str(self.value))
