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

"""
Run performance tests for the web-component approach.
"""

import gzip
from pathlib import Path
import sys
import time

WEB_COMPONENT_URL = "http://127.0.0.1:5433/projects/6980c39c924613b4604bac3e"


def get_gzipped_size(file_path):
    """Calculate gzipped size of a file."""
    with open(file_path, "rb") as f:
        content = f.read()
    return len(gzip.compress(content, compresslevel=9))


def analyze_web_component_bundle():
    """Analyze the web-component bundle."""
    web_component_dir = Path("src/ansys/solutions/dashboard/ui/assets/dashboard-app")
    files = []

    for f in web_component_dir.glob("*"):
        if f.is_file() and f.suffix in [".js", ".css"]:
            size = f.stat().st_size
            gzipped = get_gzipped_size(f)
            files.append((f.name, size, gzipped, f.suffix))

    total_size = sum(f[1] for f in files)
    total_gzipped = sum(f[2] for f in files)
    js_size = sum(f[1] for f in files if f[3] == ".js")
    css_size = sum(f[1] for f in files if f[3] == ".css")

    print("=" * 50)
    print("Web Component Bundle Analysis")
    print("=" * 50)
    print(f"Total Size: {total_size / 1024:.2f} KB")
    print(f"Gzipped:    {total_gzipped / 1024:.2f} KB")
    print(f"JS Size:    {js_size / 1024:.2f} KB")
    print(f"CSS Size:   {css_size / 1024:.2f} KB")
    for f in files:
        print(f"  - {f[0]}: {f[1] / 1024:.2f} KB ({f[2] / 1024:.2f} KB gzipped)")
    print("=" * 50)

    return {
        "total_kb": total_size / 1024,
        "gzipped_kb": total_gzipped / 1024,
        "js_kb": js_size / 1024,
        "css_kb": css_size / 1024,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Performance Tests for Web-Component Approach")
    print(f"URL: {WEB_COMPONENT_URL}")
    print("=" * 60)

    # Bundle analysis only (Web Vitals and Memory are run via pytest)
    bundle = analyze_web_component_bundle()

    print("\n" + "=" * 60)
    print("BUNDLE SUMMARY")
    print("=" * 60)
    print(f"Total Size: {bundle['total_kb']:.2f} KB")
    print(f"Gzipped:    {bundle['gzipped_kb']:.2f} KB")
    print(f"JS Size:    {bundle['js_kb']:.2f} KB")
    print(f"CSS Size:   {bundle['css_kb']:.2f} KB")
    print("=" * 60)
    print("\nTo run Web Vitals and Memory tests, use:")
    print(f'  $env:BENCHMARK_URL="{WEB_COMPONENT_URL}"')
    print("  pytest tests/performance/test_performance.py::TestWebVitals -v -s")
    print("  pytest tests/performance/test_performance.py::TestMemoryProfile -v -s")
