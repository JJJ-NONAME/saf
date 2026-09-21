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

# ©2024, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""This module contains the logic for the table example."""

from typing import Any

import numpy as np


def generate_table_data(points: int = 30) -> dict[str, Any]:
    """Compute the data for the table."""
    t = np.linspace(-6, 6, points)
    x_s = 10 * np.sin(9.9 * t) * np.round(np.sqrt(np.cos(np.cos(10 * t))))
    y_s = 9 * np.cos(9.9 * t) ** 2 * np.sin(np.sin(10 * t))
    x, y = np.empty(0), np.empty(0)
    for alpha in np.linspace(0, 360, 6):
        alpha = np.radians(alpha)
        x = np.append(x, x_s * np.cos(alpha) + y_s * np.sin(alpha), axis=0)
        y = np.append(y, -x_s * np.sin(alpha) + y_s * np.cos(alpha), axis=0)
    d = np.sqrt(x**2 + y**2)
    data_dict = {"x_coords": x.tolist(), "y_coords": y.tolist(), "distance": d.tolist()}
    return data_dict
