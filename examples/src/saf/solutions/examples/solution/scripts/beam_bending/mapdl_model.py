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

"""MAPDL model for the beam bending example."""

from ansys.mapdl.core import Mapdl
import numpy as np
from scipy.spatial import KDTree


class Setup:
    """Setup the MAPDL model."""

    def __init__(
        self,
        mapdl: Mapdl,
        length: float,
        radius: float,
        elastic_modulus: float,
        poisson_ratio: float,
        load_position: float,
        load_amplitude: float,
        element_type: str = "BEAM188",
        number_of_elements: int = 100,
    ) -> None:
        """Set up the MAPDL model."""
        self._length = length
        self._radius = radius
        self._elastic_modulus = elastic_modulus
        self._poisson_ratio = poisson_ratio
        self._load_position = load_position
        self._load_amplitude = load_amplitude
        self._load_node_label = None
        self._element_type = element_type
        self._number_of_elements = number_of_elements
        self._radial_subdivisions = 1  # 1 <= N <= 5
        self._circular_subdivisions = 50  # 8 <= N <= 120
        self._mapdl = mapdl

    def mesh(self) -> None:
        """Generate the mesh."""
        # Define a circular beam
        self._mapdl.prep7()
        self._mapdl.et(1, self._element_type)
        self._mapdl.keyopt(1, 4, 1)  # transverse shear stress output

        # Define material properties
        self._mapdl.mp("EX", 1, self._elastic_modulus)  # N/mm²
        self._mapdl.mp("PRXY", 1, self._poisson_ratio)  #  Poisson's ratio

        # Define beam section
        sec_num = 1
        mesh_refinement = 3  # 0 < mesh_refinement < 5
        self._mapdl.sectype(sec_num, "BEAM", "CSOLID", "CircularSection", mesh_refinement)
        self._mapdl.secoffset("CENT")  # Beam node will be offset to centroid
        beam_info = self._mapdl.secdata(
            self._radius, self._circular_subdivisions, self._radial_subdivisions
        )  # dimensions are in mm

        # Generate mesh
        number_of_nodes = self._number_of_elements + 1
        x = np.linspace(0, self._length, number_of_nodes)
        y = np.zeros(number_of_nodes)
        z = np.zeros(number_of_nodes)
        coordinates = np.array([x, y, z]).T
        distance, index = self._find_nearest_node(coordinates, np.array([self._load_position, 0, 0]))
        relative_position_error = distance / self._load_position
        if relative_position_error > 0.05:
            index += 1
            number_of_nodes += 1
            self._number_of_elements += 1
            coordinates = np.insert(coordinates, index, np.array([self._load_position, 0, 0]), axis=0)
        self._load_node_label = index + 1
        for i in range(number_of_nodes):
            self._mapdl.n(i + 1, coordinates[i, 0], coordinates[i, 1], coordinates[i, 2])

        for node in self._mapdl.mesh.nnum[:-1]:
            self._mapdl.e(node, node + 1)

    def boundary_conditions(self) -> None:
        """Define the boundary conditions."""
        # Allow movement only in the X and Z direction
        for const in ["UX", "UY", "ROTX", "ROTZ"]:
            self._mapdl.d("all", const)

        # constrain just nodes 1 and 23 in the Z direction
        self._mapdl.d(1, "UZ")
        self._mapdl.d(self._number_of_elements + 1, "UZ")

    def load(self) -> None:
        """Define the load."""
        self._mapdl.f(self._load_node_label, "FZ", -self._load_amplitude)

    def _find_nearest_node(self, coordinates: np.ndarray, point: np.ndarray) -> int:
        """Find the nearest node to a given coordinate.

        Parameters
        ----------
        coordinates: np.ndarray
            The x, y, z coordinates of the nodes.
        point: np.ndarray
            The x, y, z coordinates of the point to find the nearest node to.

        Returns
        -------
        distance, index: Tuple[float, int]
            The distance and index of the nearest node.
        """
        return KDTree(coordinates).query(point, k=1)


class Solve:
    """Solve the MAPDL model."""

    def __init__(self, mapdl: Mapdl) -> None:
        """Solve the model in MAPDL."""
        self._mapdl = mapdl

    def solve(self) -> None:
        """Solve the model in MAPDL."""
        self._mapdl.run("/solu")
        self._mapdl.antype("static")
        self._mapdl.solve()


class PostProcess:
    """Post process the MAPDL model."""

    def __init__(self, mapdl: Mapdl) -> None:
        """Post process the model in MAPDL."""
        self._mapdl = mapdl
        self._mapdl.post1()
        self._mapdl.set(1, 1)

    def get_deformed_state(self) -> None:
        """Compute the deformed coordinates."""
        displacements = self._mapdl.post_processing.nodal_displacement("ALL")
        return self._mapdl.mesh.nodes + displacements

    def plot_nodal_displacement(self, filename: str) -> None:
        """Plot the nodal displacement."""
        self._mapdl.post_processing.plot_nodal_displacement(
            "Z",
            off_screen=True,
            savefig=filename,
            cpos="xz",
        )

    def plot_element_stress(self, filename: str) -> None:
        """Plot the element stress."""
        self._mapdl.post_processing.plot_element_stress(
            "EQV",
            "AVG",
            off_screen=True,
            savefig=filename,
            cpos="xz",
        )
