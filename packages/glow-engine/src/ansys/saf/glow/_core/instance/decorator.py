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

from __future__ import annotations

from functools import wraps
import logging
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar

from ansys.saf.glow._config.const import INSTANCES_USED_BY_METHOD_ATTRIBUTE_STRING
from ansys.saf.glow._core.exceptions import SolutionLoadException
from ansys.saf.glow._core.instance.attribute import CreateInstance, Instance, InstanceAttribute
from ansys.saf.glow._core.instance.identification import InstanceIdentificationClient

if TYPE_CHECKING:
    from collections.abc import Callable

    import httpx2

    from ansys.saf.glow._config.settings import Settings
    from ansys.saf.glow._core.instance.manager import ProductInstanceManager
    from ansys.saf.glow._core.instance.recoverystate import TRecoveryStateInfo
    from ansys.saf.glow._core.solution import Solution
    from ansys.saf.glow._core.step_model import StepModel
    from ansys.saf.glow._core.step_spec import StepSpec

logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")


class InstancesUsedByMethod:
    def __init__(self) -> None:
        self._instances: list[InstanceAttribute] = []

    @property
    def instance_attributes(self) -> list[InstanceAttribute]:
        return self._instances

    def find_create_instance(self) -> CreateInstance | None:
        for instance in self._instances:
            if isinstance(instance, CreateInstance):
                return instance

    def validate(self, step_specs: dict[str, StepSpec], step_name: str):
        normalized_references = [instance.get_full_name(step_name) for instance in self._instances]
        duplicate_references = self._get_duplicates(normalized_references)
        if duplicate_references:
            raise SolutionLoadException(
                "there is more than one instance decorator that refer to each of the following instances: "
                f"{', '.join(duplicate_references)}",
            )

        instance_identifiers = [i.identifier for i in self._instances]
        duplicates = self._get_duplicates(instance_identifiers)
        if len(duplicates) != 0:
            raise SolutionLoadException(
                f"the following instance identifiers are used more than once: {', '.join(duplicates)}",
            )
        for instance in self._instances:
            instance.validate(step_specs, step_name)

    def _get_duplicates(self, sequence: list[str]):
        return {i for i in sequence if sequence.count(i) > 1}

    def add(self, instance: InstanceAttribute) -> None:
        # The duplicates are tracked and not reported so that the import process can complete without exceptions.
        # The duplicates are reported by the checking process so that error reporting can be consistent and
        # account for dot notation
        self._instances.append(instance)

    def is_instance_identifier(self, name: str) -> bool:
        ids = [i.identifier for i in self._instances]
        return name in ids


def _annotate_function_with_instance(step_func: Any, step_method_wrapper: Any, attribute: InstanceAttribute) -> None:
    instances_used_by_method = InstancesUsedByMethod()
    instances_used_by_method = getattr(step_func, INSTANCES_USED_BY_METHOD_ATTRIBUTE_STRING, instances_used_by_method)
    instances_used_by_method.add(attribute)
    setattr(step_method_wrapper, INSTANCES_USED_BY_METHOD_ATTRIBUTE_STRING, instances_used_by_method)  # type: ignore

    def _raise_invalid_ordering_exception(step_name: str, solution: Any):  # type: ignore
        raise SolutionLoadException(
            f"the @{attribute.decorator_name} decorator appears before the @transaction decorator",
        )

    step_method_wrapper._validate = _raise_invalid_ordering_exception  # type: ignore


def instance_decorator_func(
    step_func: Callable[..., T],
    attribute: InstanceAttribute,
    step_self: StepModel,
    project_url: str,
    solution: Solution,
    name_of_step_containing_method: str,
    settings: Settings,
    http_client: httpx2.Client,
    **kwargs: Any,
) -> T:
    referenced_step_name = attribute.parse_field_reference(name_of_step_containing_method)[0]
    create_instance_decorator = attribute.resolve_origin_create_instance(solution, referenced_step_name)
    storage_url = create_instance_decorator.get_instance_url(project_url, referenced_step_name)
    instance_manager = create_instance_decorator.declared_instance_type(
        _instance_identification=InstanceIdentificationClient[create_instance_decorator.recovery_state_type](
            storage_url,
            http_client,
            create_instance_decorator.recovery_state_type,
            is_create_instance=isinstance(attribute, CreateInstance),
        ),
        _max_execution_time=attribute.max_execution_time,
    )
    with instance_manager._instance_manager_impl as manager_impl:  # pyright: ignore[reportPrivateUsage]
        kwargs[attribute.identifier] = instance_manager
        if isinstance(attribute, Instance):
            manager_impl.reconnect()

        if hasattr(step_func, "__wrapped__"):
            # step_func is not the real step method, but a decorated function (@long_running or @instance)
            # so let's pass the needed arguments
            return step_func(
                step_self,
                project_url,
                solution,
                name_of_step_containing_method,
                settings,
                **kwargs,
            )
        else:
            # step_func is the real step method: use only the arguments it needs
            return step_func(**kwargs)


