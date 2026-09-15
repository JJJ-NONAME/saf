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


"""Logs parser utility."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
import re
from urllib.parse import urlparse

import pandas as pd
import requests
from requests.exceptions import HTTPError


class ParseStatus(StrEnum):
    """Status of parsing logs."""

    SUCCESS_WITH_ROWS = "success_with_rows"
    SUCCESS_EMPTY_FILE = "success_empty_file"
    SUCCESS_NO_MATCHING_ROWS = "success_no_matching_rows"
    SOURCE_MISSING = "source_missing"
    FAILURE = "failure"


PARSE_ERROR_MESSAGES = {
    ParseStatus.SUCCESS_NO_MATCHING_ROWS: "No matching rows found.",
    ParseStatus.SOURCE_MISSING: "Log source is not available.",
}


@dataclass
class LogsParseResult:
    """Result of parsing logs with explicit status and optional error information."""

    status: ParseStatus
    data: pd.DataFrame
    error: str | None = None


class LogsParser:
    """
    Parse a log source and return structured results with explicit parse status.

    The log file should be generated using the Python logging module. This class
    parses such log content and returns a :class:`LogsParseResult` containing:

    - a parse status,
    - parsed rows as a pandas DataFrame,
    - optional error details for non-success states.

    Attributes
    ----------
    log_file : str or Path, required
        Path or URL to the log file to be parsed.
    log_format : str, required
        Format string of the log messages to be parsed.

    Methods
    -------
    parse_with_status():
        Parse logs and return a :class:`LogsParseResult` with status and data.
    """

    def __init__(self, log_file: Path | str, log_format: str):
        if not isinstance(log_file, str | Path):  # type: ignore - deliberately checking input type
            raise ValueError("log_file must be a string or Path object.")

        self.log_file = log_file
        self.log_format = log_format
        self.pattern, self.columns = self._generate_pattern_and_columns(log_format)

    def _read_log_file(self) -> str | None:
        """Read log content from URL or local path.

        Returns
        -------
        str or None
            File content when available. Returns ``None`` when the source is missing
            (for example a missing local file or an HTTP 404 response).
        """
        if url := self._url():
            response = requests.get(url, timeout=10)
            try:
                response.raise_for_status()
            except HTTPError as ex:
                status_code = ex.response.status_code if ex.response is not None else None
                if status_code == 404:  # File might be created later, so don't raise an exception
                    return None
                raise
            return response.text

        # Convert to Path object - works whether input is str or Path
        log_file = Path(self.log_file)
        if log_file.exists():
            return log_file.read_text()

        # File does not exist
        return None

    def parse_with_status(self) -> LogsParseResult:
        """Parse logs and return status, parsed rows, and optional error details.

        Returns
        -------
        LogsParseResult
            Parsing outcome with one of the :class:`ParseStatus` values:

            - ``SUCCESS_WITH_ROWS`` when rows are parsed.
            - ``SUCCESS_EMPTY_FILE`` when the source exists but is empty.
            - ``SUCCESS_NO_MATCHING_ROWS`` when no lines match ``log_format``.
            - ``SOURCE_MISSING`` when the source is not available.
            - ``FAILURE`` for unexpected read/parse errors.
        """
        try:
            content = self._read_log_file()
        except Exception as ex:
            return LogsParseResult(
                status=ParseStatus.FAILURE,
                data=pd.DataFrame(),
                error=self._format_exception_title(ex),
            )

        if content is None:
            return LogsParseResult(
                status=ParseStatus.SOURCE_MISSING,
                data=pd.DataFrame(),
                error=PARSE_ERROR_MESSAGES[ParseStatus.SOURCE_MISSING],
            )

        if content == "":
            return LogsParseResult(
                status=ParseStatus.SUCCESS_EMPTY_FILE,
                data=pd.DataFrame(),
            )

        data: list[dict[str, str]] = []
        for line in content.splitlines():
            match = re.match(self.pattern, line)
            if match:
                data.append(match.groupdict())

        if not data:
            return LogsParseResult(
                status=ParseStatus.SUCCESS_NO_MATCHING_ROWS,
                data=pd.DataFrame(),
                error=PARSE_ERROR_MESSAGES[ParseStatus.SUCCESS_NO_MATCHING_ROWS],
            )

        return LogsParseResult(
            status=ParseStatus.SUCCESS_WITH_ROWS,
            data=pd.DataFrame(data, columns=self.columns),  # type: ignore - pandas typing issue (pandas issue 56995)
        )

    def _url(self) -> str | None:
        """Check if the log file path is a URL."""
        if not isinstance(self.log_file, str):
            return None

        result = urlparse(self.log_file)
        return self.log_file if (result.scheme and result.netloc) else None

    def _generate_pattern_and_columns(self, log_format: str) -> tuple[str, list[str]]:
        """
        Generate a regex pattern and a list of columns based on the log format string.

        Parameters
        ----------
        log_format : str
            Format string of the log messages to be parsed.

        Returns
        -------
        tuple: A tuple containing the regex pattern and the list of columns.
        """
        format_mappings = {
            "%(asctime)s": r"(?P<asctime>[\d-]+\s[\d:,]+)",
            "%(created)f": r"(?P<created>[\d.]+)",
            "%(filename)s": r"(?P<filename>[\w.\-]+)",
            "%(funcName)s": r"(?P<funcName>[\w.]+)",
            "%(levelname)s": r"(?P<levelname>\w+)",
            "%(levelno)d": r"(?P<levelno>\d+)",
            "%(lineno)d": r"(?P<lineno>\d+)",
            "%(message)s": r"(?P<message>.+)",
            "%(module)s": r"(?P<module>[\w.]+)",
            "%(msecs)d": r"(?P<msecs>\d+)",
            "%(name)s": r"(?P<name>[\w.]+)",
            "%(pathname)s": r"(?P<pathname>[\w.:/\\\-]+)",
            "%(process)d": r"(?P<process>\d+)",
            "%(processName)s": r"(?P<processName>[\w.\-:]+)",
            "%(relativeCreated)d": r"(?P<relativeCreated>[\d.]+)",
            "%(thread)d": r"(?P<thread>\d+)",
            "%(threadName)s": r"(?P<threadName>[\w.]+)",
            # taskName is supported in Python 3.12+ - adding for completeness
            "%(taskName)s": r"(?P<taskName>[\w.]+)",
        }

        regex_pattern = re.escape(log_format)
        columns: list[str] = []

        # Find all placeholders in the log_format in order of appearance
        placeholder_pattern = r"%\(([^)]+)\)[sdf]"
        for match in re.finditer(placeholder_pattern, log_format):
            field_name = match.group(1)
            placeholder = match.group(0)

            # Replace the placeholder with its corresponding regex if it exists in mappings
            if placeholder in format_mappings:
                regex = format_mappings[placeholder]
                regex_pattern = regex_pattern.replace(re.escape(placeholder), regex)
                columns.append(field_name)

        return regex_pattern, columns

    @staticmethod
    def _format_exception_title(ex: Exception) -> str:
        # Rich, structured title for HTTP errors
        if isinstance(ex, HTTPError) and ex.response is not None:
            status = ex.response.status_code
            reason = ex.response.reason or "Unknown Reason"

            # 1xx..5xx category label similar to requests wording
            family = status // 100
            family_label = {
                1: "Informational",
                2: "Success",
                3: "Redirection",
                4: "Client Error",
                5: "Server Error",
            }.get(family, "HTTP Error")

            # Example: "500 Server Error: Internal Server Error"
            return f"{status} {family_label}: {reason}."

        # Generic fallback for non-HTTP exceptions
        return f"{ex.__class__.__module__}.{ex.__class__.__name__}."
