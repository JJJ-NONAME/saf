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

from tests.mocks.solutions.minimal_streamlit_solution.client.client import StreamlitClientProxy


def layout():
    first_arg_1: float = 8
    second_arg_1: float = 9
    st.header("____ . . .")
    st.subheader(
        f"first_arg : {first_arg_1} , second_arg : {second_arg_1} and result : {calculate(first_arg_1, second_arg_1)}",
        divider=True,
    )


def calculate(first_arg_1: float, second_arg_1: float) -> float:
    project = StreamlitClientProxy().get_project()
    first_step = project.steps.first_step
    first_step.first_arg = first_arg_1
    first_step.second_arg = second_arg_1
    first_step.calculate()
    return first_step.result
