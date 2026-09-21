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


class SameDisplayNameProjectException(Exception):  # noqa: N818
    """Exception raised when the :ref:`GLOW client API <glow-api-client-index>` gives multiple projects
    with the same display name."""

    exit_code = 4


class CantCreateProjectError(Exception):
    """Exception raised when the :ref:`GLOW client API <glow-api-client-index>` doesn't allow creation of
    a project."""

    exit_code = 5
