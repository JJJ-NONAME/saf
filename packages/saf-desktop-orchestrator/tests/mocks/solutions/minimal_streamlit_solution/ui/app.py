# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
#

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
#


import streamlit as st
import streamlit_antd_components as sac  # pyright: ignore[reportMissingTypeStubs]

from ansys.saf.desktop.orchestrator._orchestration.streamlit_client import StreamlitClient
from tests.mocks.solutions.minimal_streamlit_solution.ui.layouts import (
    first,
    second,
)

st.set_page_config(layout="wide", page_title="first_app", initial_sidebar_state="expanded")
css = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    .stApp .main .block-container{
        padding-top:3px
    }
    .stApp [data-testid='stSidebar']>div:nth-child(1)>div:nth-child(2){
        padding-top:3px
    }
    [data-testid="stSidebar"]{
        min-width: 300px;
        max-width: 300px;
    }
    iframe{
        display:block;
    }
    .stDeployButton {
        visibility: hidden;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)
# Retrieves a URL from a custom StreamlitClient object for linking back to a portal.
portal_ui_url = StreamlitClient().get_portal_ui_url()
# Sidebar
with st.sidebar.container():
    # Title
    st.subheader("First App")
    # Treeview
    page = sac.menu(  # pyright: ignore[reportUnknownMemberType]
        [
            sac.MenuItem(
                label="Select",
                icon="broadcast",
                children=[
                    sac.MenuItem(
                        "First",
                        icon="gear-fill",
                    ),
                    sac.MenuItem(
                        "Second",
                        icon="bar-chart-fill",
                    ),
                ],
            ),
            sac.MenuItem("Report", icon="clipboard-data-fill"),
            sac.MenuItem(type="divider"),
            sac.MenuItem(
                "Back to projects",
                icon="arrow-left-circle-fill",
                href=portal_ui_url or "",
                disabled=bool(portal_ui_url),
            ),
            sac.MenuItem(type="divider"),
            sac.MenuItem(
                "Documentation",
                type="group",
                children=[
                    sac.MenuItem(
                        "Developer Guide",
                        icon="compass-fill",
                        href="https://dev-docs.solutions.ansys.com/index.html",
                    ),
                    sac.MenuItem(
                        "SAF",
                        icon="code-square",
                        href="https://saf.docs.solutions.ansys.com/version/stable/",
                    ),
                    sac.MenuItem("Streamlit", icon="gem", href="https://docs.streamlit.io/"),
                ],
            ),
        ],
        format_func="title",
        open_all=True,
    )

# Body
# Page switching logic
with st.container():
    if page in ["Select", "First"]:
        first.layout()
    elif page == "Second":
        second.layout()
