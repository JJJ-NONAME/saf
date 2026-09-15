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

import logging
from typing import TYPE_CHECKING, Any

from ansys.saf.glow._core.exceptions import SolutionLoadException
from ansys.saf.glow._core.instance.manager import ProductInstanceManager
from ansys.saf.glow._utilities.conversion import python_identifier_to_url_part

if TYPE_CHECKING:
    from typing import Self

    from ansys.saf.glow._core.instance.recoverystate import RecoveryStateInfo, TRecoveryStateInfo
    from ansys.saf.glow._core.solution import Solution
    from ansys.saf.glow._core.step_spec import StepSpec

logger = logging.getLogger(__name__)


class InstanceAttribute:
    def __init__(self, instance_reference: str, transaction_name: str, identifier: str | None = None) -> None:
        """
        Provides information about the attributes passed to the @instance decorator

        Parameters
        ----------
        instance_reference : str
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
        """
        self._instance_name = instance_reference.split(".")[-1]
        self._transaction_name = transaction_name
        self._instance_reference = instance_reference
        self._identifier = self._instance_name if identifier is None else identifier

    def __hash__(self) -> int:
        return hash((self._instance_reference, self._identifier))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, InstanceAttribute):
            return self._instance_reference == other._instance_reference and self._identifier == other._identifier
        return False

    @property
    def declared_instance_type(
        self,
    ) -> type[ProductInstanceManager[Any, RecoveryStateInfo]]:
        raise NotImplementedError()

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def instance_reference(self) -> str:
        return self._instance_reference

    @property
    def instance_name(self) -> str:
        return self._instance_name

    @property
    def decorator_name(self) -> str:
        raise NotImplementedError()

    @property
    def max_execution_time(self) -> int | None:
        return None

    @property
    def transaction_name(self) -> str:
        return self._transaction_name

    def get_instance_url(self, project_url: str, step_name: str) -> str:
        step_url_identifier = python_identifier_to_url_part(step_name)
        instance_url_identifier = python_identifier_to_url_part(self._instance_name)
        return f"{project_url}/steps/{step_url_identifier}/instances/{instance_url_identifier}"

    def get_full_name(self, step_name: str) -> str:
        if "." in self.instance_reference:
            return self.instance_reference
        return f"{step_name}.{self.instance_reference}"

    def resolve_origin_create_instance(self, solution: Solution, referenced_step_name: str) -> CreateInstance:
        raise NotImplementedError()

    def validate(
        self,
        transaction: dict[str, StepSpec],
        this_step_name: str,
    ) -> None: ...

    def parse_field_reference(self, self_step_name: str) -> tuple[str, str]:
        reference_parts = self.instance_reference.split(".")
        num_parts = len(reference_parts)
        if num_parts == 1:
            return (self_step_name, self.instance_reference)
        if num_parts == 2:
            return (reference_parts[0], reference_parts[1])
        raise SolutionLoadException(f"the reference '{self.instance_reference}' contains more than one '.' character")


class CreateInstance(InstanceAttribute):
    def __init__(
        self,
        instance_reference: str,
        instance_manager_type: type[ProductInstanceManager[Any, TRecoveryStateInfo]],
        transaction_name: str,
        identifier: str | None = None,
        max_execution_time: int | None = None,
    ) -> None:
        """
        Provides information about the attributes passed to the @create_instance decorator

        Parameters
        ----------
        instance_reference : str
            Reference to a shared product instance.

            This parameter can contain no period (``.``) characters.
            If it does, then the parameter refers to the shared product instance with the same
            name that was created by another method on the same step as the
            decorated method.

            This parameter can contain a single period (``.``) character
            separating two names where the first is a step name (see Notes) and
            the second name refers to a shared product instance created on
            the named step.

        instance_manager_type : type[ProductInstanceManager]
            The type of the ``InstanceManager`` that is passed in the @create_instance decorator.

        identifier : str, optional
            The first argument passed to the create_instance decorator that triggers the instance construction
            the ``ProductInstanceManager`` object for the shared product instance
            referenced by ``instance_name``.
            If this parameter is not supplied, then the name of the
            referenced instance is used.

        max_execution_time : str, optional
            Amount of time (in seconds) after which an instance managed by Ansys HPS will be
            timed-out by HPS. Passed in the @create_instance decorator.
        """
        super().__init__(instance_reference, transaction_name, identifier)
        self._max_execution_time = max_execution_time
        self._instance_manager_type = instance_manager_type

    @property
    def declared_instance_type(
        self,
    ) -> type[ProductInstanceManager[Any, RecoveryStateInfo]]:
        return self.instance_manager_type

    @property
    def instance_manager_type(
        self,
    ) -> type[ProductInstanceManager[Any, RecoveryStateInfo]]:
        return self._instance_manager_type  # type: ignore

    @property
    def decorator_name(self) -> str:
        return "create_instance"

    @property
    def max_execution_time(self) -> int | None:
        return self._max_execution_time

    @property
    def recovery_state_type(self) -> type[RecoveryStateInfo]:
        # TODO: find a better way to retrieve the type of the recovery state info.
        return self.declared_instance_type._instance_manager_impl_type.recovery_state_info_type  # type: ignore

    def resolve_origin_create_instance(self, solution: Solution, referenced_step_name: str) -> Self:
        return self

    def validate(
        self,
        transaction: dict[str, StepSpec],
        this_step_name: str,
    ) -> None:
        if not self.instance_reference.isidentifier():
            raise SolutionLoadException(
                f"the name in @create_instance '{self.instance_reference}' "
                "is not a valid identifier (use python identifier syntax)",
            )
        if not issubclass(self.instance_manager_type, ProductInstanceManager):  # pyright: ignore
            raise SolutionLoadException(
                f"the instance_manager_type argument of @create_instance for instance {self.instance_reference} "
                "is not derived from ProductInstanceManager.",
            )
        super().validate(transaction, this_step_name)


class Instance(InstanceAttribute):
    def __init__(self, instance_name: str, transaction_name: str, instance_id: str | None = None) -> None:
        super().__init__(instance_name, transaction_name, instance_id)

    @property
    def decorator_name(self) -> str:
        return "instance"

    def resolve_origin_create_instance(self, solution: Solution, referenced_step_name: str) -> CreateInstance:
        step = solution.get_steps_fields()[referenced_step_name]
        create_instance_decorator = step._get_create_instance_by_name()[  # pyright: ignore[reportPrivateUsage]
            self.instance_name
        ]
        return create_instance_decorator
