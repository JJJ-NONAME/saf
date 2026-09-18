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


class StepSpec:
    """Definition of the fields on a given step that
    are to be transferred between a method's execution
    environment and a project at the beginning and end
    of the method's execution.

    The definition determines whether fields are either
    accessible or modifiable within the method's execution.

    Parameters
    ----------
    download : ``list of str``, optional
        Names of fields on the step whose values are transferred
        from the project to the method execution environment
        before the method starts.

        These are the only fields that are accessible with the method.

    upload : ``list of str``, optional
        Names of fields on the step whose values are transferred
        from the method execution environment to the project after
        the method has completed.

        These are the only fields that are modifiable within the method.

    Notes
    -----
    ``StepSpec`` objects are normally passed as arguments to
    instances of the :py:func:`~ansys.saf.glow.solution.transaction` decorator which
    decorate transaction methods.
    You can read about the role of ``StepSpec`` objects in transaction method
    definitions |saf-docs-transaction-methods-ref|_.
    """

    def __init__(
        self,
        download: list[str] | None = None,
        upload: list[str] | None = None,
    ) -> None:
        self._download = download or []
        self._upload = upload or []

    @property
    def download(self) -> list[str]:
        """Names of fields on the step whose values are transferred
        from the project to the method execution environment before
        the method starts.

        These are the only fields that are accessible within the method.

        Returns
        -------
        ``list of str``
            Names of fields on the step whose values are transferred
            from the project to the method execution environment
            before the method starts.
        """
        return self._download

    @property
    def upload(self) -> list[str]:
        """Names of fields on the step whose values are
        transferred from the method execution environment
        to the project after the method has completed.

        These are the only fields that are modifiable within the method.

        Returns
        -------
        ``list of str``
            Names of fields on the step whose values are transferted
            from the method execution environment to the project after
            the method has completed.
        """
        return self._upload
