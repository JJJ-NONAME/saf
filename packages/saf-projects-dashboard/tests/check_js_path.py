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

"""Check where Dash looks for JS files."""

import os

import ansys_saf_projects_dashboard

# Check where Dash would look for JS files
print("ansys_saf_projects_dashboard.__file__:", ansys_saf_projects_dashboard.__file__)
print()

# The _js_dist path is relative to the module that defines _js_dist
# Since we import from .ansys_saf_projects_dashboard, let's check where that is
import ansys_saf_projects_dashboard.ansys_saf_projects_dashboard as inner

print("inner.__file__:", inner.__file__)
print()

# Check if JS exists relative to inner module
inner_dir = os.path.dirname(inner.__file__)
js_path = os.path.join(inner_dir, "ansys_saf_projects_dashboard.js")
print("JS expected at:", js_path)
print("JS exists:", os.path.exists(js_path))
