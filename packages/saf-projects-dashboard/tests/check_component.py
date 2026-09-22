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

"""Minimal test to verify ansys_saf_projects_dashboard component works with Dash."""

import ansys_saf_projects_dashboard

# Print component info
print(f"Package name: {ansys_saf_projects_dashboard.package_name}")
print(f"Version: {ansys_saf_projects_dashboard.__version__}")

# Check the component class
comp = ansys_saf_projects_dashboard.ProjectsDashboard
print(f"\nComponent: {comp}")
print(f"Component _type: {getattr(comp, '_type', 'N/A')}")
print(f"Component _namespace: {getattr(comp, '_namespace', 'N/A')}")

# Check _js_dist
js_dist = getattr(comp, "_js_dist", [])
print(f"\n_js_dist entries: {len(js_dist)}")
for entry in js_dist:
    print(f"  - {entry}")

# Try creating an instance
instance = ansys_saf_projects_dashboard.ProjectsDashboard(id="test-dashboard")
print(f"\nCreated instance: {instance}")
print(f"Instance type: {instance.type if hasattr(instance, 'type') else 'N/A'}")
print(f"Instance to_plotly_json: {instance.to_plotly_json()}")
