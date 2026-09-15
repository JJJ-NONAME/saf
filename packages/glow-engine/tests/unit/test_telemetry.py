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

import copy
import json
import logging
import logging.config
import os
from pathlib import Path
import re
from unittest import mock
import uuid

from pydantic import ValidationError
import pytest
import pytest_mock
import yaml

from ansys.saf.glow._config.const import (
    GLOW_DEBUG,
    GLOW_DEPLOYMENT,
    GLOW_LOGGING_LEVEL,
    GLOW_SOLUTION_DEFINITION,
    Deployment,
)
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._server.method_url import MethodUrl
from ansys.saf.glow._telemetry.config import (
    LOGGING_DEFAULT_CONFIG,
    create_logging_config,
    get_log_file_paths_from_config,
)
from ansys.saf.glow._telemetry.instrumentor import Instrumentor
from tests.conftest import PACKAGE_ROOT


@pytest.fixture(autouse=True)
def mock_settings_env_vars(tmp_path: Path):
    # Instrumentor modifies environment variables, such as f"{self._name}_GLOW_UI_INTERNAL_LOG_CONFIG",
    # which can affects other tests.
    tmp_path_str = str(tmp_path)
    with mock.patch.dict(
        os.environ,
        {
            "APPDATA": tmp_path_str,
            "XDG_DATA_HOME": tmp_path_str,
            GLOW_DEPLOYMENT: Deployment.Desktop.name,
            GLOW_SOLUTION_DEFINITION: "tests.mocks.solutions.minimal_solution",
        },
    ):
        yield


def test_get_log_file_returns_expected_path():
    container = "api_server"
    called_settings = Settings(
        glow_deployment=Deployment.Desktop,
        glow_log_config=Path(__file__).parent.parent / "mocks" / "logging_configs" / f"{container}_config_to_file.yaml",
    )
    log_config = create_logging_config("GLOW API", called_settings)
    log_file_paths = get_log_file_paths_from_config(log_config)
    assert len(log_file_paths) == 1
    log_file_path = Path(log_file_paths[0])
    expected_parent = called_settings.computed_solution_appdata_directory / "logs" / container
    assert log_file_path.parent == expected_parent
    assert log_file_path.suffix == ".log"


def test_get_log_file_using_method_name_returns_expected_path():
    container = "method_runner"
    called_settings = Settings(
        glow_deployment=Deployment.Desktop,
        glow_method_log_config=Path(__file__).parent.parent
        / "mocks"
        / "logging_configs"
        / f"{container}_config_to_file.yaml",
    )
    method_name = MethodUrl("http://209.191.122.70/projects/12345678/steps/my-step:test-method").method_name
    log_config = create_logging_config("GLOW METHOD RUNNER", called_settings, method_name)
    log_file_paths = get_log_file_paths_from_config(log_config)
    assert len(log_file_paths) == 1
    log_file_path = Path(log_file_paths[0])
    expected_parent = called_settings.computed_solution_appdata_directory / "logs" / "long_running_methods"
    assert log_file_path.parent == expected_parent
    expected_stem = f"log_{method_name}_"
    assert log_file_path.stem.startswith(expected_stem)
    assert log_file_path.suffix == ".log"


@pytest.mark.parametrize(
    ("logging_level", "debug_mode", "expected_level"),
    [
        (None, False, "INFO"),
        ("ERROR", False, "ERROR"),
        (None, True, "DEBUG"),
        ("WARNING", True, "DEBUG"),
    ],
)
@pytest.mark.parametrize(
    "config_file",
    [
        None,
        Path(__file__).parent.parent / "mocks" / "logging_configs" / "api_server_config_old.yaml",
        Path(__file__).parent.parent / "mocks" / "logging_configs" / "api_server_config_to_file.yaml",
    ],
)
def test_create_telemetry_config(
    monkeypatch: pytest.MonkeyPatch,
    logging_level: str | None,
    debug_mode: bool,
    expected_level: str,
    config_file: Path | None,
):
    # arrange
    if debug_mode:
        monkeypatch.setenv(GLOW_DEBUG, "True")
    else:
        monkeypatch.delenv(GLOW_DEBUG, raising=False)
    if logging_level:
        monkeypatch.setenv(GLOW_LOGGING_LEVEL, logging_level)
    else:
        monkeypatch.delenv(GLOW_LOGGING_LEVEL, raising=False)

    settings = Settings(
        glow_deployment=Deployment.Desktop,
        glow_log_config=config_file,
    )

    # act
    config = create_logging_config("GLOW API", settings)

    # assert
    if logging_level is None and debug_mode is False and config_file is None:
        assert config is None
    else:
        for handler in config["handlers"].values():
            assert handler["level"] == expected_level

        if config_file and config_file.stem == "api_server_config_old":
            assert config["root"]["level"] == expected_level
        else:
            assert config["root"]["level"] == "WARNING"
            for logger_conf in config["loggers"].values():
                assert logger_conf["level"] == expected_level


