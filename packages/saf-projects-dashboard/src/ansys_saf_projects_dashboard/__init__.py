# ruff: noqa
# Copyright (C) 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ruff: noqa
from __future__ import print_function as _

import json
from pathlib import Path
import sys as _sys

import dash as _dash

# noinspection PyUnresolvedReferences
from ._imports_ import *  # noqa: F403
from ._imports_ import __all__

if not hasattr(_dash, "__plotly_dash") and not hasattr(_dash, "development"):
    print(
        "Dash was not successfully imported. "
        "Make sure you don't have a file "
        'named \n"dash.py" in your current directory.',
        file=_sys.stderr,
    )
    _sys.exit(1)

_filepath = Path(__file__).parent / "package-info.json"
with _filepath.open() as f:
    package = json.load(f)

__version__ = package["version"]
package_name = package["name"].replace(" ", "_").replace("-", "_")

_dash_namespace = "ansys_saf_projects_dashboard"

_js_dist = []

_js_dist.extend(
    [
        {"relative_package_path": "ansys_saf_projects_dashboard.js", "namespace": _dash_namespace},
        {"relative_package_path": "ansys_saf_projects_dashboard.js.map", "namespace": _dash_namespace, "dynamic": True},
    ],
)

# Add proptypes.js for runtime prop types validation with tsx components
_js_dist.append({"relative_package_path": "proptypes.js", "dev_only": True, "namespace": _dash_namespace})

_css_dist = []


for _component in __all__:
    setattr(locals()[_component], "_js_dist", _js_dist)  # noqa: B010
    setattr(locals()[_component], "_css_dist", _css_dist)  # noqa: B010
