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

from collections.abc import Callable
import contextlib
import json
import logging
import logging.config
import multiprocessing
import os
import pathlib
import random
from typing import Any
from unittest import mock
from unittest.mock import patch
import uuid

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore
from opentelemetry.instrumentation.logging.handler import LoggingHandler  # pyright: ignore[reportMissingTypeStubs]
import pytest
import uvicorn

from ansys.saf.glow._config.const import (
    GLOW_DEBUG,
    GLOW_DEPLOYMENT,
    GLOW_LOGGING_LEVEL,
    GLOW_SOLUTION_DEFINITION,
    OTEL_EXPORTER_OTLP_ENDPOINT,
    Deployment,
)
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._telemetry.config import LOGGING_DEFAULT_CONFIG
from ansys.saf.glow._telemetry.instrumentor import Instrumentor
from ansys.saf.glow._utilities.ip_utilities import get_random_free_port
from ansys.saf.glow.cli._cli_entry_point import run_api
from tests.mocks.solutions import minimal_solution

with contextlib.suppress(Exception):
    multiprocessing.set_start_method("spawn")


def _find_log_in_otlp(otlp_content: list[dict[str, Any]], log_msg: str, log_level: str) -> dict[str, Any] | None:
    for m in otlp_content:
        if m.get("body", "") == log_msg and m["severity_text"] == log_level:
            return m


