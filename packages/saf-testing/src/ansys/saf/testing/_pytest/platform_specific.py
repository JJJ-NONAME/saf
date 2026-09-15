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

import os
import platform

import pytest

CONNECTION_ERROR: str = (
    "[Errno 111] Connection refused"
    if platform.system() == "Linux"
    else "[WinError 10061] No connection could be made because the target machine actively refused it"
)

ADDRESS_IN_USE: str = (
    "address already in use" if platform.system() == "Linux" else "only one usage of each socket address"
)

# ================================================= [System functions] ============================================= #


def is_ci_run() -> bool:
    return str(os.getenv("RUNNER_ENVIRONMENT", "None")) != "None"


# ================================================= [Decorators] ============================================= #


def windows_only(reason: str = "Windows only."):
    return pytest.mark.skipif(platform.system() != "Windows", reason=reason)


def linux_only(reason: str = "Linux only."):
    return pytest.mark.skipif(platform.system() != "Linux", reason=reason)


def skip_for_ci(reason: str = "Skip on the CI."):
    return pytest.mark.skipif(is_ci_run(), reason=reason)


def skip_for_ci_on_windows(reason: str = "Linux only on the CI."):
    return pytest.mark.skipif(platform.system() == "Windows" and is_ci_run(), reason=reason)


def skip_for_ci_on_linux(reason: str = "Windows only on the CI."):
    return pytest.mark.skipif(platform.system() == "Linux" and is_ci_run(), reason=reason)


def xfail_for_ci(reason: str = "Expected to fail on the CI."):
    return pytest.mark.xfail(is_ci_run(), reason=reason)


def xfail_for_ci_on_linux(reason: str = "Expected to fail on Linux on the CI."):
    return pytest.mark.xfail(condition=platform.system() == "Linux" and is_ci_run(), reason=reason)


def xfail_for_ci_on_windows(reason: str = "Expected to fail on Windows on the CI."):
    return pytest.mark.xfail(condition=platform.system() == "Windows" and is_ci_run(), reason=reason)
