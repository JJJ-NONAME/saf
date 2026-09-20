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

"""
Business logic computing the transcendental butterfly curve.

The butterfly curve is a plane curve discovered by Temple H. Fay. It is described at
https://en.wikipedia.org/wiki/Butterfly_curve_(transcendental).

This module is plain Python: it has no dependency on SAF and can be used and tested on
its own.
"""

import numpy as np


def compute_butterfly_curve(
    wing_frequency: float = 4.0,
    wing_amplitude: float = 2.0,
    twist: float = 12.0,
    exponent: int = 5,
    revolutions: float = 12.0,
    points: int = 10000,
) -> tuple[list[float], list[float], list[float]]:
    """
    Compute the coordinates of the transcendental butterfly curve.

    The curve is defined in polar-like form by

    .. math::

        r(t) = e^{\\cos t} - a \\cos(f t) - \\sin^{n}(t / \\tau)

    with :math:`x = r(t) \\sin t` and :math:`y = r(t) \\cos t`, where :math:`a` is the wing
    amplitude, :math:`f` the wing frequency, :math:`n` the exponent and :math:`\\tau` the
    twist. The default values reproduce the curve described at
    https://en.wikipedia.org/wiki/Butterfly_curve_(transcendental).

    Parameters
    ----------
    wing_frequency : float, default: 4.0
        Frequency of the cosine term that shapes the wings. Higher values add wings.
    wing_amplitude : float, default: 2.0
        Amplitude of the cosine term that shapes the wings. A value of ``0`` removes them.
    twist : float, default: 12.0
        Divider of the parameter in the sine term that twists the wings. It cannot be zero.
    exponent : int, default: 5
        Exponent applied to the sine term. An integer is required because the sine term
        takes negative values.
    revolutions : float, default: 12.0
        Number of half-turns to draw. The parameter ``t`` spans ``[0, revolutions * pi]``.
        The curve is closed for even values.
    points : int, default: 10000
        Number of points used to discretize the curve.

    Returns
    -------
    tuple[list[float], list[float], list[float]]
        Three lists of ``points`` values:

        - the ``x`` coordinates of the curve,
        - the ``y`` coordinates of the curve,
        - the distance of each point to the origin, that is ``sqrt(x ** 2 + y ** 2)``.

    Raises
    ------
    ValueError
        If ``twist`` is zero or if ``exponent`` is not an integer.

    Examples
    --------
    >>> x, y, distance = compute_butterfly_curve(points=5)
    >>> len(x), len(y), len(distance)
    (5, 5, 5)
    """
    if twist == 0:
        raise ValueError("The twist parameter cannot be zero.")
    if exponent != int(exponent):
        raise ValueError("The exponent parameter must be an integer.")

    t = np.linspace(0, revolutions * np.pi, points)
    r = np.exp(np.cos(t)) - wing_amplitude * np.cos(wing_frequency * t) - np.sin(t / twist) ** int(exponent)
    x = r * np.sin(t)
    y = r * np.cos(t)

    return x.tolist(), y.tolist(), np.abs(r).tolist()
