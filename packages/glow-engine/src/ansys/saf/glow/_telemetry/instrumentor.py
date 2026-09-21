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

import importlib.metadata
import json
import logging
import logging.config
import os
import sys
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider  # pyright: ignore[reportMissingTypeStubs]
from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor  # pyright: ignore[reportMissingTypeStubs]
from opentelemetry.instrumentation.logging.handler import LoggingHandler  # pyright: ignore[reportMissingTypeStubs]
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs._internal.export import ConsoleLogRecordExporter
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.export import ConsoleMetricExporter, MetricReader
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from ansys.saf.glow._config.const import GLOW_API_SERVICE_NAME, GLOW_UI_SERVICE_NAME
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._telemetry.config import (
    LOGGING_DEFAULT_CONFIG,
    create_logging_config,
    get_log_file_paths_from_config,
)

logger = logging.getLogger(__name__)


class Instrumentor:
    """Utility class used to instrument, generate, collect and export telemetry data (metrics, logs and traces).
    The Instrumentor takes care of creating the tracer, logger and meter automatically, thus avoiding the user to take
    care about the order in which they must be done.
    """

    _instance = None

    def __new__(cls, *args: Any, **kwargs: Any):
        raise RuntimeError("Direct instantiation is not allowed. Use Instrumentor.instrumentalize_process().")

    @classmethod
    def instrumentalize_process(
        cls,
        name: str,
        settings: Settings,
        method_name: str = "",
    ) -> "Instrumentor":
        """The Instrumentor should only be instantiated once per process.
        - API server
        - ProcessMethodRunner (long running transaction)
        - UI server
        - Dash background callback.
        """
        if not cls._instance:
            instance = super().__new__(cls)
            instance._initialize(name, settings, method_name)

            # Tracing should be configured before logging, otherwise the otelServiceName field in logging is empty.
            instance._configure_tracing()
            instance._configure_logging()
            instance._configure_metrics()

            cls._instance = instance

        return cls._instance

    def _initialize(self, name: str, settings: Settings, method_name: str) -> None:
        self._name = name
        self._settings = settings
        self._method_name = method_name

        self._trace_provider = None
        self._logger_provider = None
        self._metric_provider = None
        self._log_config = None
        self._log_level = (
            logging.DEBUG
            if self._settings.glow_debug
            else (
                logging.getLevelName(self._settings.glow_logging_level.value)  # pyright: ignore[reportDeprecated]
                if self._settings.glow_logging_level
                else logging.INFO
            )
        )
        self._resource = Resource.create(
            {
                SERVICE_NAME: self._name,
                SERVICE_VERSION: importlib.metadata.version("ansys-saf-glow-engine"),
                SERVICE_NAMESPACE: "ansys.saf.glow",
            },
        )

    @property
    def name(self):
        return self._name

    @property
    def tracer(self):
        return self._tracer

    @property
    def log_config(self):
        return self._log_config

    @property
    def meter(self):
        return self._meter

    @property
    def span(self):
        return trace.get_current_span()

    def _configure_tracing(self) -> None:
        self._trace_provider = TracerProvider(resource=self._resource)
        trace.set_tracer_provider(self._trace_provider)

        if self._settings.otel_exporter_otlp_endpoint:
            trace_exporter = (
                OTLPSpanExporter()  # default using OTEL_EXPORTER_OTLP_ENDPOINT env var
                if self._settings.otel_exporter_otlp_endpoint.startswith("http")
                else ConsoleSpanExporter(out=sys.stderr)
            )
            trace_processor = BatchSpanProcessor(trace_exporter)
            self._trace_provider.add_span_processor(trace_processor)

        self._tracer = trace.get_tracer(self._name)

    def _configure_logging(self) -> None:
        # Inject { otelSpanID | otelTraceID | otelServiceName | otelTraceSampled } attributes and resource into logging
        LoggingInstrumentor().instrument(set_logging_format=True)  # type: ignore

        # We load the default config, even if the user has specified a custom config file or
        # there is one saved in log_config_var_name.
        # This means that user configurations are complementary, and they don't need to configure all loggers.
        logging.config.dictConfig(LOGGING_DEFAULT_CONFIG)

        log_config_var_name = f"{self._name.replace(' ', '_')}_INTERNAL_LOG_CONFIG"
        if self._settings.otel_exporter_otlp_endpoint:
            logger.info(f"Telemetry enabled, using OTLP logging configuration for {self._name}")
            self._logger_provider = LoggerProvider(resource=self._resource)
            set_logger_provider(self._logger_provider)

            log_exporter = (
                OTLPLogExporter()  # default using OTEL_EXPORTER_OTLP_ENDPOINT env var
                if self._settings.otel_exporter_otlp_endpoint.startswith("http")
                else ConsoleLogRecordExporter(out=sys.stderr)
            )
            log_processor = BatchLogRecordProcessor(log_exporter)
            self._logger_provider.add_log_record_processor(log_processor)

            otlp_handler = LoggingHandler(level=self._log_level, logger_provider=self._logger_provider)
            # Careful, it's easy to end up in an infinite loop if destination is down (e.g., tests)
            # because it keeps retrying to export its own errors.
            # See https://github.com/open-telemetry/opentelemetry-python/issues/2701
            # Replace default handlers and configure the corresponding level for the loggers
            # (except root, like in create_logging_config())
            root_logger = logging.getLogger()
            for handler in root_logger.handlers:
                root_logger.removeHandler(handler)
            root_logger.addHandler(otlp_handler)
            ansys_logger = logging.getLogger("ansys")
            ansys_logger.setLevel(self._log_level)
            for handler in ansys_logger.handlers:
                ansys_logger.removeHandler(handler)
            ansys_logger.addHandler(otlp_handler)
        elif log_config_var_name in os.environ:
            # API/UI server was reloaded, load the custom configuration from the backup dump
            # this is done to avoid creating new log files if there are some random templating
            # (see _parse_config_from_file).
            # if we remove that part, we can remove this one too.
            logger.info(f"Reload detected, reusing existing logging configuration for {self._name}")
            self._log_config = json.loads(os.environ[log_config_var_name])
            if self._log_config:
                logging.config.dictConfig(self._log_config)
        else:
            # apply user configuration
            self._log_config = create_logging_config(self._name, self._settings, self._method_name)
            if self._log_config:
                if self._name in [GLOW_UI_SERVICE_NAME, GLOW_API_SERVICE_NAME]:
                    # We don't want Methods reusing logging configuration, and possibly, log files.
                    os.environ[log_config_var_name] = json.dumps(self._log_config)
                logger.info(f"Applied user logging configuration for {self._name}")
                log_files = get_log_file_paths_from_config(self._log_config)
                if log_files:
                    # do it before applying config. otherwise, the user will have to manually find where the log is
                    logger.info(f"{self._name} logging to {', '.join(log_files)}")
                logging.config.dictConfig(self._log_config)
            else:
                logger.info(f"Using default logging config for {self._name}")

    def _configure_metrics(self) -> None:
        metric_readers: list[MetricReader] = []

        if self._settings.otel_exporter_otlp_endpoint:
            metric_exporter = (
                OTLPMetricExporter()  # default using OTEL_EXPORTER_OTLP_ENDPOINT env var
                if self._settings.otel_exporter_otlp_endpoint.startswith("http")
                else ConsoleMetricExporter(out=sys.stderr)
            )
            metric_readers.append(PeriodicExportingMetricReader(metric_exporter))

        self._metric_provider = MeterProvider(metric_readers=metric_readers, resource=self._resource)
        metrics.set_meter_provider(self._metric_provider)
        self._meter = metrics.get_meter(self._name)

    def force_flush(self) -> None:
        if self._metric_provider is not None:
            self._metric_provider.force_flush()
        if self._logger_provider is not None:
            self._logger_provider.force_flush()
        if self._trace_provider is not None:
            self._trace_provider.force_flush()
