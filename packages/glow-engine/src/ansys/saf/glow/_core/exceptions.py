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


class SolutionLoadException(Exception):  # noqa: N818
    """Exception raised when errors are detected during
    validation of a :py:class:`~ansys.saf.glow.solution.Solution` derived class prior to creating an API server.

    Parameters
    ----------
    errors : str, list of str
        Errors detected in the a :py:class:`~ansys.saf.glow.solution.Solution` derived class.
    """

    exit_code = 3

    def __init__(self, errors: str | list[str]) -> None:
        super().__init__(errors)
        self._errors = errors if isinstance(errors, str) else "\n".join(errors)

    @property
    def errors(self) -> str:
        """Errors detected in a :py:class:`~ansys.saf.glow.solution.Solution` derived class.

        Returns
        -------
        str
            Errors detected in a :py:class:`~ansys.saf.glow.solution.Solution` derived class.
        """
        return self._errors
