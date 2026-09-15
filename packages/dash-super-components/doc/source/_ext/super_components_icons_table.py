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

"""
Sphinx extension that generates an HTML table of bundled SVG icons.

Use the ``.. icon_table::`` directive in any RST file to render a
responsive table that shows every member of
``ansys.solutions.dash_super_components.utils.svg_icons.IconNames``
together with its Python constant name and the underlying icon-set
identifier string.
"""

from string import Template

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx

ROW_TEMPLATE = Template("""\
    <tr>
        <td class='icon-cell'>${svg}</td>
        <td><code class='icon-enum'>${enum_name}</code></td>
        <td><code class='icon-value'>${icon_value}</code></td>
    </tr>""")

TABLE_TEMPLATE = Template("""\
<table class="icon-table">
    <thead>
        <tr><th>Icon</th><th>Enum name</th><th>Icon identifier</th></tr>
    </thead>
    <tbody>
${rows}
    </tbody>
</table>
""")


class IconTableDirective(Directive):
    """Render a visual table of all bundled SVG icons.

    The directive takes no arguments and produces an HTML table
    that lists every ``IconNames`` member together with a preview
    image, its Python constant name, and the underlying icon-set
    identifier string.
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    def run(self):
        """Build the raw HTML table node."""
        try:
            from ansys.solutions.dash_super_components.utils.svg_icons import (
                IconNames,
                get_svg_icon,
            )
        except ImportError as exc:
            error = self.state_machine.reporter.error(
                f"{__name__}: could not import svg_icons module: {exc}",
                nodes.literal_block(str(exc), str(exc)),
                line=self.lineno,
            )
            return [error]

        rows = []
        for member in IconNames:
            svg_raw = get_svg_icon(member, color="#555555")
            svg_markup = svg_raw.strip()

            row = ROW_TEMPLATE.substitute(
                svg=svg_markup,
                enum_name=member.name,
                icon_value=member.value,
            )
            rows.append(row)

        html = TABLE_TEMPLATE.substitute(rows="".join(rows))

        return [nodes.raw("", html, format="html")]


def setup(app: Sphinx) -> dict:
    """Register the ``super-components-icons-table`` directive with Sphinx."""
    app.add_directive("super-components-icons-table", IconTableDirective)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
