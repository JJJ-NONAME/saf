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
from typing import Generic
from urllib.parse import urlparse

from fastapi.encoders import jsonable_encoder
import httpx2

from ansys.saf.glow._core.instance.recoverystate import TRecoveryStateInfo
from ansys.saf.glow._server.schemas import CreateInstanceRequest, InstanceResponse, ModifyInstanceRequest


class CreateInstanceRecord(CreateInstanceRequest[TRecoveryStateInfo]):
    # pydantic doesn't let override mandatory field with Optional
    # so let's create fake ones.
    name: str = "projects/fake/url"
    state_directory_storage_reference: str = ""


class UpdateInstanceRecord(ModifyInstanceRequest[TRecoveryStateInfo]): ...


class InstanceRecord(InstanceResponse[TRecoveryStateInfo]): ...


class AbstractInstanceIdentificationClient(ABC, Generic[TRecoveryStateInfo]):
    """AbstractInstanceIdentificationClient is the interface through
    which the instance manager object obtains information about specific instance
    that it represents. When the instance manager runs in the method it uses a
    implementation of AbstractInstanceIdentificationClient that uses REST to get and set
    the information from the API server.
    """

    @abstractmethod
    def get(self) -> InstanceRecord[TRecoveryStateInfo] | None:
        raise NotImplementedError()

    @abstractmethod
    def add(self, instance_record: CreateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]:
        raise NotImplementedError()

    @abstractmethod
    def update(self, instance_record: UpdateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]:
        raise NotImplementedError()

    @abstractmethod
    def delete(self) -> None:
        raise NotImplementedError()


class UnsharedProductIdentificationClient(AbstractInstanceIdentificationClient[TRecoveryStateInfo]):
    def __init__(self) -> None:
        """Specific implementation of an InstanceIdentificationClient to be used in a unshared context,
        i.e. when the ProductInstanceManager is instantiated within the transaction method."""
        self._instance_record: InstanceRecord[TRecoveryStateInfo] | None = None

    def get(self) -> InstanceRecord[TRecoveryStateInfo] | None:
        return self._instance_record

    def add(self, instance_record: CreateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]:
        record = InstanceRecord(**instance_record.model_dump())
        self._instance_record = record
        return self._instance_record

    def update(self, instance_record: UpdateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]:
        update_data = instance_record.model_dump(exclude_unset=True)
        self._instance_record = self._instance_record.model_copy(update=update_data)  # type: ignore
        return self._instance_record

    def delete(self) -> None:
        self._instance_record = None


class DirectReadOnlyInstanceIdentificationClient(AbstractInstanceIdentificationClient[TRecoveryStateInfo]):
    def __init__(
        self,
        instance: InstanceResponse[TRecoveryStateInfo],
        recovery_state_info_type: type[TRecoveryStateInfo],
    ) -> None:
        self._instance = instance
        self._recovery_state_info_type = recovery_state_info_type

    def get(self) -> InstanceRecord[TRecoveryStateInfo] | None:
        return InstanceRecord[TRecoveryStateInfo](**self._instance.model_dump())

    def update(
        self,
        instance_record: UpdateInstanceRecord[TRecoveryStateInfo],
    ) -> InstanceRecord[TRecoveryStateInfo]: ...

    def add(self, instance_record: CreateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]: ...

    def delete(self) -> None: ...


class InstanceIdentificationClient(AbstractInstanceIdentificationClient[TRecoveryStateInfo]):
    def __init__(
        self,
        instance_identification_url: str,
        http_client: httpx2.Client,
        recovery_state_info_type: type[TRecoveryStateInfo],
        is_create_instance: bool = False,
    ) -> None:
        self._instance_identification_url = instance_identification_url
        self._http_client = http_client
        self._recovery_state_info_type = recovery_state_info_type
        self._is_create_instance = is_create_instance

    def get(self) -> InstanceRecord[TRecoveryStateInfo] | None:
        response = self._http_client.get(
            self._instance_identification_url,
            params={"ignore_not_found": self._is_create_instance},
        )
        if response.status_code in [204, 404]:
            return None
        response.raise_for_status()
        return InstanceRecord[self._recovery_state_info_type].model_validate(response.json())

    def add(self, instance_record: CreateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]:
        instance_record.name = urlparse(self._instance_identification_url).path.lstrip("/")
        response = self._http_client.post(
            self._instance_identification_url,
            json=jsonable_encoder(instance_record.model_dump()),  # encoder needed for entityhandle UUID
        )
        response.raise_for_status()
        return InstanceRecord[self._recovery_state_info_type].model_validate(response.json())

    def update(self, instance_record: UpdateInstanceRecord[TRecoveryStateInfo]) -> InstanceRecord[TRecoveryStateInfo]:
        response = self._http_client.patch(
            self._instance_identification_url,
            json=jsonable_encoder(instance_record.model_dump()),  # encoder needed for entityhandle UUID
        )
        response.raise_for_status()
        return InstanceRecord[self._recovery_state_info_type].model_validate(response.json())

    def delete(self) -> None:
        response = self._http_client.delete(self._instance_identification_url)
        response.raise_for_status()
