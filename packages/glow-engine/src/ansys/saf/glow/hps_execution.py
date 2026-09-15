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

# this code is designed to be loadable into older versions of python in HPS
# hence disabling ruff and black
# fmt: off
# ruff: noqa

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class HpsProduct(ABC):
    """A product accessible to a HPS job or design point evaluation."""

    @property
    @abstractmethod
    def name(self) -> str:
        """HPS name of the product."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the product (Ansys products use the form '<year> R<release>')."""
        ...

    @property
    @abstractmethod
    def executable(self) -> Path:
        """The path to the executable of the product."""
        ...

class HpsExecutionContext(ABC):
    """The context of an execution of a HPS job or design point evaluation
    providing information about the job or design point evaluation."""

    @property
    @abstractmethod
    def input_parameters(self) -> Dict[str, Any]:
        """The input parameters and files of the job or design point evaluation.
        The keys are the names of the parameters or files.
        For parameters the values in the dictionary are the values of the parameters.
        For files the values in the dictionary are the absolute paths to the file."""
        ...

    @property
    @abstractmethod
    def required_output_parameters(self) -> List[str]:
        """The key names of the output parameters passed to the project creation method."""
        ...

    @property
    @abstractmethod
    def required_output_files(self) -> Dict[str, str]:
        """A dictionary where the keys are the key names of the output files that the project
        definition expects from the job or design point evaluation.
        The values of the dictionary are the relative paths where the files are expected."""
        ...

    @property
    def required_output_directories(self) -> Dict[str, str]:
        """A dictionary where the keys are the key names of the output directories that the project
        definition expects from the job or design point evaluation.
        The values of the dictionary are the relative paths where the directories are expected."""
        ...

    @property
    @abstractmethod
    def products(self) -> List[HpsProduct]:
        """The products that were required for the job or design point evaluation includes
        the products passed to the project creation method."""
        ...

class HpsExecutionFunctionality(ABC):
    """The internal implementation of functionality to support execution of a HPS job or design point."""
    @abstractmethod
    def run_and_capture_output(self, args : List[Any], **kwargs : Any):
        ...

    @property
    @abstractmethod
    def context(self) -> HpsExecutionContext:
        ...

class HpsExecution(ABC):
    """A job or design point evaluation for execution in HPS.
    Derived classes implement the computation comprising the job or design point evaluation.
    """

    def run_and_capture_output(self, args : List[Any], keyword_args: dict[str, Any]):
        """
        Convenience function to execute an application in a new process,
        log its stdout/stderr and wait until the process completes.

        Parameters
        ----------

        args
            See args in subprocess.Popen

        **kwargs
            Allows you to pass keyword arguments to subprocess.Popen,
            except for stdout and stderr which are overridden as

            * stdout = subprocess.PIPE
            * stderr = subprocess.STDOUT

        """
        self._impl.run_and_capture_output(args, **keyword_args)

    def load_impl(self, impl: HpsExecutionFunctionality):
        """Do not call this method from Solution code."""
        self._impl = impl

    @property
    def context(self) -> HpsExecutionContext:
        """The context of an execution of the job or design point evaluation providing information about the job or design point evaluation."""
        return self._impl.context

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """The core execution of the job or design point evaluation. This method must be implemented by the derived class.

        This method should:

        - extract input parameter values from the
          :py:attr:`~ansys.saf.glow.hps_execution.HpsExecutionContext.input_parameters` property of the
          :py:attr:`~ansys.saf.glow.hps_execution.HpsExecution.context` property.
        - read input files from the current working directory. Reading files can be guided by the values
          (for those entries matching input files) in
          the :py:attr:`~ansys.saf.glow.hps_execution.HpsExecutionContext.input_parameters` property of the
          :py:attr:`~ansys.saf.glow.hps_execution.HpsExecution.context` property which are the absolute paths
          to the input files for the job.
        - write output files to the current working directory (can be guided by the
          :py:attr:`~ansys.saf.glow.hps_execution.HpsExecutionContext.required_output_files` property of the
          :py:attr:`~ansys.saf.glow.hps_execution.HpsExecution.context` property)
        - throw exceptions when error conditions are encountered
        - output logs to std out

        This method can access information about the products or applications required by the job via the
        :py:attr:`~ansys.saf.glow.hps_execution.HpsExecutionContext.products` property of the
        :py:attr:`~ansys.saf.glow.hps_execution.HpsExecution.context` property.

        If the evaluation needs to start a subprocess it is recommended that the
        :py:meth:`~ansys.saf.glow.hps_execution.HpsExecution.run_and_capture_output` method is used.

        Returns
        -------
        Dict[str, Any]]
          A dictionary of output parameter values
          where the keys and types of the values match the definition passed to the ``output_parameters`` argument of the
          :py:meth:`~ansys.saf.glow.solution.hps.HpsParametricStudyProject.start_hps_parametric_study` or
          :py:meth:`~ansys.saf.glow.solution.hps.HpsSimpleProject.start_hps_job` method call that created the job or design point.
        """
        ...


# fmt: on
