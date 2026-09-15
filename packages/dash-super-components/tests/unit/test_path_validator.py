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


"""Unit tests for path validator module."""

import math
from pathlib import Path
from unittest import mock
import uuid

from ansys.solutions.dash_super_components.utils.path_validator import (
    PathDoesNotExistError,
    PathIsTooLongError,
    PathValidator,
)


def test_max_path_length_windows():
    """Test max path length on Windows platform."""
    # Simulate Windows platform
    with mock.patch("platform.system", return_value="Windows"):
        max_length = PathValidator.max_path_length()
        assert max_length == 250


def test_max_path_length_unix():
    """Test max path length on Unix platform."""

    # Simulate Unix platform
    def mock_os_pathconf(path: str, name: str) -> int:  # Correct signature with type hints
        if name == "PC_PATH_MAX":
            return 4096
        raise ValueError("Unknown pathconf name")

    # Use create=True to allow patching os.pathconf on Windows where it doesn't exist
    with (
        mock.patch("platform.system", return_value="Linux"),
        mock.patch("os.pathconf", side_effect=mock_os_pathconf, create=True),
    ):
        max_length = PathValidator.max_path_length()
        assert max_length == 4096


def test_validate_path_ok_defaults():
    """Test path validation with default settings."""
    cwd = str(Path.cwd())
    # Ensure the input path is within default max length
    assert len(cwd) <= 250

    validator = PathValidator(cwd)
    res = validator.validate()
    assert isinstance(res, Path)


def test_validate_path_ok_custom_max_length():
    """Test path validation with custom max length."""
    cwd = str(Path.cwd())
    custom_max_length = len(cwd) + 10  # Ensure cwd is within custom max length

    validator = PathValidator(cwd)
    res = validator.validate(max_path_length=custom_max_length)
    assert isinstance(res, Path)


def test_validate_too_long_path_defaults():
    """Test validation of path that exceeds default max length."""
    folder_name = "/long_string"
    n_times = math.ceil(PathValidator.max_path_length() / len(folder_name))

    validator = PathValidator(folder_name * n_times)
    res = validator.validate()
    assert isinstance(res, PathIsTooLongError)


def test_too_long_path_with_custom_max_path_length():
    """Test validation of path that exceeds custom max length."""
    validator = PathValidator("/too/long")
    res = validator.validate(max_path_length=1)
    assert isinstance(res, PathIsTooLongError)


def test_path_does_not_exist():
    """Test validation of path that does not exist."""
    validator = PathValidator(f"/{uuid.uuid4()}")
    res = validator.validate()
    assert isinstance(res, PathDoesNotExistError)


def test_max_path_length_unix_fallback_attribute_error():
    """Test max path length fallback when os.pathconf raises AttributeError on Unix."""
    # Simulate Unix platform where os.pathconf is not available
    with (
        mock.patch("platform.system", return_value="Linux"),
        mock.patch(
            "os.pathconf",
            side_effect=AttributeError("pathconf not available"),
            create=True,
        ),
    ):
        max_length = PathValidator.max_path_length()
        assert max_length == 4096


def test_max_path_length_unix_fallback_os_error():
    """Test max path length fallback when os.pathconf raises OSError on Unix."""
    # Simulate Unix platform where os.pathconf raises OSError
    with (
        mock.patch("platform.system", return_value="Linux"),
        mock.patch(
            "os.pathconf",
            side_effect=OSError("Invalid operation"),
            create=True,
        ),
    ):
        max_length = PathValidator.max_path_length()
        assert max_length == 4096


def test_max_path_length_unix_fallback_value_error():
    """Test max path length fallback when os.pathconf raises ValueError on Unix."""
    # Simulate Unix platform where os.pathconf raises ValueError
    with (
        mock.patch("platform.system", return_value="Linux"),
        mock.patch(
            "os.pathconf",
            side_effect=ValueError("Invalid pathconf name"),
            create=True,
        ),
    ):
        max_length = PathValidator.max_path_length()
        assert max_length == 4096
