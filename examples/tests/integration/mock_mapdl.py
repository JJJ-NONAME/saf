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

"""Reusable MAPDL client mock for beam-bending integration tests."""

from pathlib import Path
from typing import Any

import numpy as np


class MockMapdlMesh:
    """Minimal MAPDL mesh representation used by the integration tests."""

    def __init__(self) -> None:
        self.nnum = np.arange(1, 6)
        self.nodes = np.empty((0, 3))


class MockMapdlPostProcessing:
    """Minimal post-processing API used by ``mapdl_model.PostProcess``."""

    def __init__(self, mapdl: "MockMapdlClient") -> None:
        self._mapdl = mapdl

    def nodal_displacement(self, _: str) -> np.ndarray:
        return np.zeros_like(self._mapdl.mesh.nodes)

    def plot_nodal_displacement(self, _: str, *, savefig: str, **__: Any) -> None:
        Path(savefig).write_bytes(b"nodal displacement")

    def plot_element_stress(self, _: str, __: str, *, savefig: str, **___: Any) -> None:
        Path(savefig).write_bytes(b"element stress")


class MockMapdlClient:
    """Small MAPDL client double for exercising the GLOW backend transactions."""

    def __init__(self) -> None:
        self.mesh = MockMapdlMesh()
        self.post_processing = MockMapdlPostProcessing(self)
        self.calls: list[str] = []
        self._nodes: list[list[float]] = []

    def prep7(self) -> None:
        self.calls.append("prep7")

    def et(self, *args: Any) -> None:
        self.calls.append("et")

    def keyopt(self, *args: Any) -> None:
        self.calls.append("keyopt")

    def mp(self, *args: Any) -> None:
        self.calls.append("mp")

    def sectype(self, *args: Any) -> None:
        self.calls.append("sectype")

    def secoffset(self, *args: Any) -> None:
        self.calls.append("secoffset")

    def secdata(self, *args: Any) -> None:
        self.calls.append("secdata")

    def n(self, _: int, x: float, y: float, z: float) -> None:
        self.calls.append("n")
        self._nodes.append([x, y, z])
        self.mesh.nodes = np.asarray(self._nodes)

    def e(self, *args: Any) -> None:
        self.calls.append("e")

    def d(self, *args: Any) -> None:
        self.calls.append("d")

    def f(self, *args: Any) -> None:
        self.calls.append("f")

    def run(self, _: str) -> None:
        self.calls.append("run")

    def antype(self, _: str) -> None:
        self.calls.append("antype")

    def solve(self) -> None:
        self.calls.append("solve")

    def post1(self) -> None:
        self.calls.append("post1")

    def set(self, *_: Any) -> None:
        self.calls.append("set")
