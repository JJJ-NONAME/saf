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
import types
from typing import Self

import pytest

from ansys.saf.testing.docker import is_docker_installed_fun


def _mock_find_spec(name: str) -> str | None:
    assert name == "docker"
    return "Module is installed"


def mock_api_client_factory(expected_base_url: str | None, raise_exception: bool = False):
    class MockAPIClient:
        def __init__(self, base_url: str | None = None) -> None:
            assert base_url == expected_base_url

        def __enter__(self) -> Self:
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
        ) -> None:
            pass

        def ping(self) -> None:
            if raise_exception:
                raise Exception("Docker daemon not accessible")

    return MockAPIClient


class TestIsDockerInstalledFun:
    """Test cases for is_docker_installed_fun function."""

    def test_docker_installed_and_accessible(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test when docker is installed and daemon is accessible."""
        monkeypatch.setattr("ansys.saf.testing._docker.docker.find_spec", _mock_find_spec)
        monkeypatch.setattr("docker.APIClient", mock_api_client_factory(None, False))

        assert is_docker_installed_fun()

    def test_docker_host_environment_variable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that DOCKER_HOST environment variable is used."""
        monkeypatch.setattr("ansys.saf.testing._docker.docker.find_spec", _mock_find_spec)
        expected_url = "tcp://custom-host:2376"
        monkeypatch.setattr("docker.APIClient", mock_api_client_factory(expected_url, False))

        # Set DOCKER_HOST environment variable
        monkeypatch.setenv("DOCKER_HOST", expected_url)

        assert is_docker_installed_fun()

    def test_docker_host_environment_variable_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test when DOCKER_HOST environment variable is not set."""
        monkeypatch.setattr("ansys.saf.testing._docker.docker.find_spec", _mock_find_spec)
        monkeypatch.setattr("docker.APIClient", mock_api_client_factory(None, False))

        # Ensure DOCKER_HOST is not set
        monkeypatch.delenv("DOCKER_HOST", raising=False)

        assert is_docker_installed_fun()

    def test_docker_installed_but_not_accessible(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test when docker is installed but daemon is not accessible."""
        monkeypatch.setattr("ansys.saf.testing._docker.docker.find_spec", _mock_find_spec)
        monkeypatch.setattr("docker.APIClient", mock_api_client_factory(None, True))

        assert not is_docker_installed_fun()
