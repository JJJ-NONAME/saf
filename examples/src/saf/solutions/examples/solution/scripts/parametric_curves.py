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

# ©2023, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.
"""Module for computing parametric curves."""
import numpy as np


def compute_curve(a: float, b: float, c: float, d: float, j: float, k: float) -> tuple[list[float], list[float]]:
    """Compute a parametric curve."""
    t = np.linspace(0, 2 * np.pi, 10000)
    x = 200 * (np.cos(a * t) - np.cos(b * t) ** j)
    y = 200 * (np.sin(c * t) - np.sin(d * t) ** k)

    return x.tolist(), y.tolist()


def compute_rd_curve(model: str, points: int = 10000) -> tuple[list[float], list[float], list[float]]:
    """
    Compute a parametric curve based on the model.

    Windmill: https://www.pinterest.co.uk/pin/339458890637961859/
    Flower: https://www.pinterest.co.uk/pin/115123334204984391/visual-search/?x=16&y=16&w=532&h=423.
    """
    if model == "windmill":
        t = np.linspace(-6, 6, points)
        x_s = 10 * np.sin(9.9 * t) * np.round(np.sqrt(np.cos(np.cos(10 * t))))
        y_s = 9 * np.cos(9.9 * t) ** 2 * np.sin(np.sin(10 * t))
        x, y = np.empty(0), np.empty(0)
        for alpha in np.linspace(0, 360, 6):
            alpha = np.radians(alpha)
            x = np.append(x, x_s * np.cos(alpha) + y_s * np.sin(alpha), axis=0)
            y = np.append(y, -x_s * np.sin(alpha) + y_s * np.cos(alpha), axis=0)
        d = np.sqrt(x**2 + y**2)
    elif model == "flower":
        t = np.linspace(-2.5, 2.5, points)
        x_s = 3 * np.cos(np.cos(7.32 * np.round(t))) * 1.2 * (1 + np.cos(16.6 * t))
        y_s = 3 * np.sin(16.6 * t) ** 2 * np.sin(7.32 * t)
        x, y = np.empty(0), np.empty(0)
        for alpha in np.linspace(0, 360, 10):
            alpha = np.radians(alpha)
            x = np.append(x, x_s * np.cos(alpha) + y_s * np.sin(alpha), axis=0)
            y = np.append(y, -x_s * np.sin(alpha) + y_s * np.cos(alpha), axis=0)
        d = np.sqrt(x**2 + y**2)
    elif model == "vegas":
        t = np.linspace(-0.2, 6.2, points)
        x_s = 10 * np.sin(2.78 * t) * np.round(np.sqrt(np.cos(np.cos(8.2 * t))))
        y_s = 9 * np.cos(2.78 * t) ** 2 * np.sin(np.sin(8.2 * t))
        x, y = np.empty(0), np.empty(0)
        for alpha in np.linspace(0, 360, 20):
            alpha = np.radians(alpha)
            x = np.append(x, x_s * np.cos(alpha) + y_s * np.sin(alpha), axis=0)
            y = np.append(y, -x_s * np.sin(alpha) + y_s * np.cos(alpha), axis=0)
        d = np.sqrt(x**2 + y**2)
    else:
        raise ValueError(f"Unknown model {model}.")

    return x.tolist(), y.tolist(), d.tolist()