def _find_span_in_otlp(
    otlp_content: list[dict[str, Any]],
    span_name: str,
    span_attributes: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    for m in otlp_content:
        if m.get("name", "") == span_name and (span_attributes is None or m["attributes"] == span_attributes):
            return m


def _find_metrics_in_otlp(otlp_content: list[dict[str, Any]]) -> dict[str, Any] | None:
    for m in otlp_content:
        if "resource_metrics" in m:
            return m


@pytest.fixture
def run_otlp_process(tmp_path: pathlib.Path):
    def _run_otlp_process(function: Callable[[pathlib.Path], None]) -> list[dict[str, Any]]:
        output_file = tmp_path / f"{str(uuid.uuid4())}.log"
        p = multiprocessing.Process(target=function, args=(output_file,))
        p.start()
        p.join()
        captured_output = output_file.read_text().splitlines()
        # output contains lines from the logging module and lines from the OTLP module
        # keep only the ones from OTLP
        otlp_output = [line for line in captured_output if "resource.service.name=TEST]-" not in line]
        otlp_content = json.loads("[" + "".join(otlp_output).replace("}{", "}, {") + "]")
        return otlp_content

    return _run_otlp_process


@pytest.fixture
def mock_settings_env_vars(tmp_path: pathlib.Path):
    tmp_path_str = str(tmp_path)
    # port is not going to be used, but should be random to test that is configured with it
    random_otlp_port = random.randint(5000, 50000)
    with mock.patch.dict(
        os.environ,
        {
            "APPDATA": tmp_path_str,
            "XDG_DATA_HOME": tmp_path_str,
            GLOW_DEPLOYMENT: Deployment.Desktop.name,
            OTEL_EXPORTER_OTLP_ENDPOINT: f"http://localhost:{random_otlp_port}",
            GLOW_SOLUTION_DEFINITION: "tests.mocks.solutions.minimal_solution",
        },
    ):
        yield


@pytest.fixture
def mock_settings_console_env_vars(tmp_path: pathlib.Path):
    tmp_path_str = str(tmp_path)
    with mock.patch.dict(
        os.environ,
        {
            "APPDATA": tmp_path_str,
            "XDG_DATA_HOME": tmp_path_str,
            GLOW_DEPLOYMENT: Deployment.Desktop.name,
            OTEL_EXPORTER_OTLP_ENDPOINT: "console",
            GLOW_SOLUTION_DEFINITION: "tests.mocks.solutions.minimal_solution",
        },
    ):
        yield


@pytest.mark.usefixtures("mock_settings_env_vars")
@pytest.mark.parametrize(
    ("logging_level", "debug_mode", "expected_level"),
    [
        (None, False, "INFO"),
        ("ERROR", False, "ERROR"),
        (None, True, "DEBUG"),
        ("WARNING", True, "DEBUG"),
    ],
)
def test_otlp_http_stack_is_setup(
    monkeypatch: pytest.MonkeyPatch,
    debug_mode: bool,
    logging_level: str | None,
    expected_level: str | None,
):
    # ARRANGE
    if debug_mode:
        monkeypatch.setenv(GLOW_DEBUG, "True")
    else:
        monkeypatch.delenv(GLOW_DEBUG, raising=False)
    if logging_level:
        monkeypatch.setenv(GLOW_LOGGING_LEVEL, logging_level)
    else:
        monkeypatch.delenv(GLOW_LOGGING_LEVEL, raising=False)

    # ACT
    with (
        patch("ansys.saf.glow._telemetry.instrumentor.OTLPSpanExporter") as mock_otlp_span_exporter,
        patch(
            "ansys.saf.glow._telemetry.instrumentor.OTLPLogExporter",
        ) as mock_otlp_log_exporter,
        patch(
            "ansys.saf.glow._telemetry.instrumentor.OTLPMetricExporter",
        ) as mock_otlp_metric_exporter,
        mock.patch.object(
            logging.Logger,
            "info",
        ) as logging_info_mock,
        mock.patch.object(
            logging.Logger,
            "setLevel",
        ) as logging_set_level,
        mock.patch.object(
            logging.Logger,
            "addHandler",
        ) as logging_add_handler,
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
        Instrumentor.instrumentalize_process("TEST", Settings.model_validate({}))

        # ASSERT: logging is configured and all exporters are initialised
        logging_config.assert_called_once_with(LOGGING_DEFAULT_CONFIG)
        assert (
            logging_info_mock.call_args_list[0][0][0] == "Telemetry enabled, using OTLP logging configuration for TEST"
        )

        assert (
            logging.getLevelName(logging_set_level.call_args_list[-1][0][0])  # pyright: ignore[reportDeprecated]
            == expected_level
        )
        added_handler = logging_add_handler.call_args_list[-1][0][0]
        assert isinstance(added_handler, LoggingHandler)
        assert logging.getLevelName(added_handler.level) == expected_level

        mock_otlp_span_exporter.assert_called_once()
        mock_otlp_log_exporter.assert_called_once()
        mock_otlp_metric_exporter.assert_called_once()


def sample_instrumented_code(output_file: pathlib.Path):
    # Small snippet executed in a different process, to avoid many issues due to trying to run this instrumented code
    # with all the leaks from other tests that also use instrumented-code, even if it's partially mocked.
    with output_file.open("w") as output, mock.patch("sys.stderr", output):
        instrumentor = Instrumentor.instrumentalize_process("TEST", Settings.model_validate({}))
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("TEST SPAN") as span:
            span.set_attribute("my_attribute", "hello")
            logging.getLogger("ansys").info("test message")
        counter = instrumentor.meter.create_counter(name="my.metric.counter", description="custom metric")
        counter.add(2)
        instrumentor.force_flush()


@pytest.mark.usefixtures("mock_settings_console_env_vars")
def test_otlp_console_stack_is_setup(
    run_otlp_process: Callable[[Callable[[pathlib.Path], None]], list[dict[str, Any]]],
):
    # ACT
    otlp_content = run_otlp_process(sample_instrumented_code)

    # ASSERT: otlp exports traces, logs and metrics
    assert _find_log_in_otlp(otlp_content, "test message", "INFO")
    assert _find_span_in_otlp(otlp_content, "TEST SPAN", {"my_attribute": "hello"})
    assert _find_metrics_in_otlp(otlp_content)


def sample_run_method_code(output_file: pathlib.Path):
    # Small snippet executed in a different process, to avoid many issues due to trying to run this instrumented code
    # with all the leaks from other tests that also use instrumented-code, even if it's partially mocked.
    import httpx2

    from ansys.saf.glow._executor.method_runner import ThreadMethodRunner
    from ansys.saf.glow._server.method_url import MethodUrl

    settings = Settings()

    with (
        output_file.open("w") as output,
        mock.patch("sys.stderr", output),
        mock.patch.object(
            ThreadMethodRunner,
            "_run_method",
        ),
        mock.patch.object(
            ThreadMethodRunner,
            "_set_method_state",
        ),
        mock.patch.object(
            ThreadMethodRunner,
            "_get_transaction_step_method",
        ),
        mock.patch.object(
            ThreadMethodRunner,
            "_raise_method_event",
        ),
        mock.patch.object(
            ThreadMethodRunner,
            "_create_method_storage_scope",
            new=lambda self: setattr(self, "_multiplexor_method_storage_scope", None),  # type: ignore
        ),
    ):
        instrumentor = Instrumentor.instrumentalize_process("TEST", Settings.model_validate({}))
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("PARENT METHOD EXECUTION"):
            transaction_url = MethodUrl(
                "http://my_host:my_port/projects/project_fake/steps/step_fake:transaction_fake",
            )
            ThreadMethodRunner(
                project_id=None,  # pyright: ignore[reportArgumentType]
                solution=None,  # pyright: ignore[reportArgumentType]
                method_url=transaction_url,
                settings=settings,
                instance_system_factory=None,  # pyright: ignore[reportArgumentType]
                http_client=httpx2.Client(),
                graphql_client=None,  # pyright: ignore[reportArgumentType]
                multiplexor_storage_factory=None,  # pyright: ignore[reportArgumentType]
                oidc_client=None,  # pyright: ignore[reportArgumentType]
            ).run_method()
            logging.getLogger("ansys").info(f"expected-transaction-url: {transaction_url.url}")
        instrumentor.force_flush()


def sample_run_long_running_method_code(output_file: pathlib.Path):
    # Small snippet executed in a different process, to avoid many issues due to trying to run this instrumented code
    # with all the leaks from other tests that also use instrumented-code, even if it's partially mocked.
    from ansys.saf.glow._executor.method_runner import ProcessMethodRunner
    from ansys.saf.glow._server.method_url import MethodUrl

    settings = Settings()

    with (
        output_file.open("w") as output,
        mock.patch("sys.stderr", output),
        mock.patch.object(
            ProcessMethodRunner,
            "_run_method",
        ),
        mock.patch.object(
            ProcessMethodRunner,
            "_set_method_state",
        ),
        mock.patch.object(
            ProcessMethodRunner,
            "_get_transaction_step_method",
        ),
        mock.patch.object(
            ProcessMethodRunner,
            "_raise_method_event",
        ),
        mock.patch.object(
            ProcessMethodRunner,
            "_create_method_storage_scope",
            new=lambda self: setattr(self, "_multiplexor_method_storage_scope", None),  # type: ignore
        ),
    ):
        instrumentor = Instrumentor.instrumentalize_process("TEST", Settings.model_validate({}))
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("PARENT METHOD EXECUTION"):
            transaction_url = MethodUrl(
                "http://my_host:my_port/projects/project_fake/steps/step_fake:transaction_fake",
            )
            ProcessMethodRunner(
                project_id=None,  # pyright: ignore[reportArgumentType]
                solution=None,  # pyright: ignore[reportArgumentType]
                method_url=transaction_url,
                settings=settings,
                instance_system_factory=None,  # pyright: ignore[reportArgumentType]
                multiplexor_storage_factory=None,  # pyright: ignore[reportArgumentType]
                oidc_client=None,  # pyright: ignore[reportArgumentType]
            ).run_method()
            logging.getLogger("ansys").info(f"expected-transaction-url: {transaction_url.url}")
        instrumentor.force_flush()


@pytest.mark.usefixtures("mock_settings_console_env_vars")
@pytest.mark.parametrize("long_running", [True, False])
def test_method_transaction_creates_linked_span(
    run_otlp_process: Callable[[Callable[[pathlib.Path], None]], list[dict[str, Any]]],
    long_running: bool,
):
    """Test that a transaction creates the expected span, linked to the parent one."""
    # ACT
    if long_running:
        otlp_content = run_otlp_process(sample_run_long_running_method_code)
    else:
        otlp_content = run_otlp_process(sample_run_method_code)

    # ASSERT
    parent_span = _find_span_in_otlp(otlp_content, "PARENT METHOD EXECUTION", {})
    assert parent_span
    assert not parent_span["parent_id"]
    parent_trace_id = parent_span["context"]["trace_id"]
    parent_span_id = parent_span["context"]["span_id"]

    method_runner_span = _find_span_in_otlp(
        otlp_content,
        "METHOD EXECUTION",
        {"method_url": "http://my_host:my_port/projects/project_fake/steps/step_fake:transaction_fake"},
    )
    assert method_runner_span
    assert method_runner_span["context"]["trace_id"] == parent_trace_id
    assert method_runner_span["parent_id"] == parent_span_id


def sample_dash_callback_code(output_file: pathlib.Path):
    # Small snippet executed in a different process, to avoid many issues due to trying to run this instrumented code
    # with all the leaks from other tests that also use instrumented-code, even if it's partially mocked.
    from ansys.saf.glow._client.dashclient import callback

    class mocked_dash_callback:  # noqa: N801
        def __call__(self, f: Callable[[], Any]):
            f()

    def _example_callback() -> Any:
        logging.getLogger("ansys.solutions.my_solution.ui").warning("test solution message")

    with (
        output_file.open("w") as output,
        mock.patch("sys.stderr", output),
        mock.patch(
            "dash_extensions.enrich.callback",
            mocked_dash_callback,
        ),
    ):
        instrumentor = Instrumentor.instrumentalize_process("TEST", Settings.model_validate({}))
        callback().__call__(_example_callback)
        instrumentor.force_flush()


@pytest.mark.usefixtures("mock_settings_console_env_vars")
def test_dash_callback_span(run_otlp_process: Callable[[Callable[[pathlib.Path], None]], list[dict[str, Any]]]):
    """Test that the dashclient's callback creates the expected span and log messages."""
    # ACT
    otlp_content = run_otlp_process(sample_dash_callback_code)

    # ASSERT
    assert _find_log_in_otlp(
        otlp_content,
        "started callback _example_callback in tests.unit.test_observability",
        "INFO",
    )
    assert _find_log_in_otlp(
        otlp_content,
        "completed callback _example_callback in tests.unit.test_observability",
        "INFO",
    )
    assert _find_log_in_otlp(otlp_content, "test solution message", "WARN")
    assert _find_span_in_otlp(otlp_content, "callback _example_callback in tests.unit.test_observability", {})


def test_api_server_instrumented():
    """Test that fastapi app used for API server is instrumented"""
    # ACT
    with (
        mock.patch.dict(os.environ, os.environ.copy()),
        mock.patch.object(
            uvicorn.Server,
            "main_loop",
        ),
        mock.patch.object(FastAPIInstrumentor, "instrument_app") as fast_api_instrumentor,
        mock.patch.object(
            Instrumentor,
            "_instance",
            return_value=None,
            new_callable=mock.PropertyMock,
        ),
    ):
        # calling run_api is going to set env vars, mock os.environ to leave it clean
        run_api("127.0.0.1", get_random_free_port(), minimal_solution)

    # ASSERT
    fast_api_instrumentor.assert_called_once()


def sample_client_api_code(output_file: pathlib.Path):
    # Small snippet executed in a different process, to avoid many issues due to trying to run this instrumented code
    # with all the leaks from other tests that also use instrumented-code, even if it's partially mocked.
    import httpx2

    from ansys.saf.glow._utilities.solution_modules import find_solution
    from ansys.saf.glow.client import Client

    with (
        output_file.open("w") as output,
        mock.patch("sys.stderr", output),
        mock.patch.object(
            httpx2.HTTPTransport,
            "handle_request",
            return_value=httpx2.Response(200),
        ) as mocked_http_transport,
    ):
        instrumentor = Instrumentor.instrumentalize_process("TEST", Settings.model_validate({}))
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("PARENT CLIENT API"):
            c = Client(find_solution(minimal_solution), "")
            c._http_client.get("http://www.google.es")  # type: ignore
            http_request = mocked_http_transport.call_args_list[0][0][0]
            traceparent = http_request.headers.get("traceparent", "")
            # Keep only trace_id-span_id because version/flags may vary
            traceparent_middle = "-".join(traceparent.split("-")[1:3])
            logging.getLogger("ansys").info(f"request-header-traceparent: {traceparent_middle}")
        instrumentor.force_flush()


@pytest.mark.usefixtures("mock_settings_console_env_vars")
def test_client_api_injects_traces(run_otlp_process: Callable[[Callable[[pathlib.Path], None]], list[dict[str, Any]]]):
    """Test that the Client's internal http client injects traces into requests."""
    # ACT
    otlp_content = run_otlp_process(sample_client_api_code)

    # ASSERT
    parent_span = _find_span_in_otlp(otlp_content, "PARENT CLIENT API", {})
    assert parent_span
    assert not parent_span["parent_id"]
    parent_trace_id = parent_span["context"]["trace_id"]
    parent_span_id = parent_span["context"]["span_id"]

    expected_trace_parent = f"{parent_trace_id[2:]}-{parent_span_id[2:]}"
    assert _find_log_in_otlp(otlp_content, f"request-header-traceparent: {expected_trace_parent}", "INFO")


def sample_run_metrics_middleware(output_file: pathlib.Path):
    # Small snippet executed in a different process, to avoid many issues due to trying to run this instrumented code
    # with all the leaks from other tests that also use instrumented-code, even if it's partially mocked.
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from ansys.saf.glow._telemetry.metrics_middleware import MetricsMiddleware

    with output_file.open("w") as output, mock.patch("sys.stderr", output):
        instrumentor = Instrumentor.instrumentalize_process("TEST", Settings.model_validate({}))
        app = FastAPI()

        @app.get("/projects")
        async def get_projects():  # type: ignore
            logging.getLogger("ansys").info("hello")

        FastAPIInstrumentor.instrument_app(app)  # type: ignore
        app.add_middleware(MetricsMiddleware, app_name=instrumentor.name, meter=instrumentor.meter)

        with TestClient(app) as test_client:
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span("PARENT HTTP REQUEST"):
                test_client.get("/projects").raise_for_status()
        instrumentor.force_flush()


@pytest.mark.usefixtures("mock_settings_console_env_vars")
def test_metrics_middleware_continues_trace(
    run_otlp_process: Callable[[Callable[[pathlib.Path], None]], list[dict[str, Any]]],
):
    """Test that MetricsMiddleware does not interrupt the trace in the HTTP request."""
    # ACT
    otlp_content = run_otlp_process(sample_run_metrics_middleware)

    # ASSERT
    parent_span = _find_span_in_otlp(otlp_content, "PARENT HTTP REQUEST", {})
    assert parent_span
    assert not parent_span["parent_id"]
    parent_trace_id = parent_span["context"]["trace_id"]
    parent_span_id = parent_span["context"]["span_id"]

    request_span = _find_span_in_otlp(otlp_content, "GET /projects")
    assert request_span
    assert request_span["parent_id"] == parent_span_id
    assert request_span["context"]["trace_id"] == parent_trace_id
    request_span_id = request_span["context"]["span_id"]

    log_line = _find_log_in_otlp(otlp_content, "hello", "INFO")
    assert log_line
    assert log_line["trace_id"] == parent_trace_id
    assert log_line["span_id"] == request_span_id
