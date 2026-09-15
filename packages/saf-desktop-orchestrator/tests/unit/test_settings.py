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

from pathlib import Path

from pydantic import ValidationError
import pytest

from ansys.saf.desktop.orchestrator._config.schema import (
    DEFAULT_PORTAL_API_VERSION,
    DEFAULT_SAF_DESKTOP_HEALTH_CHECK_TIMEOUT,
    OTEL_EXPORTER_OTLP_ENDPOINT,
    PORTAL_API_VERSION,
    SAF_DEFINITION_PATH,
    SAF_DESKTOP_HEALTH_CHECK_TIMEOUT,
    SAF_DESKTOP_LOG_TO_FILES,
    SAF_DESKTOP_SOLUTION_NAME,
    SAF_DESKTOP_TEST_ENV,
    Settings,
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch):
    env_vars_to_clean = [
        SAF_DESKTOP_SOLUTION_NAME,
        PORTAL_API_VERSION,
        SAF_DESKTOP_TEST_ENV,
        SAF_DEFINITION_PATH,
        SAF_DESKTOP_HEALTH_CHECK_TIMEOUT,
        SAF_DESKTOP_LOG_TO_FILES,
        OTEL_EXPORTER_OTLP_ENDPOINT,
    ]
    for var in env_vars_to_clean:
        monkeypatch.delenv(var, raising=False)


def test_required_field_solution_name_missing_raises_error():
    with pytest.raises(ValidationError, match="saf_desktop_solution_name\n  Field required"):
        Settings()  # pyright: ignore[reportCallIssue]


def test_default_settings(mock_appdata: Path):
    settings = Settings(saf_desktop_solution_name="test-solution")

    assert settings.saf_desktop_solution_name == "test-solution"
    assert settings.portal_api_version == DEFAULT_PORTAL_API_VERSION
    assert settings.saf_desktop_test_env is False
    assert settings.saf_definition_path is None
    assert settings.saf_desktop_health_check_timeout == DEFAULT_SAF_DESKTOP_HEALTH_CHECK_TIMEOUT
    assert settings.saf_desktop_log_to_files is False
    assert settings.computed_solution_appdata_directory == mock_appdata / "ansys" / "glow" / "test-solution"


def test_settings_from_environment_variables(mock_appdata: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(SAF_DESKTOP_SOLUTION_NAME, "will-be-overridden")
    monkeypatch.setenv(PORTAL_API_VERSION, "v2")
    monkeypatch.setenv(SAF_DESKTOP_TEST_ENV, "true")
    monkeypatch.setenv(SAF_DEFINITION_PATH, "/path/to/definition.yaml")
    monkeypatch.setenv(SAF_DESKTOP_HEALTH_CHECK_TIMEOUT, "30")
    monkeypatch.setenv(SAF_DESKTOP_LOG_TO_FILES, "true")

    settings = Settings(saf_desktop_solution_name="env-solution")

    assert settings.saf_desktop_solution_name == "env-solution"
    assert settings.portal_api_version == "v2"
    assert settings.saf_desktop_test_env is True
    assert settings.saf_definition_path == Path("/path/to/definition.yaml")
    assert settings.saf_desktop_health_check_timeout == 30
    assert settings.saf_desktop_log_to_files is True
    assert settings.computed_solution_appdata_directory == mock_appdata / "ansys" / "glow" / "env-solution"


def test_explicit_values_override_environment(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(SAF_DESKTOP_SOLUTION_NAME, "env-solution")
    monkeypatch.setenv(PORTAL_API_VERSION, "v2")

    settings = Settings(saf_desktop_solution_name="explicit-solution", portal_api_version="v3")

    assert settings.saf_desktop_solution_name == "explicit-solution"
    assert settings.portal_api_version == "v3"


@pytest.mark.parametrize(
    ("env_value", "expected"),
    [
        ("True", True),
        ("true", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("False", False),
        ("false", False),
        ("0", False),
        ("no", False),
        ("off", False),
        ("", None),
        ("test", None),
    ],
)
def test_boolean_parsing_from_environment(env_value: str, expected: bool | None, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(SAF_DESKTOP_LOG_TO_FILES, env_value)

    if expected is None:
        with pytest.raises(ValidationError, match="saf_desktop_log_to_files\n  Input should be a valid boolean"):
            Settings(saf_desktop_solution_name="test")
    else:
        settings = Settings(saf_desktop_solution_name="test")

        assert settings.saf_desktop_log_to_files == expected


def test_otel_set_with_log_to_files_true_raises_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_ENDPOINT, "http://localhost:4317")
    monkeypatch.setenv(SAF_DESKTOP_LOG_TO_FILES, "true")

    error_msg = (
        "saf_desktop_log_to_files\n  Value error, "
        "The env var 'OTEL_EXPORTER_OTLP_ENDPOINT' is defined but it is not compatible with logging to files."
    )
    with pytest.raises(ValidationError, match=error_msg):
        Settings(saf_desktop_solution_name="test")