def test_default_telemetry_config():
    # GIVEN: Settings without any custom logging configuration
    with (
        mock.patch.object(logging.Logger, "info") as logging_info_mock,
        mock.patch.object(
            logging.config,
            "dictConfig",
        ) as logging_config,
        mock.patch.object(
            Instrumentor,
            "_instance",
            return_value=None,
            new_callable=mock.PropertyMock,
        ),
    ):
        # WHEN: Instrumenting
        Instrumentor.instrumentalize_process("GLOW API", Settings.model_validate({}))

        # THEN: LOGGING_DEFAULT_CONFIG is loaded and it contains the expected loggers and handlers
        last_config_applied = logging_config.call_args_list[-1][0][0]

        assert last_config_applied == LOGGING_DEFAULT_CONFIG
        logging_info_mock.assert_called_once_with("Using default logging config for GLOW API")

        assert last_config_applied["root"]["level"] == "WARNING"
        root_handler = last_config_applied["root"]["handlers"][0]
        assert last_config_applied["handlers"][root_handler]["class"] == "logging.StreamHandler"
        assert last_config_applied["handlers"][root_handler]["level"] == "INFO"
        assert "sys.stderr" in last_config_applied["handlers"][root_handler]["stream"]

        assert last_config_applied["loggers"]["ansys"]["level"] == "INFO"
        ansys_handler = last_config_applied["loggers"]["ansys"]["handlers"][0]
        assert last_config_applied["handlers"][ansys_handler]["class"] == "logging.StreamHandler"
        assert last_config_applied["handlers"][ansys_handler]["level"] == "INFO"
        assert "sys.stderr" in last_config_applied["handlers"][ansys_handler]["stream"]
        assert not last_config_applied["loggers"]["ansys"]["propagate"]


def test_default_telemetry_config_not_modified():
    # GIVEN: Settings with a custom logging configuration that is applied over LOGGING_DEFAULT_CONFIG
    settings = Settings(
        glow_deployment=Deployment.Desktop,
        glow_debug=True,
    )

    with (
        mock.patch.object(logging.config, "dictConfig") as logging_config,
        mock.patch.object(
            Instrumentor,
            "_instance",
            return_value=None,
            new_callable=mock.PropertyMock,
        ),
    ):
        # WHEN: Instrumenting
        Instrumentor.instrumentalize_process("GLOW API", settings)

        # THEN: LOGGING_DEFAULT_CONFIG is not modified
        last_config_applied = logging_config.call_args_list[-1][0][0]
        assert last_config_applied != LOGGING_DEFAULT_CONFIG
        ansys_handler = last_config_applied["loggers"]["ansys"]["handlers"][0]
        assert LOGGING_DEFAULT_CONFIG["handlers"][ansys_handler]["level"] == "INFO"
        assert last_config_applied["handlers"][ansys_handler]["level"] == "DEBUG"


def test_telemetry_logs_to_logging_file():
    # GIVEN: Settings with a custom logging configuration file that contains a file handler
    settings = Settings(
        glow_deployment=Deployment.Desktop,
        glow_log_config=Path(__file__).parent.parent / "mocks" / "logging_configs" / "api_server_config_to_file.yaml",
    )

    with (
        mock.patch.object(logging.Logger, "info") as logging_info_mock,
        mock.patch.object(
            logging.config,
            "dictConfig",
        ),
        mock.patch.object(Instrumentor, "_instance", return_value=None, new_callable=mock.PropertyMock),
    ):
        # WHEN: Instrumenting
        Instrumentor.instrumentalize_process("GLOW API", settings)

        # THEN: Custom log config file is applied and a log message is shown before the configuration is applied
        #       with the path to the log files.
        assert any(
            "Applied user logging configuration for GLOW API" in args[0][0] for args in logging_info_mock.call_args_list
        )
        log_file = None
        for args in logging_info_mock.call_args_list:
            if "GLOW API logging to " in args[0][0]:
                log_file = Path(args[0][0].split("logging to ")[-1])
        assert isinstance(log_file, Path)
        # Log file doesn't exist, because logging is actually mocked and no info messages pass through.
        # However, parent dir should have been created.
        assert log_file.parent.is_dir()


