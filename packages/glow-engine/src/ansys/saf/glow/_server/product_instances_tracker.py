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

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from ansys.saf.glow._core.instance.attribute import CreateInstance
from ansys.saf.glow._core.instance.recoverystate import RecoveryStateInfo, TRecoveryStateInfo
from ansys.saf.glow._core.solution import Solution
from ansys.saf.glow._server.schemas import InstanceResponse

T = TypeVar("T", bound=Solution)


class TrackedInstanceInfo(BaseModel, Generic[TRecoveryStateInfo], arbitrary_types_allowed=True):
    record: InstanceResponse[TRecoveryStateInfo]
    project_id: str
    instance_attribute: CreateInstance

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.record.pim_name == other.record.pim_name

    def __hash__(self) -> int:
        return hash(self.record.pim_name)


class ProductInstancesTracker(ABC):
    """This is an interface to an object that is recording product
    instances."""

    @abstractmethod
    def record_instance(
        self,
        solution_type: type[T],
        step_name: str,
        instance_id: str,
        instance: InstanceResponse[RecoveryStateInfo],
        project_id: str,
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def remove_instance(self, pim_name: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_instances(self) -> set[TrackedInstanceInfo[RecoveryStateInfo]]:
        raise NotImplementedError()


class InactiveProductInstancesTracker(ProductInstancesTracker):
    """This is an empty implementation of ProductInstancesTracker for
    environments where tracking is not needed but the calling code
    doesn't need to know whether tracking is active or not."""

    def record_instance(
        self,
        solution_type: type[T],
        step_name: str,
        instance_id: str,
        instance: InstanceResponse[TRecoveryStateInfo],
        project_id: str,
    ) -> None:
        pass

    def remove_instance(self, pim_name: str) -> None:
        pass

    def get_instances(self) -> set[TrackedInstanceInfo[RecoveryStateInfo]]:
        return set()


class ActiveProductInstancesTracker(ProductInstancesTracker):
    """This is an complete implementation of ProductInstancesTracker
    for environments where tracking is required."""

    def __init__(self) -> None:
        self._instances: set[TrackedInstanceInfo[RecoveryStateInfo]] = set()

    def record_instance(
        self,
        solution_type: type[T],
        step_name: str,
        instance_id: str,
        instance: InstanceResponse[TRecoveryStateInfo],
        project_id: str,
    ) -> None:
        step_type = solution_type.get_steps_fields()[step_name]
        create_instance_attribute = step_type._get_create_instance_by_name().get(  # pyright: ignore[reportPrivateUsage]
            instance_id,
        )
        if create_instance_attribute is None:
            raise RuntimeError(
                f"Unable to resolve instance manager type for instance '{instance_id}' on step '{step_name}'",
            )
        existing_instance = next((inst for inst in self._instances if inst.record.name == instance.name), None)
        if existing_instance:
            self._instances.remove(existing_instance)
        tracked_instance = TrackedInstanceInfo[TRecoveryStateInfo](
            record=instance,
            project_id=project_id,
            instance_attribute=create_instance_attribute,
        )
        self._instances.add(tracked_instance)  # type: ignore

    def remove_instance(self, pim_name: str) -> None:
        instance_to_remove = next(
            (
                existing_instance
                for existing_instance in self._instances
                if existing_instance.record.pim_name == pim_name
            ),
            None,
        )
        if instance_to_remove:
            self._instances.remove(instance_to_remove)

    def get_instances(self) -> set[TrackedInstanceInfo[RecoveryStateInfo]]:
        return self._instances
