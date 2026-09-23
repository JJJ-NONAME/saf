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
Performance testing utilities for comparing web-component vs Dash component approaches.

This module provides tools to measure:
- Bundle sizes and build times
- Core Web Vitals (LCP, TBT, CLS)
- Memory usage and potential leaks
- Network efficiency and callback patterns
- Re-render counts and optimization effectiveness

Usage:
    from tests.performance import bundle_analyzer, web_vitals, memory_profiler
    from tests.performance.report_generator import generate_report
"""

from .bundle_analyzer import (
    BundleAnalysis,
    BundleMetrics,
    analyze_bundle,
    analyze_dash_component,
    compare_bundle_analyses,
    compare_bundles,
)
from .memory_profiler import MemoryProfile, MemorySnapshot, compare_memory_profiles, profile_memory, sync_profile_memory
from .report_generator import PerformanceComparison, generate_report
from .web_vitals import (
    WebVitalsAnalysis,
    WebVitalsMetrics,
    compare_web_vitals,
    measure_web_vitals,
    run_web_vitals_benchmark,
    sync_run_benchmark,
)

__all__ = [
    # Bundle analysis
    "BundleMetrics",
    "BundleAnalysis",
    "analyze_bundle",
    "analyze_dash_component",
    "compare_bundles",
    "compare_bundle_analyses",
    # Web Vitals
    "WebVitalsMetrics",
    "WebVitalsAnalysis",
    "measure_web_vitals",
    "run_web_vitals_benchmark",
    "compare_web_vitals",
    "sync_run_benchmark",
    # Memory profiling
    "MemorySnapshot",
    "MemoryProfile",
    "profile_memory",
    "compare_memory_profiles",
    "sync_profile_memory",
    # Report generation
    "PerformanceComparison",
    "generate_report",
]
