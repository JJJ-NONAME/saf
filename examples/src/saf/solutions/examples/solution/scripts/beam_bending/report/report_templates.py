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
Define the ADR report templates for the beam bending example.

Templates are implemented using the PyDynamicReporting Serverless
ADR API ``Template`` class.
"""

from ansys.dynamicreporting.core.serverless import (
    BasicLayout,
    HeaderLayout,
    PanelLayout,
    TableMergeGenerator,
    TOCLayout,
)


def create_report_template(adr):
    """Create the templates for the beam bending report."""
    template_00 = adr.create_template(BasicLayout, name="solution-report", parent=None)
    template_00.params = '{"HTML": ""}'
    template_00.save()

    template_01 = adr.create_template(HeaderLayout, name="Logo", parent=template_00)
    template_01.set_filter("A|i_name|eq|ansys-logo;")
    template_01.save()

    template_02 = adr.create_template(BasicLayout, name="Title", parent=template_00)
    template_02.params = '{\
        "HTML": "<h1>Analysis of Beam Deflection under Concentrated Load using Euler-Beam Theory</h1>",\
        "properties": {"justification": "center"}}'
    template_02.set_filter("A|i_name|eq|report-title;")
    template_02.save()

    toc_template = adr.create_template(TOCLayout, name="Table of Contents", parent=template_00)
    toc_template.params = '{"TOCitems": 1}'
    toc_template.set_filter("A|i_name|eq|__NonexistantName__;")
    toc_template.save()

    template_03 = adr.create_template(PanelLayout, name="Introduction", parent=template_00)
    template_03.params = '{"properties": {"TOCItem": "1"}, "HTML": "<h3>1. Introduction</h3>"}'
    template_03.set_filter("A|i_tags|cont|section=introduction;")
    template_03.save()

    template_04 = adr.create_template(PanelLayout, name="Model", parent=template_00)
    template_04.params = '{"properties": {"TOCItem": "1"}, "HTML": "<h3>2. Model</h3>"}'
    template_04.set_filter("A|i_tags|cont|section=model;")
    template_04.save()

    template_05 = adr.create_template(PanelLayout, name="Setup", parent=template_00)
    template_05.params = '{"HTML": "<h3>3. Setup</h3>", "properties": {"TOCItem": "1"}}'
    template_05.set_filter("A|i_tags|cont|section=setup;")
    template_05.save()

    template_06 = adr.create_template(TableMergeGenerator, name="Table", parent=template_05)
    template_06.params = '{"generate_merge": "replace", \
        "merge_params": {"column_labels_as_ids": 1, "transpose_output": 0, "force_numeric": 0,\
        "merge_type": "column", "column_merge": "all", "column_id_row": "0", "collision_tag": "",\
        "unknown_value": "nan", "table_name": "merged table"}, \
        "properties": {"table_page": "6", "format": "\\"floatdotx\\""}}'
    template_06.save()

    template_07 = adr.create_template(PanelLayout, name="Results", parent=template_00)
    template_07.params = '{"properties": {"TOCItem": "1"}, "HTML": "<h3>4. Results</h3>"}'
    template_07.set_filter("A|i_tags|cont|section=results;")
    template_07.save()

    # TODO: Uncomment TableMergeGenerator once ADR bug is fixed for merging data with different x values.
    # Currently plotting theoretical and MAPDL deflection curves separately as a workaround.
    # template_08 = adr.create_template(TableMergeGenerator, name="Plot", parent=template_07)
    # template_08.params = '{"properties": {\
    #     "plot": "line", "xaxis_format": "floatdot0", "yaxis_format": "floatdot2", "xaxis": "Position", \
    #     "ytitle": "Deflection [mm]", "xtitle": "Position [mm]", "show_border": ""}, \
    #     "merge_params": {"column_labels_as_ids": 0, "transpose_output": 0, "force_numeric": 0, \
    #     "merge_type": "row", "column_merge": "all", "column_id_row": "0", "collision_tag": "", \
    #     "unknown_value": "nan", "table_name": "merged table", "source_rows": "\'*|merge\'"}, \
    #     "generate_merge": "replace", "transpose": false}'
    # template_08.save()

    template_09 = adr.create_template(PanelLayout, name="Conclusion", parent=template_00)
    template_09.params = '{"properties": {"TOCItem": "1"}, "HTML": "<h3>5. Conclusion</h3>"}'
    template_09.set_filter("A|i_tags|cont|section=conclusion;")
    template_09.save()
