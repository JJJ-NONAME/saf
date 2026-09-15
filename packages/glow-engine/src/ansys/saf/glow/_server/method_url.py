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

import re
from urllib.parse import urlparse, urlunparse

from ansys.saf.glow._utilities.conversion import url_part_to_python_identifier


class MethodUrl:
    def __init__(self, method_url: str) -> None:
        self._url = method_url
        self._parsed_url = urlparse(method_url)
        match = re.search(r"projects\/.+\/steps\/[\w\-_]+:\w+", self._parsed_url.path)
        if not match:
            raise Exception(
                f"Expecting url of the form <domain>/projects/<project>/steps/<step>:<method> - got {method_url}",
            )
        path_segments = [segment for segment in self._parsed_url.path.split("/") if segment != ""]
        last_segments = path_segments.pop().split(":")  # pop step_id:method
        self._method_id = last_segments.pop()
        self._method_name = url_part_to_python_identifier(self._method_id)
        self._step_id = last_segments.pop()
        self._step_name = url_part_to_python_identifier(self._step_id)
        path_segments.pop()  # pop "steps"
        self._project_resource_name = "/".join(path_segments)
        self._project_url = urlunparse(
            (self._parsed_url.scheme, self._parsed_url.netloc, self._project_resource_name, "", "", ""),
        )
        step_resource_name = f"{self._project_resource_name}/steps/{self._step_id}"
        self._step_url = urlunparse((self._parsed_url.scheme, self._parsed_url.netloc, step_resource_name, "", "", ""))
        event_resource_name = f"events/{step_resource_name}/streams/{self._method_id}"
        self._event_url = urlunparse(
            [self._parsed_url.scheme, self._parsed_url.netloc, event_resource_name, "", "", ""],
        )

    @property
    def url(self) -> str:
        return self._url

    @property
    def step_name(self) -> str:
        return self._step_name

    @property
    def method_name(self) -> str:
        return self._method_name

    @property
    def step_id(self) -> str:
        return self._step_id

    @property
    def method_id(self) -> str:
        return self._method_id

    @property
    def project_resource_name(self) -> str:
        return self._project_resource_name

    @property
    def project_url(self) -> str:
        return self._project_url

    @property
    def step_url(self) -> str:
        return self._step_url

    @property
    def event_url(self) -> str:
        return self._event_url