def test_telemetry_invalid_log_config():
    # GIVEN: Settings with a custom logging configuration file that is invalid
    # THEN: An error is raised
    fake_file = Path("fake_file.txt").absolute()
    with pytest.raises(
        ValidationError,
        match=re.escape(f"The system cannot find the path '{fake_file}' specified by GLOW_LOG_CONFIG"),
    ):
        Settings(
            glow_deployment=Deployment.Desktop,
            glow_log_config=fake_file,
        )


def test_telemetry_invalid_config(tmp_path: Path):
    # GIVEN: Settings with a custom logging configuration file that has a file handler with an invalid filename
    #        This applies to any invalid config.
    logging_config_with_wrong_filename = {
        "version": 1,
        "handlers": {"file": {"class": "logging.handlers.TimedRotatingFileHandler", "level": "INFO", "filename": 56}},
        "root": {"level": "WARNING", "handlers": ["file"]},
    }

    with Path(tmp_path / "logging_config_wrong_filename.yaml").open("w") as config_file:
        yaml.dump(logging_config_with_wrong_filename, config_file)

    settings = Settings(
        glow_deployment=Deployment.Desktop,
        glow_log_config=tmp_path / "logging_config_wrong_filename.yaml",
    )

    # WHEN: Instrumenting
    with mock.patch.object(  # noqa: SIM117
        Instrumentor,
        "_instance",
        return_value=None,
        new_callable=mock.PropertyMock,
    ):
        with pytest.raises(ValueError, match="Unable to configure handler 'file'"):
            # THEN: An error is raised
            Instrumentor.instrumentalize_process("GLOW API", settings)
            # FIXME: configuration applied by Instrumentor (DEFAULT) is leaked to other tests


def test_telemetry_multiple_filebased_handlers(tmp_path: Path):
    # GIVEN: Settings with a custom logging configuration file that has multiple file handlers of different types
    log_files = [str(tmp_path / str(uuid.uuid4()) / f"file_{str(i)}.log") for i in range(3)]
    assert all(not Path(log_file).parent.is_dir() for log_file in log_files)

    logging_config_with_multiple_file_handlers = {
        "version": 1,
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "filename": log_files[0],
            },
            "file2": {
                "class": "logging.handlers.WatchedFileHandler",
                "level": "INFO",
                "filename": log_files[1],
            },
            "file3": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "INFO",
                "filename": log_files[2],
            },
        },
        "root": {"level": "WARNING", "handlers": ["file", "file2", "file3"]},
    }

    with Path(tmp_path / "logging_config_multiple_files.yaml").open("w") as config_file:
        yaml.dump(logging_config_with_multiple_file_handlers, config_file)

    settings = Settings(
        glow_deployment=Deployment.Desktop,
        glow_log_config=tmp_path / "logging_config_multiple_files.yaml",
    )

    with (
        mock.patch.object(logging.Logger, "info") as logging_info_mock,
        mock.patch.object(
            logging.config,
            "dictConfig",
        ),
        mock.patch.object(Instrumentor, "_instance", return_value=None, new_callable=mock.PropertyMock),
    ):
        # WHEN: Instrumenting
        Instrumentor.instrumentalize_process("GLOW API", settings)

        # THEN: Custom config is applied and all file handlers and log files are parsed,
        # managed (dir is created) and shown.
        assert any(
            "Applied user logging configuration for GLOW API" in args[0][0] for args in logging_info_mock.call_args_list
        )
        assert any(
            f"GLOW API logging to {', '.join(log_files)}" in args[0][0] for args in logging_info_mock.call_args_list
        )
        assert all(Path(log_file).parent.is_dir() for log_file in log_files)


def test_telemetry_default_config_does_not_propagate(tmp_path: Path):
    # GIVEN: Instrumentor with default config should have ansys logger without propagate
    Instrumentor.instrumentalize_process("GLOW API", Settings.model_validate({}))
    assert not logging.getLogger("ansys").propagate

    # GIVEN: a filehandler added to root logger so we can easily track which messages reach this logger
    log_file = tmp_path / str(uuid.uuid4()) / "log_file.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(filename=str(log_file))
    logging.getLogger().addHandler(handler)

    # WHEN: logging a test message using ansys logger
    logging.getLogger("ansys").info("test message")
    handler.flush()

    # THEN: log file doesn't contain the message
    assert not log_file.read_text()

    # WHEN: enabling the propagate attribute of ansys logger and sending again the message
    logging.getLogger("ansys").propagate = True
    assert logging.getLogger("ansys").propagate
    logging.getLogger("ansys").info("test message")
    handler.flush()

    # THEN: log file contains the message
    assert "test message" in log_file.read_text()

    # END: Undo logging configuration
    logging.getLogger().removeHandler(handler)
    handler.close()
    # FIXME: configuration applied by Instrumentor is leaked to other tests


