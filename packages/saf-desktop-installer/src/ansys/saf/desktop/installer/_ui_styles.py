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

"""Styles and styling utilities for the installer UI."""

from typing import Any

LONG_PATH_WARNING_HIDDEN_STYLE: dict[str, Any] = {"display": "none"}
LONG_PATH_WARNING_SHOWN_STYLE: dict[str, Any] = {
    "display": "flex",
    "width": "100%",
    "align-items": "flex-start",
    "color": "#856404",
    "background-color": "#fff3cd",
    "border": "1px solid #ffc107",
    "border-radius": "4px",
    "padding": "8px 12px",
    "margin-bottom": "8px",
    "font-size": "13px",
    "font-style": "italic",
}
PREREQUISITES_NOT_FULFILLED_MSG_STYLE_BASE: dict[str, Any] = {
    "color": "red",
    "font-size": "14px",
    "text-align": "center",
    "padding-top": "6px",
    "font-style": "italic",
}


def install_button_style(disabled: bool = False) -> dict[str, Any]:
    """Return the inline style dict for the Install button based on its disabled state.

    Parameters
    ----------
    disabled : bool
        Whether the button is disabled.

    Returns
    -------
    dict[str, Any]
        Style dictionary for the Install button.
    """
    color = "#000000" if not disabled else "#d9d9d9"
    return {
        "width": "100%",
        "background-color": color,
        "color": "white",
        "border-radius": "2px",
        "border": f"2px solid {color}",
        "pointer-events": "auto" if not disabled else "none",
        "cursor": "pointer" if not disabled else "not-allowed",
    }
