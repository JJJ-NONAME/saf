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

from ansys.saf.testing._common.common import has_modules_installed

__all__ = []

if has_modules_installed(["selenium"]):
    from ansys.saf.testing._frontend.selenium import (
        DEFAULT_IMPLICIT_WAIT,
        DEFAULT_TIMEOUT,
        chrome_options,
        get_selenium_webdriver,
        move_to_element,
        selenium_webdriver,
        session_selenium_webdriver,
        wait_for_element,
        wait_for_element_and_click,
        wait_for_element_and_send_text,
        wait_for_element_to_be_clickable,
        wait_for_expected_attribute,
        wait_for_expected_property,
        wait_for_partial_text,
        wait_for_text,
        wait_for_text_to_be_different,
    )

    __all__ += [  # pyright: ignore[reportUnknownVariableType]
        "DEFAULT_IMPLICIT_WAIT",
        "DEFAULT_TIMEOUT",
        "chrome_options",
        "session_selenium_webdriver",
        "selenium_webdriver",
        "get_selenium_webdriver",
        "wait_for_expected_attribute",
        "wait_for_expected_property",
        "wait_for_text",
        "wait_for_text_to_be_different",
        "wait_for_element",
        "wait_for_partial_text",
        "wait_for_element_to_be_clickable",
        "wait_for_element_and_click",
        "wait_for_element_and_send_text",
        "move_to_element",
    ]