def test_telemetry_reload_detected(tmp_path: Path):
    # INIT: ENV VAR where logging configs are saved is not set
    assert not os.environ.get("GLOW_API_INTERNAL_LOG_CONFIG")

    # GIVEN: User customizes logging using a config file
    custom_config = copy.deepcopy(LOGGING_DEFAULT_CONFIG)
    custom_config["formatters"]["streamFormat"]["format"] += " [TEST CONFIG]"
    with (tmp_path / "custom_log_config.yaml").open("w") as config_file:
        yaml.dump(custom_config, config_file)

    settings = Settings(
        glow_deployment=Deployment.Desktop,
        glow_log_config=tmp_path / "custom_log_config.yaml",
    )

    # WHEN: Instrumenting
    with (
        mock.patch.object(logging.Logger, "info") as logging_info_mock,
        mock.patch.object(
            logging.config,
            "dictConfig",
        ) as logging_config,
        mock.patch.object(
            Instrumentor,
            "_instance",
            return_value=None,
            new_callable=mock.PropertyMock,
        ),
    ):
        Instrumentor.instrumentalize_process("GLOW API", settings)

        # THEN: Custom config from file is applied and saved into the env var
        assert logging_info_mock.call_args_list[0][0][0] == "Applied user logging configuration for GLOW API"
        assert logging_config.call_args_list[-1][0][0] == custom_config
        assert json.loads(os.environ["GLOW_API_INTERNAL_LOG_CONFIG"]) == custom_config

    # GIVEN: ENV VAR with logging config saved (different from first one, just to check that it is actually loaded)
    custom_config_modified = copy.deepcopy(custom_config)
    custom_config_modified["formatters"]["streamFormat"]["format"] += " [TEST CONFIG 2]"
    os.environ["GLOW_API_INTERNAL_LOG_CONFIG"] = json.dumps(custom_config_modified)

    # WHEN: Instrumenting
    with (
        mock.patch.object(logging.Logger, "info") as logging_info_mock,
        mock.patch.object(
            logging.config,
            "dictConfig",
        ) as logging_config,
        mock.patch.object(
            Instrumentor,
            "_instance",
            return_value=None,
            new_callable=mock.PropertyMock,
        ),
    ):
        Instrumentor.instrumentalize_process("GLOW API", settings)

        # THEN: Custom config is loaded from env var and applied
        assert (
            logging_info_mock.call_args_list[0][0][0]
            == "Reload detected, reusing existing logging configuration for GLOW API"
        )
        assert logging_config.call_args_list[-1][0][0] == custom_config_modified


def test_telemetry_user_config_is_complementary(tmp_path: Path):
    # GIVEN: Settings with a custom logging configuration file that has a new logger,
    # different from the ones in DEFAULT_LOGGING_CONFIG
    log_file = tmp_path / str(uuid.uuid4()) / "log_file.log"
    logging_config_overwrites_partially = {
        "version": 1,
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "level": "CRITICAL",
                "filename": str(log_file),
            },
        },
        "loggers": {
            "ansys.saf.portal": {
                "level": "CRITICAL",
                "handlers": ["file"],
                "propagate": False,
            },
        },
    }
    assert "ansys.saf.portal" not in LOGGING_DEFAULT_CONFIG.get("loggers", {})

    with Path(tmp_path / "logging_config_overwrites_partially.yaml").open("w") as config_file:
        yaml.dump(logging_config_overwrites_partially, config_file)

    settings = Settings(
        glow_deployment=Deployment.Desktop,
        glow_log_config=tmp_path / "logging_config_overwrites_partially.yaml",
    )

    # WHEN: Instrumenting
    with (
        mock.patch.object(logging.Logger, "info") as logging_info_mock,
        mock.patch.object(
            Instrumentor,
            "_instance",
            return_value=None,
            new_callable=mock.PropertyMock,
        ),
    ):
        Instrumentor.instrumentalize_process("GLOW API", settings)

        # THEN: User config is applied upon the DEFAULT_LOGGING_CONFIG
        assert logging_info_mock.call_args_list[0][0][0] == "Applied user logging configuration for GLOW API"
        assert f"GLOW API logging to {str(log_file)}" == logging_info_mock.call_args_list[1][0][0]

        assert logging.getLevelName(logging.getLogger().level) == LOGGING_DEFAULT_CONFIG["root"]["level"]
        assert (
            logging.getLevelName(logging.getLogger("ansys").level)
            == LOGGING_DEFAULT_CONFIG["loggers"]["ansys"]["level"]
        )
        assert logging.getLevelName(logging.getLogger("ansys.saf.portal").level) == "CRITICAL"
        # FIXME: configuration applied by Instrumentor is leaked to other tests


