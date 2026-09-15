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

from ansys.saf.testing._pytest.platform_specific import (
    ADDRESS_IN_USE,
    CONNECTION_ERROR,
    is_ci_run,
    linux_only,
    skip_for_ci,
    skip_for_ci_on_linux,
    skip_for_ci_on_windows,
    windows_only,
    xfail_for_ci,
    xfail_for_ci_on_linux,
    xfail_for_ci_on_windows,
)

__all__ = [
    "ADDRESS_IN_USE",
    "CONNECTION_ERROR",
    "is_ci_run",
    "windows_only",
    "linux_only",
    "skip_for_ci",
    "skip_for_ci_on_windows",
    "skip_for_ci_on_linux",
    "xfail_for_ci",
    "xfail_for_ci_on_linux",
    "xfail_for_ci_on_windows",
]
