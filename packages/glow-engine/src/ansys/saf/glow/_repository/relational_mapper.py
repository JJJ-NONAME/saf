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

import uuid

from ansys.saf.glow._core.instance.recoverystate import RecoveryStateInfo
from ansys.saf.glow._repository.relational_models import BdmLock, Instance, MethodState, Project
import ansys.saf.glow._server.models as models
from ansys.saf.glow._server.schemas import InstanceResponse, ProjectInfo


def create_project_info(project_in_database: Project) -> ProjectInfo:
    project_info = ProjectInfo(
        name=f"projects/{project_in_database.id}",
        date_created=project_in_database.date_created,
        date_modified=project_in_database.date_modified,
        display_name=project_in_database.project_display_name,
        description=project_in_database.description,
    )
    return project_info


def create_method_state(method_state: MethodState) -> models.MethodState:
    return models.MethodState(
        # not sure what's happening seems sqlalchmey returns empty strings for some null cases ???
        status=method_state.status,
        result=method_state.result,
        status_code=method_state.status_code,
        exception_message=method_state.exception_message,
        exception_stack=method_state.exception_stack,
    )


def create_instance_model(instance_url: str, instance: Instance) -> models.Instance[RecoveryStateInfo]:
    return models.Instance(
        name=instance_url,
        pim_name=instance.pim_name,
        service_name=instance.service_name,
        max_execution_time=instance.max_execution_time,
        recovery_state_info=instance.recovery_state_info,
        product_version=instance.product_version,
    )


def create_bdm_lock(lock_in_database: BdmLock) -> models.BdmLockModel:
    return models.BdmLockModel(
        id=uuid.UUID(lock_in_database.external_id),
        expiration_date=lock_in_database.expiration_date,
    )


def create_instance_response(
    instance_url: str,
    instance: Instance,
) -> InstanceResponse[RecoveryStateInfo]:
    return InstanceResponse(
        **create_instance_model(instance_url, instance).model_dump(),
    )