def test_telemetry_resource(tmp_path: Path):
    # GIVEN: Default logging configuration
    with (
        mock.patch.object(logging.Logger, "info"),
        mock.patch.object(logging.config, "dictConfig"),
        mock.patch.object(
            Instrumentor,
            "_instance",
            return_value=None,
            new_callable=mock.PropertyMock,
        ),
    ):
        # WHEN: Instrumenting
        # THEN: OpenTelemetry Logging Instrumentation is injected
        # https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/logging/logging.html
        Instrumentor.instrumentalize_process("GLOW API", Settings.model_validate({}))

        # WHEN: Adding a file handler to root with the OTEL keys and logging a message
        log_file = tmp_path / str(uuid.uuid4()) / "log_file.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(filename=str(log_file))
        handler.setFormatter(
            logging.Formatter(
                "[trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s trace_sampled=%(otelTraceSampled)s]- %(message)s",  # noqa: E501
            ),
        )
        logging.getLogger().addHandler(handler)
        logging.getLogger().warning("test_message")
        handler.flush()

        # THEN: log doesn't raise an error an OTEL keys have non-empty values
        log_message = log_file.read_text()
        assert log_message.split("trace_id=")[-1].split(" ")[0]
        assert log_message.split("span_id=")[-1].split(" ")[0]
        assert log_message.split("resource.service.name=")[-1].split(" ")[0]
        assert log_message.split("trace_sampled=")[-1].split("]-")[0]

        # END: Undo logging configuration
        logging.getLogger().removeHandler(handler)
        handler.close()


def test_root_logger_is_not_used():
    # GIVEN: src dir for glow engine, assuming pytest execution from repo root
    src_dir = PACKAGE_ROOT / "src"
    assert src_dir.is_dir()

    # WHEN: looking for logging statements that use the root logger
    logging_statements = [
        "logging.debug(",
        "logging.info(",
        "logging.warning(",
        "logging.error(",
        "logging.critical(",
        "logging.exception(",
        "root_logger.debug(",
        "root_logger.info(",
        "root_logger.warning(",
        "root_logger.error(",
        "root_logger.critical(",
        "root_logger.exception(",
        "logging.getLogger().debug(",
        "logging.getLogger().info(",
        "logging.getLogger().warning(",
        "logging.getLogger().error(",
        "logging.getLogger().critical(",
        "logging.getLogger().exception(",
    ]
    for python_file in src_dir.rglob("*.py"):
        content = python_file.read_text()
        # THEN: no statement is found
        if any(log_statement in content for log_statement in logging_statements):
            pytest.fail(reason=f"File {python_file} contains root logging statements.")


def test_instrumentor_cannot_be_directly_instantiated():
    with pytest.raises(
        RuntimeError,
        match="Direct instantiation is not allowed. Use Instrumentor.instrumentalize_process().",
    ):
        Instrumentor()


def test_instrumentor_is_only_executed_one_per_process(mocker: pytest_mock.MockFixture):
    mocker.patch.object(Instrumentor, "_instance", return_value=None, new_callable=mock.PropertyMock)
    init = mocker.spy(Instrumentor, "_initialize")
    config_logs = mocker.spy(Instrumentor, "_configure_logging")
    config_traces = mocker.spy(Instrumentor, "_configure_tracing")
    config_metrics = mocker.spy(Instrumentor, "_configure_metrics")

    Instrumentor.instrumentalize_process("TEST", Settings.model_validate({}))
    assert init.call_count == config_logs.call_count == config_traces.call_count == config_metrics.call_count == 1
    Instrumentor.instrumentalize_process("TEST", Settings.model_validate({}))
    assert init.call_count == config_logs.call_count == config_traces.call_count == config_metrics.call_count == 1

    # Changing the name, the settings or other parameter does not trigger re-instrumentalization
    Instrumentor.instrumentalize_process("Other name", Settings.model_validate({}))
    assert init.call_count == config_logs.call_count == config_traces.call_count == config_metrics.call_count == 1
    Instrumentor.instrumentalize_process("New name", Settings(glow_hps_host="fake_host"))
    assert init.call_count == config_logs.call_count == config_traces.call_count == config_metrics.call_count == 1
