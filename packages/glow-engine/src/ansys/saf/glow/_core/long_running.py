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

from collections.abc import Callable
import functools
import time
from typing import Generic, ParamSpec, TypeVar

import httpx2
from pydantic import TypeAdapter

from ansys.saf.glow._core.client_exceptions import CLIENT_EXCEPTIONS_BY_CODE, BadRequestException, check
from ansys.saf.glow._core.method_status import MethodState, MethodStatus
from ansys.saf.glow._core.step_model import StepModel

T = TypeVar("T")
P = ParamSpec("P")


class LongRunning(Generic[T]):
    """An object that monitors the execution of a call to a long-running transaction method.

    A method that is decorated with :py:func:`~ansys.saf.glow.solution.long_running` will return a
    ``LongRunning`` object when called from a :py:class:`~ansys.saf.glow.solution.Solution` instance returned by
    the GLOW client. The calling environment can use the ``LongRunning`` object to monitor the method execution.

    It is not expected that the constructor will be called directly by a Solution client.

    Parameters
    ----------
    step_model_type : ``type of StepModel``
        The step class that contains the method to be monitored.

    step_name : str
        The name of the step that contains the method to be monitored.
        The name of a step is the name of a field on a
        :py:class:`~ansys.saf.glow.solution.StepsModel` derived class.
        The :py:class:`~ansys.saf.glow.solution.StepsModel` derived class is the type of the
        :py:class:`~ansys.saf.glow.solution.Solution.steps` field which defines the set of steps in a
        :py:class:`~ansys.saf.glow.solution.Solution` derived class.

    method_name : str
        The name of the method that contains the method to be monitored.

    method_url : str
        The URL of the method to be monitored.

    Notes
    -----
    For more detailed information on the concept of long-running methods, see
    |saf-docs-asynchronous-execution-ref|_ of the User Guide.
    """

    def __init__(
        self,
        step_model_type: type[StepModel],
        step_name: str,
        method_name: str,
        method_url: str,
        http_client: httpx2.Client,
        return_type: T,
    ) -> None:
        self._step_model_type = step_model_type
        self._step_name = step_name
        self._method_name = method_name
        if method_name not in self._step_model_type.get_long_running_method_names():
            raise BadRequestException(f"{method_name} is not a long running method on {self._step_name}")
        self._method_url = method_url
        self._http_client = http_client
        self._return_type = return_type

    def get_state(self) -> MethodState:
        """Get the state of the long running method.

        Returns
        -------
        MethodState
            The current state of the method execution

        Notes
        -----
        For instructions and an example on using this method, see
        |saf-docs-check-method-execution-status-ref|_ in the User Guide.
        """
        r = self._http_client.get(self._method_url)
        check(r)
        state = MethodState.model_validate(r.json())
        return state

    def is_complete(self, raise_for_error: bool = True) -> bool:
        """Specify whether the long-running method is complete or not.

        Parameters
        ----------
        raise_for_error : bool
            If specified, then an exception is raised if the method has failed.

        Returns
        -------
        bool
            Whether the long-running method is complete or not.

        Notes
        -----
        For instructions and an example of using this method, see
        |saf-docs-check-method-execution-status-ref|_ in the User Guide.
        """
        state = self.get_state()
        if raise_for_error:
            state.raise_for_error(CLIENT_EXCEPTIONS_BY_CODE)
        return state.status == MethodStatus.Completed

    def wait(self, timeout: int | None = None) -> T:
        """Wait for the long running method to terminate.

        If the process does not terminate after timeout seconds,
        then raise a :py:class:`TimeoutError` exception. It is safe to
        catch this exception and retry the wait.

        Parameters
        ----------
        timeout : int
            If specified, then the parameter can be used to control
            the maximum number of seconds to wait before returning.

        Notes
        -----
        For a description of this method with an example of its use, see
        |saf-docs-wait-for-long-running-ref|_ in the User Guide.
        """
        status = None
        start = time.perf_counter()
        state = None
        while status != MethodStatus.Completed:
            state = self.get_state()
            state.raise_for_error(CLIENT_EXCEPTIONS_BY_CODE)
            status = state.status
            duration = time.perf_counter() - start
            if timeout is not None and duration > timeout:
                raise TimeoutError(f"Waiting for the long running method '{self._method_name}' timed out.")
            time.sleep(0.5)
        return TypeAdapter(self._return_type).validate_python(state.result)  # type: ignore


def long_running(step_func: Callable[P, T]) -> Callable[P, LongRunning[T]]:
    """Decorator for transaction methods which need to be non-blocking in the client or in the REST API.
    Calls by a client to a ``long_running`` decorated transaction method will be non-blocking.
    The REST POST calls to a ``long_running`` decorated transaction method will complete before
    the transaction method implementation has completed. Typically, methods decorated with ``long_running``
    potentially have a long execution time.

    Notes
    -----
    For details on using this decorator, see |saf-docs-asynchronous-execution-ref|_ in the User Guide.
    """

    @functools.wraps(step_func)
    def wrapper_func(*args: P.args, **kwargs: P.kwargs) -> T:
        if hasattr(step_func, "__wrapped__"):
            # step_func is not the real step method, but a decorated function (e.g. @instance)
            # so let's pass the needed arguments
            return step_func(*args, **kwargs)
        else:
            # step_func is the real step method: use only the arguments it needs
            return step_func(**kwargs)  # type: ignore

    wrapper_func.__wrapped_long_running_method__ = step_func  # type: ignore

    return wrapper_func  # type: ignore