def instance(
    instance_name: str,
    identifier: str | None = None,
):
    """A decorator of transaction methods which indicates that
    the method will use a shared product instance that was
    created by another method.

    A method decorated with the :py:func:`~ansys.saf.glow.solution.create_instance`
    decorator indicates that the decorated method will create a named instance.

    An ``InstanceManager`` object for the shared product instance
    is passed as an argument to the transaction method.

    Parameters
    ----------
    instance_name : str
        Reference to a shared product instance.

        This parameter can contain no period (``.``) characters.
        If it does, then the parameter refers to the shared product instance with the same
        name that was created by another method on the same step as the
        decorated method.

        This parameter can contain a single period (``.``) character
        separating two names where the first is a step name (see Notes) and
        the second name refers to a shared product instance created on
        the named step.

    identifier : str, optional
        Name of the argument of the decorated method that is passed
        the ``InstanceManager`` object for the shared product instance
        referenced by ``instance_name``.
        If this parameter is not supplied, then the name of the
        referenced instance is used.

    Notes
    -----
    For instructions and examples of how to use ``instance`` to access shared product instances, see
    |saf-docs-access-use-product-instance-ref|_ in the User Guide.

    A 'step' is a field on a
    :py:class:`~ansys.saf.glow.solution.StepsModel` derived class.
    The name of a step is the name of the field.
    The :py:class:`~ansys.saf.glow.solution.StepsModel` derived class is the type of the
    :py:class:`~ansys.saf.glow.solution.Solution.steps` field which defines the set of steps in a
    :py:class:`~ansys.saf.glow.solution.Solution` derived class.
    """

    def decorator(step_func: Callable[P, T]) -> Callable[..., T]:
        attribute = Instance(instance_name, step_func.__name__, identifier)

        @wraps(step_func)
        def step_method_wrapper(
            step_self: StepModel,
            project_url: str,
            solution: Solution,
            name_of_step_containing_method: str,
            settings: Settings,
            http_client: httpx2.Client,
            *_: P.args,
            **kwargs: P.kwargs,
        ) -> T:
            return instance_decorator_func(
                step_func,
                attribute,
                step_self,
                project_url,
                solution,
                name_of_step_containing_method,
                settings,
                http_client,
                **kwargs,
            )

        _annotate_function_with_instance(step_func, step_method_wrapper, attribute)
        return step_method_wrapper

    return decorator


def create_instance(
    instance_name: str,
    instance_manager_type: type[ProductInstanceManager[Any, TRecoveryStateInfo]],
    identifier: str | None = None,
    max_execution_time: int | None = None,
):
    """Transaction method decorator which ensures that, in the current
    project, a named shared product instance is created for the step
    in which the method is declared.

    Parameters
    ----------
    instance_name : str
        The name of the product instance.

        This string must be unique across the ``create_instance`` decorators
        in the step.

    instance_manager_type : ``class derived from ProductInstanceManager``
        Instance manager that is to be used to manage the product instance.

        This class determines the type of product instance that is created. It is recommended that a class derived
        from :py:class:`~ansys.saf.glow.solution.InstanceManager` is used as it would provide a
        typed (IDE friendly) interface to the product client.

    identifier : str, optional
        Name of the argument of the annotated method that will be passed
        the object of ``instance_manager_type`` when the method is invoked.

        If not given, then ``instance_name`` is used instead.

    max_execution_time : str, optional
        Amount of time (in seconds) after which an instance managed by Ansys HPS will be
        timed-out by HPS. Useful to avoid leaving instances on a stuck state.

        Currently has no effect if 'GLOW_PRODUCT_INSTANCE_SYSTEM' is set to 'PIM'.

        If not given, the value is set to 7200 seconds (2 hours).

    Notes
    -----
    For instructions and examples on how to use ``create_instance`` to create shared product instances, see
    |saf-docs-create-product-instance-ref|_ in the User Guide.

    Examples
    --------
    >>> @transaction(self=StepSpec(download=["aedt_file"]))
    >>> @create_instance("aedt", Maxwell2DManager, max_execution_time=3600)
    >>> def initialize_instance(self, aedt: Maxwell2DManager) -> None:
    >>>    aedt.initialize(self.aedt_file)
    """

    def decorator(step_func: Callable[P, T]) -> Callable[..., T]:
        attribute = CreateInstance(
            instance_name,
            instance_manager_type,
            step_func.__name__,
            identifier,
            max_execution_time,
        )

        @wraps(step_func)
        def step_method_wrapper(
            step_self: StepModel,
            project_url: str,
            solution: Solution,
            name_of_step_containing_method: str,
            settings: Settings,
            http_client: httpx2.Client,
            *_: P.args,
            **kwargs: P.kwargs,
        ) -> T:
            return instance_decorator_func(
                step_func,
                attribute,
                step_self,
                project_url,
                solution,
                name_of_step_containing_method,
                settings,
                http_client,
                **kwargs,
            )

        _annotate_function_with_instance(step_func, step_method_wrapper, attribute)
        return step_method_wrapper

    return decorator
