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

from collections.abc import Generator
import importlib.util
import subprocess
import sys

from asgi_lifespan import LifespanManager
from httpx2 import ASGITransport, AsyncClient
import pytest

from ansys.saf.glow._config.settings import Settings
from tests.mocks.solutions import minimal_solution
from tests.unit.conftest import MOCK_APP_STARTUP_TIMEOUT, build_mock_app

solution = minimal_solution


OPTIONAL_PIMS_DEPS = [
    "ansys.platform.instancemanagement",
    "ansys.hps.client",
]

OPTIONAL_DASH_DEPS = [
    "dash",
    "dash_extensions",
    "flask",
]
GLOW_CLIENT_MODULES = [
    "ansys.saf.glow.client",
    "ansys.saf.glow._client",
]

OPTIONAL_MCP_DEPS = [
    "fastmcp",
    "mcp",
]
GLOW_API_MODULES = [
    "ansys.saf.glow.api",
]


@pytest.fixture
def remove_from_sys_modules(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    sys_modules_backup = sys.modules.copy()
    optional_deps = request.param

    for loaded_module in list(sys.modules.keys()):
        if loaded_module.startswith(tuple(optional_deps)):
            del sys.modules[loaded_module]

    yield

    sys.modules = sys_modules_backup


@pytest.mark.parametrize("remove_from_sys_modules", [OPTIONAL_PIMS_DEPS], indirect=True)
@pytest.mark.usefixtures("remove_from_sys_modules")
async def test_solution_doesnt_import_optional_pims_dependencies(settings: Settings):
    """Test that optional Product Instance Management System (PIMS) dependencies
    aren't imported if they are not used.
    """
    # GIVEN: app that runs a minimal solution without PIMS
    app = build_mock_app(settings, solution)
    # WHEN: starting the app and running some API calls
    async with (
        LifespanManager(app, startup_timeout=MOCK_APP_STARTUP_TIMEOUT) as manager,
        AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://test",
            follow_redirects=True,
        ) as async_client,
    ):
        # THEN: the app is working (TODO: launch a couple of sync and longrunning transactions)
        response = await async_client.post("/projects", json={"display_name": "my_project"})
        response.raise_for_status()
        project_name = response.json()["name"]
        response = await async_client.get("/projects")
        response.raise_for_status()
        assert any(project["name"] == project_name for project in response.json()["projects"])
        response = await async_client.patch(f"{project_name}/steps/minimal-step/", json={"x": 100})
        response.raise_for_status()
        response = await async_client.delete(project_name)
        response.raise_for_status()
        # THEN: optional PIMS dependencies have not been imported
        for loaded_module in sys.modules:
            assert not loaded_module.startswith(tuple(OPTIONAL_PIMS_DEPS))


@pytest.mark.parametrize("remove_from_sys_modules", [OPTIONAL_DASH_DEPS + GLOW_CLIENT_MODULES], indirect=True)
@pytest.mark.usefixtures("remove_from_sys_modules")
def test_client_imports_without_optional_dash_dependencies():
    """Test that client module can be imported without UI optional dependencies."""
    for loaded_module in sorted(sys.modules):
        assert not loaded_module.startswith(tuple(GLOW_CLIENT_MODULES))

    import ansys.saf.glow.client  # pyright: ignore[reportUnusedImport]  # noqa: F401

    for loaded_module in sorted(sys.modules):
        assert not loaded_module.startswith(tuple(OPTIONAL_DASH_DEPS))


def test_testing_import_when_testing_deps_available() -> None:
    # Arrange: Ensure pytest and pytest-mock are available
    assert importlib.util.find_spec("pytest")
    assert importlib.util.find_spec("pytest_mock")
    assert importlib.util.find_spec("httpx2")

    # Act: Import the testing module
    import ansys.saf.glow.testing as testing_module

    # Assert: __all__ contains fixtures
    assert len(testing_module.__all__) > 0
    assert "configure_solution" in testing_module.__all__
    assert "client_project" in testing_module.__all__
    assert "solution_logs" in testing_module.__all__


@pytest.mark.parametrize("missing_dep", ["pytest", "pytest_mock", "httpx2"])
def test_testing_import_when_testing_deps_unavailable(missing_dep: str) -> None:
    # Ended up with a subprocess to isolate it. Couldn't make it work alongside the rest of tests.
    script = f"""
import sys
from typing import Any

# Install import hook to block pytest and pytest_mock
original_import = __builtins__.__import__
def mock_import(name: str, *args: Any, **kwargs: Any):
    if name.startswith("{missing_dep}",):
        raise ImportError()
    return original_import(name, *args, **kwargs)
__builtins__.__import__ = mock_import

# Import the testing module
import ansys.saf.glow.testing as testing_module

# Print __all__ for verification
print(testing_module.__all__)
"""

    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.strip() == "[]"


@pytest.mark.parametrize("remove_from_sys_modules", [OPTIONAL_MCP_DEPS + GLOW_API_MODULES], indirect=True)
@pytest.mark.usefixtures("remove_from_sys_modules")
def test_solution_api_when_mcp_disabled(monkeypatch: pytest.MonkeyPatch):
    """Test that the FastAPI app can be imported without MCP optional dependencies."""
    monkeypatch.setenv("GLOW_SOLUTION_DEFINITION", "tests.mocks.solutions.minimal_solution")
    monkeypatch.setenv("GLOW_MCP_DISABLED", "True")

    for loaded_module in sorted(sys.modules):
        assert not loaded_module.startswith(tuple(GLOW_API_MODULES))

    from ansys.saf.glow.api import app  # pyright: ignore[reportUnusedImport]  # noqa: F401

    for loaded_module in sorted(sys.modules):
        assert not loaded_module.startswith(tuple(OPTIONAL_MCP_DEPS))


@pytest.mark.parametrize("missing_dep", ["fastmcp", "mcp"])
def test_solution_api_when_mcp_deps_unavailable(missing_dep: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the FastAPI app can be imported without MCP optional dependencies even if MCP is enabled."""
    monkeypatch.setenv("GLOW_SOLUTION_DEFINITION", "tests.mocks.solutions.minimal_solution")
    monkeypatch.setenv("GLOW_MCP_DISABLED", "False")

    script = f"""
import logging
import sys
from typing import Any

logging.basicConfig(level=logging.WARNING)

# Install import hook to block fastmcp and mcp
original_import = __builtins__.__import__
def mock_import(name: str, *args: Any, **kwargs: Any):
    if name.startswith("{missing_dep}",):
        raise ImportError()
    return original_import(name, *args, **kwargs)
__builtins__.__import__ = mock_import

# Import the Solution API module
from ansys.saf.glow.api import app

print(type(app).__name__)
"""

    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.strip() == "FastAPI"
    assert "MCP not mounted: missing dependencies: fastmcp, mcp" in result.stderr
