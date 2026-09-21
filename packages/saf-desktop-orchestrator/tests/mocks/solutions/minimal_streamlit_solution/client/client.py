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

import streamlit as st

from ansys.saf.desktop.orchestrator._orchestration.streamlit_client import StreamlitClient
from tests.mocks.solutions.minimal_streamlit_solution.solution.definition import MySolutionSolution


class StreamlitClientProxy:
    def __init__(self) -> None:
        # Retrieves the project_id from the query parameters of the Streamlit app.
        # This assumes that the Streamlit app expects a project_id as a query parameter when interacting with this
        # client.
        self._project_id = st.query_params["project_id"]
        # sets up necessary configurations or connections specific to the TestSolution within the Streamlit client
        # context, preparing it for subsequent interactions with the Solution API.
        StreamlitClient.initialize(MySolutionSolution)  # pyright: ignore[reportUnknownMemberType]

    def get_project(self) -> MySolutionSolution:
        """Get the project from the solution API."""
        return StreamlitClient.get_project(self._project_id)  # pyright: ignore[reportUnknownVariableType]
