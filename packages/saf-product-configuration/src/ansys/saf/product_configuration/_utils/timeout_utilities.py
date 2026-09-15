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

import os


def get_timeout_from_environment(environment_variable: str, default_timeout: int) -> int:
    """Return a positive timeout value configured in an environment variable."""
    configured_timeout = os.getenv(environment_variable)
    if configured_timeout is None:
        return default_timeout

    try:
        timeout = int(configured_timeout)
    except ValueError as error:
        raise ValueError(f"{environment_variable} must be a positive integer.") from error

    if timeout <= 0:
        raise ValueError(f"{environment_variable} must be a positive integer.")

    return timeout
