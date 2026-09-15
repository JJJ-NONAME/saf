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

import base64
import re


def camel_to_snake(name: str) -> str:
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def python_identifier_to_url_part(python_identifier: str) -> str:
    return python_identifier.replace("_", "-")


def url_part_to_python_identifier(url_part: str) -> str:
    return url_part.replace("-", "_")


def data_uri_to_bytes(data_uri: str) -> bytes:
    """Convert a Data URI (Uniform Resource Identifier) to bytes.

    This function extracts the base64-encoded data from the URI and decodes it to bytes.

    Parameters
    ----------
    data_uri : str
        A string representing the Data URI to be converted.

    Returns
    -------
        bytes
            The decoded binary data extracted from the Data URI.
    """
    data = data_uri.split(",")[-1]
    return base64.b64decode(data)
