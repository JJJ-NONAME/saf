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

from ansys.saf.desktop.orchestrator._orchestration.process import ServiceProcess


class ServiceInfo:
    def __init__(self, address: str, service_type: str, process: ServiceProcess):
        self._address = address
        self._type = service_type
        self._process = process

    @property
    def address(self) -> str:
        return self._address

    @property
    def service_type(self) -> str:
        return self._type

    @property
    def process(self) -> ServiceProcess:
        return self._process
