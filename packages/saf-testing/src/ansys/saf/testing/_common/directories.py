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
from pathlib import Path

import pytest

from ansys.saf.testing._common.common import YieldFixture


@pytest.fixture
def mock_appdata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    appdata = tmp_path / "appdata"
    appdata.mkdir(exist_ok=True, parents=True)
    monkeypatch.setenv("APPDATA", str(appdata))
    monkeypatch.setenv("XDG_DATA_HOME", str(appdata))
    return appdata


@pytest.fixture(scope="module")
def mock_module_appdata(tmp_path_factory: pytest.TempPathFactory, monkeysession: pytest.MonkeyPatch) -> Path:
    appdata = tmp_path_factory.mktemp("appdata")
    monkeysession.setenv("APPDATA", str(appdata))
    monkeysession.setenv("XDG_DATA_HOME", str(appdata))
    return appdata


@pytest.fixture(scope="session")
def mock_session_appdata(tmp_path_factory: pytest.TempPathFactory, monkeysession: pytest.MonkeyPatch) -> Path:
    appdata = tmp_path_factory.mktemp("appdata")
    monkeysession.setenv("APPDATA", str(appdata))
    monkeysession.setenv("XDG_DATA_HOME", str(appdata))
    return appdata


@pytest.fixture
def tmp_path_as_working_dir(tmp_path: Path, request: pytest.FixtureRequest) -> YieldFixture[Path]:
    new_cwd = tmp_path if not hasattr(request, "param") else tmp_path / request.param
    new_cwd.mkdir(exist_ok=True, parents=True)
    original_path = Path.cwd()
    os.chdir(new_cwd)
    yield new_cwd
    os.chdir(original_path)
