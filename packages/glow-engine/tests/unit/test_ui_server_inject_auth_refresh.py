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

# ©2026, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Unit tests for authentication script injection in server.py.

This module tests the _inject_auth_refresh_script function that injects
GLOW's authentication refresh JavaScript into Dash applications.

"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from ansys.saf.glow._config.const import AUTH_SCRIPT_MARKER
from ansys.saf.glow._ui.server import (
    GLOW_ASSETS_PATH,
    _inject_auth_refresh_script,  # pyright: ignore[reportPrivateUsage]
)
from tests.mocks.mock_ui import MockUI


@pytest.fixture
def mock_ui_app():
    """Create a mock Dash app using MockUI."""
    return MockUI()


@pytest.fixture
def sample_js_content():
    """Sample JavaScript content for testing.

    Returns
    -------
    str
        Sample JavaScript code representing an auth refresh handler.
    """
    return """
(function() {
    console.log('GLOW Auth Refresh Handler');
    // Authentication refresh logic here
    setInterval(function() {
        fetch('/api/auth/refresh').then(function(response) {
            return response.json();
        });
    }, 300000);
})();
"""


@pytest.fixture
def mock_logger(mocker: MockerFixture):
    return mocker.patch("ansys.saf.glow._ui.server.logger")


def test_inject_script_success(
    mock_ui_app: Mock,
    sample_js_content: str,
    mocker: MockerFixture,
    mock_logger: Mock,
):
    """Test successful injection of auth refresh script."""
    mocker.patch.object(Path, "read_text", return_value=sample_js_content)

    _inject_auth_refresh_script(mock_ui_app)

    # Verify script appears before closing body tag
    assert all(
        fragment in mock_ui_app.index_string
        for fragment in [
            "<script>",
            f"{AUTH_SCRIPT_MARKER}",
            sample_js_content.strip(),
            "</script>",
        ]
    )
    # Verify Dash placeholders are preserved
    dash_placeholders = [
        "{%metas%}",
        "{%title%}",
        "{%css%}",
        "{%app_entry%}",
        "{%config%}",
        "{%scripts%}",
        "{%renderer%}",
    ]

    assert all(marker in mock_ui_app.index_string for marker in dash_placeholders)

    mock_logger.info.assert_called_once_with("Auth refresh script injected successfully")


def test_inject_script_file_not_found(
    mock_ui_app: Mock,
    mocker: MockerFixture,
):
    """Test behavior when auth refresh JavaScript file cannot be read.

    Verifies that a RuntimeError is raised when the JavaScript file
    does not exist or cannot be accessed.
    """
    original_index = mock_ui_app.index_string

    mocker.patch.object(Path, "read_text", side_effect=OSError("File not found"))

    with pytest.raises(RuntimeError, match="Failed to load auth refresh script"):
        _inject_auth_refresh_script(mock_ui_app)

    # Verify index_string is unchanged
    assert mock_ui_app.index_string == original_index


def test_inject_script_multiple_injections(
    mock_ui_app: Mock,
    sample_js_content: str,
    mocker: MockerFixture,
):
    """Test that the auth refresh script is not injected multiple times.

    Verifies that calling the function multiple times results in only
    one script being present in the index_string.
    """
    mocker.patch.object(Path, "read_text", return_value=sample_js_content)

    # First injection
    _inject_auth_refresh_script(mock_ui_app)
    first_result = mock_ui_app.index_string

    assert "<script>" in first_result
    assert sample_js_content.strip() in first_result

    # Verify only one script marker exists
    assert first_result.count("// GLOW Authentication Refresh Handler") == 1

    # Second injection should be skipped
    _inject_auth_refresh_script(mock_ui_app)
    second_result = mock_ui_app.index_string

    # Verify script count is still one
    assert second_result.count("// GLOW Authentication Refresh Handler") == 1

    # Verify HTML structure is still valid
    assert second_result.strip().endswith("</body>\n</html>")

    # Ensure script appears before closing body tag
    last_body_index = second_result.rfind("</body>")
    scripts_section = second_result[:last_body_index]
    assert scripts_section.count("<script>") == 1


def test_inject_script_no_body_tag(
    mock_ui_app: Mock,
    sample_js_content: str,
    mocker: MockerFixture,
    mock_logger: Mock,
):
    """Test behavior when index_string has no </body> tag.

    Verifies that a warning is logged when the closing body tag is missing,
    and the script cannot be injected.

    """
    # Create app without </body> tag
    mock_ui_app.index_string = "<html><head></head><div>content</div></html>"
    mocker.patch.object(Path, "is_file", return_value=True)
    mocker.patch.object(Path, "read_text", return_value=sample_js_content)

    _inject_auth_refresh_script(mock_ui_app)

    # Verify warning is logged
    mock_logger.warning.assert_called_once_with(
        "Unable to inject auth refresh script: </body> not found in index_string",
    )

    # Verify script was not added
    assert "<script>" not in mock_ui_app.index_string


def test_assets_path_constant(mock_ui_app: Mock):
    """Test that the assets path correctly resolves the auth refresh script.

    Verifies that _inject_auth_refresh_script can read the JavaScript
    file from the assets directory without mocking filesystem access.
    """
    assert isinstance(GLOW_ASSETS_PATH, Path)
    assert GLOW_ASSETS_PATH.name == "assets"
    assert "_ui" in str(GLOW_ASSETS_PATH)

    _inject_auth_refresh_script(mock_ui_app)
    assert "// GLOW Authentication Refresh Handler" in mock_ui_app.index_string
    assert "<script>" in mock_ui_app.index_string
