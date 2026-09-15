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

"""Check the examples solution through a real Chrome browser."""

import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver

from tests.e2e.conftest import (
    BrowserDiagnostics,
    RunningExamples,
    clear_browser_logs,
    collect_browser_diagnostics,
    discover_navigation_pages,
    navigate_to_discovered_page,
    wait_for_page_rendered,
)


def _assert_no_browser_failures(page_url: str, diagnostics: BrowserDiagnostics) -> None:
    """Fail with one readable report of console and network diagnostics."""
    failures = _get_browser_failure_messages(diagnostics)
    assert not failures, f"Browser failures while loading {page_url}:\n" + "\n".join(failures)


def _get_browser_failure_messages(diagnostics: BrowserDiagnostics) -> list[str]:
    """Return readable browser failure messages without raising an assertion."""
    failures = [
        *(f"console: {message}" for message in diagnostics.console_errors),
        *(f"network: {message}" for message in diagnostics.network_failures),
    ]
    return failures


def test_solution_ui_is_accessible_in_browser(
    running_examples: RunningExamples,
    examples_webdriver: WebDriver,
) -> None:
    """Verify the shortcut-launched solution renders its initial project page.

    The test opens the project page, waits for Dash to render it, and checks
    that no browser console errors or failed network requests were recorded.
    """
    clear_browser_logs(examples_webdriver)
    examples_webdriver.get(running_examples.project_ui_url)
    wait_for_page_rendered(examples_webdriver)
    diagnostics = collect_browser_diagnostics(examples_webdriver)
    _assert_no_browser_failures(running_examples.project_ui_url, diagnostics)


def test_discovered_pages_render_without_browser_failures(
    running_examples: RunningExamples,
    examples_webdriver: WebDriver,
) -> None:
    """Verify every page exposed by the solution renders without browser failures.

    The navigation tree is read at runtime, so this test does not need a list of
    routes, labels, headings, or navigation groups for a particular solution.
    """
    try:
        discovered_pages = discover_navigation_pages(
            examples_webdriver,
            running_examples.project_ui_url,
        )
    except (RuntimeError, WebDriverException) as exc:
        pytest.fail(f"Unable to discover solution pages: {exc}")

    page_failures: list[str] = []
    for page in discovered_pages:
        try:
            page_url = navigate_to_discovered_page(
                examples_webdriver,
                running_examples,
                page,
            )
        except WebDriverException as exc:
            page_failures.append(f"Unable to render {page.navigation_label!r}: {exc}")
            continue

        diagnostics = collect_browser_diagnostics(examples_webdriver)
        browser_failures = _get_browser_failure_messages(diagnostics)
        if browser_failures:
            page_failures.append(
                f"Browser failures while loading {page_url}:\n" + "\n".join(browser_failures),
            )

    assert not page_failures, "Failures occurred while checking discovered pages:\n" + "\n\n".join(page_failures)
