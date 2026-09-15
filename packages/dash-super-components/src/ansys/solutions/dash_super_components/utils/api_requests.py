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


"""Collection of abstract classes for making API requests."""

import json

import requests


class GlowAPIRequest:
    """HTTP client for interacting with the GLOW API.

    Parameters
    ----------
    url : str
        The base URL of the GLOW API server.
    """

    def __init__(self, url: str):
        self._url = url

    def get_transaction_method_status(self, step_name: str, method_name: str) -> str:
        """Retrieve the current status of a transaction method from the GLOW API.

        Parameters
        ----------
        step_name : str
            The name of the GLOW step that contains the method. Use underscores or hyphens.
        method_name : str
            The name of the GLOW transaction method. Use underscores or hyphens.

        Returns
        -------
        str
            The status string returned by the API (e.g. ``"running"``,
            ``"completed"``, ``"failed"``).

        Raises
        ------
        Exception
            If the API response is not successful.
        """
        step_name_hyphenated = step_name.replace("_", "-")
        method_name_hyphenated = method_name.replace("_", "-")
        response = requests.get(
            f"{self._url}/steps/{step_name_hyphenated}:{method_name_hyphenated}",
            headers={"accept": "application/json"},
            timeout=10,
        )
        if response.ok:
            response_content = json.loads(response.content)
            return response_content["status"]
        else:
            raise Exception("Failed to get the response")
