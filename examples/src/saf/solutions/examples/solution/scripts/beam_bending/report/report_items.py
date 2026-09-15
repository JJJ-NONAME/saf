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

# ©2025, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""
This module uses PyDynamicReporting API's Item class to create and push report items to the ADR database.

PyDynamicReporting Documentation: https://dynamicreporting.docs.pyansys.com/version/stable/index.html

The report items are created in section-specific methods. Each method is responsible for creating,
defining, and setting tags for the items in the reports main sections,
namely Introduction, Model, Problem Setup, Results, and Conclusion.

Example usage:
--------------
Create a new text item for the Example section:

new_item = adr.create_item(String, name="example-description", content="This is an Example", tags="section=example")
new_item.save()

Set a tag for the item. This is useful for filtering only the relevant data in the sections of the report.
    new_item.set_tags("section=example")

"""
import logging
from pathlib import Path

from ansys.dynamicreporting.core.serverless import HTML, Image, String, Table

logger = logging.getLogger(__name__)


def create_introduction_items(adr, project_tag):
    """Create the introduction text item in the ADR database."""
    section_name = "introduction"
    tags = f"section={section_name} {project_tag}"

    item_text = (
        "This report analyzes the bending behavior of a simply supported beam subjected "
        "to a concentrated load. The analytical solution based on Euler–Bernoulli beam "
        "theory is compared with a numerical solution obtained using MAPDL finite "
        "element analysis. The study investigates the influence of beam geometry, "
        "material properties, and load magnitude on the beam deflection."
    )

    adr.create_item(String, name=f"{section_name}-description", content=item_text, tags=tags)


def create_model_items(adr, image_path, project_tag):
    """Create the model description and image items in the ADR database."""
    section = "model"
    tags = f"section={section} {project_tag}"

    if not Path(image_path).exists():
        logger.error("Beam model image not found: %s", image_path)
        raise FileNotFoundError(f"Model image not found: {image_path}")

    item_text = """
        <b>Model</b>

        <p>The Euler-Bernoulli beam theory is used to predict the deflection.</p>

        <b>Assumptions:</b>
        <ul>
            <li>$H_1$: two-dimensional problem.</li>
            <li>$H_2$: the gravity is neglected.</li>
            <li>$H_3$: the beam deflection is very small compared to the length of the beam.</li>
            <li>$H_3$: the beam is made of an homogeneous elastic material.</li>
        </ul>

        <b>Geometry parameters</b>
        <ul>
            <li>$l$: beam length.</li>
            <li>$a$: distance of the load P with respect to the left support.</li>
            <li>$b$: distance of the load P with respect to the right support.</li>
            <li>$d$: diameter of the beam section.</li>
        </ul>

        <b>Material</b>
        <ul>
            <li>$E$: Young's modulus of elasticity.</li>
        </ul>

        <b>Loading</b>
        <ul>
            <li>$P$: concentrated force.</li>
        </ul>

        <b>Solution</b>

        <p>Deflection at any section for $0<x<a$:</p>
        <ul>
        $$y = \\frac{Pbx}{6lEI} (l^2-x^2-b^2)$$
        </ul>
        <p>Deflection at any section for $a<x<l$:</p>
        <ul>
        $$y = \\frac{Pb}{6lEI} (\\frac{l}{b}(x-a)^3+(l^2-b^2)x-x^3)$$
        </ul>
    """

    adr.create_item(HTML, name=f"{section}-description", content=item_text, tags=tags)

    adr.create_item(
        Image,
        name="beam-model",
        content=image_path,
        tags=tags,
    )


def create_setup_items(adr, names, values, project_tag):
    """Create the problem setup table item in the ADR database."""
    section = "setup"
    tags = f"section={section} {project_tag}"

    table_content = values.reshape(-1, 1)
    setup_table_item = adr.create_item(Table, name="setup-data", content=table_content, tags=tags)
    setup_table_item.labels_row = names
    setup_table_item.labels_column = ["Value"]
    setup_table_item.save()


def create_results_items(adr, analytical_deflection, mapdl_deflection, project_tag):
    """Create the results table item in the ADR database."""
    section = "results"
    tags = f"section={section} {project_tag}"

    results_table = adr.create_item(Table, name="deflection-data", content=analytical_deflection, tags=tags)
    results_table.labels_row = ["Position", f"Analytical Deflection"]

    results_table.plot = "line"
    results_table.xaxis = "Position"

    results_table.xaxis_format = "floatdot0"
    results_table.yaxis_format = "floatdot2"

    results_table.xtitle = "Position"
    results_table.ytitle = "Deflection"

    results_table.save()

    mapdl_results_table = adr.create_item(Table, name="mapdl-deflection-data", content=mapdl_deflection, tags=tags)
    mapdl_results_table.labels_row = ["Position", f"MAPDL Deflection"]

    mapdl_results_table.plot = "line"
    mapdl_results_table.xaxis = "Position"

    mapdl_results_table.xaxis_format = "floatdot0"
    mapdl_results_table.yaxis_format = "floatdot2"
    mapdl_results_table.xtitle = "Position"
    mapdl_results_table.ytitle = "Deflection"

    mapdl_results_table.save()


def create_mapdl_results_items(adr, nodal_disp_path, element_stress_path, project_tag):
    """Create MAPDL result image items."""
    section = "results"
    tags = f"section={section} {project_tag}"

    if Path(nodal_disp_path).exists():
        adr.create_item(
            Image,
            name="mapdl-nodal-displacement",
            content=nodal_disp_path,
            tags=tags,
        )

    if Path(element_stress_path).exists():
        adr.create_item(
            Image,
            name="mapdl-element-stress",
            content=element_stress_path,
            tags=tags,
        )


def create_conclusion_items(adr, project_tag):
    """Create the conclusion text item in the ADR database."""
    section = "conclusion"
    tags = f"section={section} {project_tag}"

    item_text = (
        "The comparison between the analytical Euler–Bernoulli beam solution "
        "and the finite element results obtained with MAPDL shows good agreement. "
        "Small differences may arise due to discretization effects and numerical "
        "approximations in the finite element model."
    )
    adr.create_item(String, name=f"conclusion-description", content=item_text, tags=tags)
