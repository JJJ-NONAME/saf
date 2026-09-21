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


"""Info card component for displaying information."""

from ansys.solutions.dash_super_components.utils.svg_icons import (
    IconNames,
    create_icon_span,
)
import dash_mantine_components as dmc

from ansys.solutions.showcase_dash_super_components.ui.utilities.common_colors import CommonColors


def layout(paragraphs: list[str]) -> dmc.Card:
    """Layout of the info card component."""
    return dmc.Card(
        [
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            create_icon_span(
                                IconNames.MATERIAL_INFO,
                                size_px=24,
                                color=CommonColors.MANTINE_DIMMED,
                            ),
                        ],
                        span="content",
                    ),
                    dmc.GridCol(
                        [
                            # Render each paragraph as its own dmc.Text component
                            *[
                                dmc.Text(
                                    paragraph,
                                    size="md",
                                    c=CommonColors.MANTINE_DIMMED,
                                    style={"textAlign": "left"},
                                )
                                for paragraph in paragraphs
                            ],
                        ],
                        span="auto",
                    ),
                ],
                align="center",
            )
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        style={
            "display": "flex",
            "textAlign": "center",
            "justifyContent": "center",
            "width": "60%",
            "minWidth": "400px",
        },
    )
