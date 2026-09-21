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

from types import ModuleType

from ansys.saf.glow.cli._cli_entry_point import SolutionModule, cli


def glow_main(definition_module: ModuleType, ui_app_module: ModuleType | None = None) -> None:
    """Implement a Solution component process requiring a :py:class:`~ansys.saf.glow.solution.Solution` derived
    Solution definition. The process will be orchestrated by GLOW which will pass command line arguments
    to enable the process to perform the required functionality. ``glow_main`` will parse those command line
    arguments.

    From the perspective of a Solution developer the call to ``glow_main`` is the means for registering a
    Solution (a class derived from :py:class:`~ansys.saf.glow.solution.Solution`) and, optionally, a UI for that
    Solution with the GLOW infrastructure.

    ``glow_main`` should be called as the only or core part of a module designed to run in
    `the python top-level code environment <https://docs.python.org/3/library/__main__.html>`_.

    The ``saf run`` command searches ``ansys.solutions`` for a module that imports
    ``glow_main`` (as ``glow_main``) and executes that module in
    `the python top-level code environment <https://docs.python.org/3/library/__main__.html>`_.

    The ``saf run`` command, with a ``--no-ui`` argument, can run the Solution without a UI if
    ``ui_app_module`` is not present.

    The GLOW Solution template includes a ``main`` module that satisfies the requirements of ``saf run``.
    `The Solution Developer's guide section on solution creation
    <https://dev-docs.external.solutions.ansys.com/version/stable/user_guide/create_solution/index.html>`_
    contains more information on the Solution template.

    Parameters
    ----------
    definition_module : ModuleType
        The python module object that contains a single class derived from
        :py:class:`~ansys.saf.glow.solution.Solution`.

    ui_app_module : ModuleType, optional
        The python module object that contains an ``app`` variable referring to a
        `Dash app object <https://dash.plotly.com/reference#the-app-object>`_.
        This module is required to enable the GLOW infrastructure to orchestrate a UI for the Solution.

    Notes
    -----
    The module containing ``glow_main`` will potentially be executed by the orchestrator in a number of different
    concurrent processes in the same Solution stack.


    """

    # The `package-solution Github action
    # <https://github.com/Solution-Applications/actions/blob/main/package-solution/action.yml>`_
    # which creates a Solution deployment zip assumes that ``glow_main`` is called by the
    # ``ansys.solutions.<solution name>.main`` module which is expected to run in
    # `the python top-level code environment <https://docs.python.org/3/library/__main__.html>`_.

    cli(obj=SolutionModule(definition_module=definition_module, ui_module=ui_app_module))
