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

"""Check how Dash and DashProxy register component resources."""

from dash import Dash, html
from dash_extensions.enrich import DashProxy, MultiplexerTransform, NoOutputTransform, TriggerTransform

import ansys_saf_projects_dashboard

# Test 1: Standard Dash
print("=== Standard Dash ===")
app1 = Dash(__name__)
app1.layout = html.Div([ansys_saf_projects_dashboard.ProjectsDashboard(id="test")])

with app1.server.test_request_context():
    html_content = app1.index()
    if "ansys_saf_projects_dashboard" in html_content:
        print("  FOUND ansys_saf_projects_dashboard in HTML")
    else:
        print("  NOT FOUND in HTML")

# Test 2: DashProxy
print("\n=== DashProxy ===")
app2 = DashProxy(
    __name__,
    serve_locally=True,
    suppress_callback_exceptions=True,
    transforms=[NoOutputTransform(), TriggerTransform(), MultiplexerTransform()],
)
app2.layout = html.Div([ansys_saf_projects_dashboard.ProjectsDashboard(id="test")])

with app2.server.test_request_context():
    html_content = app2.index()
    if "ansys_saf_projects_dashboard" in html_content:
        print("  FOUND ansys_saf_projects_dashboard in HTML")
        import re

        scripts = re.findall(r'<script[^>]*src="[^"]*ansys_saf_projects_dashboard[^"]*"[^>]*>', html_content)
        for s in scripts:
            print(f"  {s}")
    else:
        print("  NOT FOUND in HTML")

# Check get_dist for DashProxy
print("\nget_dist for DashProxy:")
try:
    dist = app2.get_dist("ansys_saf_projects_dashboard")
    print(f"  {dist}")
except Exception as e:
    print(f"  Error: {e}")
