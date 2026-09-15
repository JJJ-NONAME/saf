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

HPS_EXECUTION_CONTENT = """
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class HpsProduct(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        ...

    @property
    @abstractmethod
    def executable(self) -> Path:
        ...

class HpsExecutionContext(ABC):

    @property
    @abstractmethod
    def input_parameters(self) -> Dict[str, Any]:
        ...

    @property
    @abstractmethod
    def required_output_parameters(self) -> List[str]:
        ...

    @property
    @abstractmethod
    def required_output_files(self) -> Dict[str, str]:
        ...

    @property
    def required_output_directories(self) -> Dict[str, str]:
        return self._data["required_output_directories"]

    @property
    @abstractmethod
    def products(self) -> List[HpsProduct]:
        ...

class HpsExecutionFunctionality(ABC):
    @abstractmethod
    def run_and_capture_output(self, args : List[Any], **kwargs : Any):
        ...

    @property
    @abstractmethod
    def context(self) -> HpsExecutionContext:
        ...

class HpsExecution(ABC):

    def run_and_capture_output(self, args : List[Any], keyword_args: dict[str, Any]):
        self._impl.run_and_capture_output(args, **keyword_args)

    def load_impl(self, impl: HpsExecutionFunctionality):
        self._impl = impl

    @property
    def context(self) -> HpsExecutionContext:
        return self._impl.context

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        ...



"""
# fmt: on
