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

from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class MethodStatus(StrEnum):
    """The execution state of a transaction method
    in the context of a project.
    Notes
    -----
    |saf-docs-transaction-methods-ref|_ explains the transaction method concept in
    more detail.
    """

    RunRequired = "run-required"
    """The method has never been run in the project."""

    Running = "running"
    """The method is currently running in the project."""

    Completed = "completed"
    """The last execution of the method in the project
    was successful.

    The method has run at least once in the project.
    """

    Failed = "failed"
    """The last execution of the method in the
    project failed.

    The method has run at least once in the project.
    """


class MethodState(BaseModel):
    """The state of a transaction method in the context
    of a project.
    Notes
    -----
    |saf-docs-transaction-methods-ref|_ explains the transaction method concept in
    more detail.
    """

    status: MethodStatus
    """The state of the method."""

    result: Any | None = None
    """The value returned by the method, if any."""

    status_code: int | None = None
    """If an error occurred, this field indicates the result of the method execution
    encoded according to the HTTP response status code standard.

    See https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status.
    """

    exception_message: str | None = None
    """If an error occurred (:py:attr:`~ansys.saf.glow.solution.MethodState.status` is
    :py:attr:`~ansys.saf.glow.solution.MethodStatus.Failed`), then this field contains the exception message for
    the failure.

    If :py:attr:`~ansys.saf.glow.solution.MethodState.status` is not
    :py:attr:`~ansys.saf.glow.solution.MethodStatus.Failed`, then this field is ``None``.
    """

    exception_stack: str | None = None
    """If an error occurred (:py:attr:`~ansys.saf.glow.solution.MethodState.status` is
    :py:attr:`~ansys.saf.glow.solution.MethodStatus.Failed`),
    then this field contains the stack trace for the failure.

    If :py:attr:`~ansys.saf.glow.solution.MethodState.status` is not
    :py:attr:`~ansys.saf.glow.solution.MethodStatus.Failed`, then this field is ``None``.
    """

    def raise_for_error(self, exceptions_by_code: dict[int, type[Exception]]):
        """Raise an exception base on the status_code if an error occurred
        (when :py:attr:`~ansys.saf.glow.solution.MethodState.status` is
        :py:attr:`~ansys.saf.glow.solution.MethodStatus.Failed`)."""
        if self.status != MethodStatus.Failed or self.status_code is None:
            return
        if self.exception_message is None:
            raise RuntimeError(
                "Something is wrong with the state of the method: it does not contain any error message.",
            )
        message = self.exception_message
        if self.exception_stack:
            message += f"\n  {self.exception_stack}"
        exception = exceptions_by_code[self.status_code]
        raise exception(message)
