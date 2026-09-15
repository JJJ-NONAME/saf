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

from collections.abc import Callable
from pathlib import Path
import random

import pytest


@pytest.fixture
def get_temp_sqlite_database(tmp_path: Path) -> Callable[[], Path]:
    def _get_temp_sqlite_database() -> Path:
        # stem of db file is used as table name, doesn't accept all characters
        return tmp_path / f"saf_testing_{str(random.randint(0, 100000)).zfill(6)}.db"

    return _get_temp_sqlite_database
