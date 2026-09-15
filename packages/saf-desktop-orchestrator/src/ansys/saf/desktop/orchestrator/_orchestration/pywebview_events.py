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

import ctypes
from ctypes import wintypes
import importlib
import logging
from pathlib import Path
import platform

from webview import Window

logger = logging.getLogger(__name__)


def _get_pywebview_icon_path(solution_main_module_name: str) -> Path | None:
    """Check for the presence of a custom icon for pywebview in the solution UI assets.

    Given a solution main module name that points to <solution_root>/main.py, the icon is expected to be located at
    <solution_root>/ui/assets/pywebview/favicon.ico."""
    module = importlib.import_module(solution_main_module_name)
    module_file = module.__file__
    if not module_file:
        return None
    icon_path = Path(module_file).parent / "ui" / "assets" / "pywebview" / "favicon.ico"
    if icon_path.is_file():
        return icon_path
    return None


def set_custom_pywebview_icon(window: Window, solution_main_module_name: str) -> bool:
    """Event handler fired before the pywebview window is shown — sets the icon."""
    if platform.system() != "Windows":
        return False

    icon_path = _get_pywebview_icon_path(solution_main_module_name)
    if not icon_path:
        return False

    try:
        user32 = ctypes.windll.user32  # type: ignore
        # get a handle to the pywebview window
        hwnd = wintypes.HWND(window.native.Handle.ToInt64())  # type: ignore

        icon = user32.LoadImageW(None, icon_path.as_posix(), 1, 0, 0, 0x00000010)  # type: ignore

        # Use WM_SETICON message to set both small (title bar) and big icons (taskbar) for the window
        icon_small = 0
        icon_big = 1
        wm_seticon = 0x0080
        ctypes.windll.user32.SendMessageW(hwnd, wm_seticon, icon_small, icon)  # type: ignore
        ctypes.windll.user32.SendMessageW(hwnd, wm_seticon, icon_big, icon)  # type: ignore

        logger.debug(f"Set custom icon for pywebview from {icon_path}")
        return True
    except Exception as e:
        logger.warning(f"Failed to set custom icon for pywebview: {e}")
        return False
