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

import logging
from typing import TypeVar

from fastapi import APIRouter
from pydantic import BaseModel

from ansys.saf.glow._bdm.multiplexor import SafMultiplexorStorageScopeFactory
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._core.instance.identification import DirectReadOnlyInstanceIdentificationClient, InstanceRecord
from ansys.saf.glow._core.instance.iinstance_system import IProductInstanceSystemFactory
from ansys.saf.glow._core.method_status import MethodState, MethodStatus
from ansys.saf.glow._core.project_files_locator import ProjectFilesLocator
from ansys.saf.glow._core.solution import Solution
from ansys.saf.glow._crud.crud import Crud
from ansys.saf.glow._executor.local import transaction_local
from ansys.saf.glow._hps_auth.interactive_authenticator import HpsInteractiveAuthenticator
from ansys.saf.glow._server.dependencies import (
    CrudDep,
    HpsAuthInfoDep,
    InstanceSystemFactoryDep,
    ProductInstancesTrackerDep,
    RunningMethodsDep,
    SettingsDep,
    get_project_info,
)
from ansys.saf.glow._server.exceptions import BadRequestError
from ansys.saf.glow._server.hps_auth_info import HpsAuthInfo
from ansys.saf.glow._server.product_instances_tracker import ProductInstancesTracker

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=Solution)
PersistenceModelType = TypeVar("PersistenceModelType", bound=BaseModel)

router = APIRouter(
    prefix="/desktop",
    tags=["desktop"],
)


async def _shutdown_product_instances_created_in_this_process(
    product_instances_created_by_this_process: ProductInstancesTracker,
    settings: Settings,
    instance_system_factory: IProductInstanceSystemFactory,
    crud: Crud,
) -> None:
    for instance_info in product_instances_created_by_this_process.get_instances():
        # Recreate an instance manager with the saved information in order to connect to the instance
        # and call shutdown_impl.
        transaction_local.project_directory = settings.computed_project_files_directory / instance_info.project_id
        transaction_local.instance_system_factory = instance_system_factory
        transaction_local.settings = settings
        project_files_directory = ProjectFilesLocator.get_project_files_root(settings)
        multiplexor_storage_factory = SafMultiplexorStorageScopeFactory(
            # Storage factory only used for shutting down instances properly.
            # Instances shouldn't need to use subsystems for cleaning up, so let's only
            # create the primary system without subsystems.
            project_files_dir=str(project_files_directory),
            project_id=instance_info.project_id,
            settings=settings,
        )
        transaction_local.multiplexor_storage_factory = multiplexor_storage_factory
        project_info = await get_project_info(instance_info.project_id, crud)
        transaction_local.project_display_name = project_info.display_name
        recovery_state_info_type = instance_info.instance_attribute.recovery_state_type
        instance_manager = instance_info.instance_attribute.declared_instance_type(
            _instance_identification=DirectReadOnlyInstanceIdentificationClient[recovery_state_info_type](
                instance_info.record,
                recovery_state_info_type,
            ),
        )
        instance_manager_impl = instance_manager._instance_manager_impl  # pyright: ignore[reportPrivateUsage]
        instance_record = InstanceRecord[instance_manager_impl.recovery_state_info_type].model_validate(
            instance_info.record.model_dump(),
        )
        instance_manager_impl.reconnect(instance_record)  # type: ignore
        instance_manager_impl._stop()  # pyright: ignore[reportPrivateUsage]


@router.post(":exit")
async def exit(  # noqa: A001
    crud: CrudDep,
    running_methods: RunningMethodsDep,
    product_instances_created_by_this_process: ProductInstancesTrackerDep,
    settings: SettingsDep,
    instance_system_factory: InstanceSystemFactoryDep,
):
    """Signal to the server that it must terminate and cleanup.

    This must only be used internally on desktop by the orchestrator.
    The goal is to provide a means for the server to cleanup itself
    when a user shuts down the full solution stack simply by closing
    the windows.
    """
    for project_id, method_ids in running_methods.items():
        for method_id in method_ids:
            step_name, method_name = method_id.split(".")
            method_state = MethodState(
                status=MethodStatus.Failed,
                exception_message="The project was closed before the method completed.",
            )
            await crud.update_method_state(project_id, step_name, method_name, method_state)
    running_methods.clear()

    await _shutdown_product_instances_created_in_this_process(
        product_instances_created_by_this_process,
        settings,
        instance_system_factory,
        crud,
    )


@router.get(":hps-auth-info")
async def get_hps_auth_info(
    crud: CrudDep,
    settings: SettingsDep,
    hps_auth_info: HpsAuthInfoDep,
    hps_server_url: str | None = None,
    client_id: str | None = None,
) -> dict[str, str]:
    auth_info_url = hps_server_url or settings.computed_glow_hps_url
    if not auth_info_url:
        raise BadRequestError("HPS system unconfigured.")

    hps_url_authenticated = auth_info_url in hps_auth_info

    if settings.glow_hps_username and settings.glow_hps_password:
        # this can be called from the Client API, without knowing which type of HPS auth
        # is configured. Pass if we don't actually require to acquire tokens.
        # Let HpsAuthInfo handle the default data when no auth tokens have been stored yet.
        auth_info = hps_auth_info[auth_info_url] if hps_url_authenticated else HpsAuthInfo()
        return auth_info.get_auth_data()

    if hps_url_authenticated:
        access_token = hps_auth_info[auth_info_url].get_auth_data()["access_token"]
        token_is_valid = HpsInteractiveAuthenticator.check_token_validity(access_token)

        if token_is_valid:
            logger.info("Reusing existing valid HPS access token...")
            return hps_auth_info[auth_info_url].get_auth_data()
        else:
            logger.info("HPS access token expired or invalid, refreshing token...")
            refresh_token = hps_auth_info[auth_info_url].get_auth_data()["refresh_token"]
            try:
                async with crud.hps_auth_lock():
                    access_token, refresh_token = HpsInteractiveAuthenticator.refresh_token(
                        hps_server_url=auth_info_url,
                        client_id=client_id or settings.glow_hps_client_id,
                        refresh_token=refresh_token,
                    )
                    hps_auth_info[auth_info_url] = HpsAuthInfo()
                    hps_auth_info[auth_info_url].set_auth_data(access_token, refresh_token)
                return hps_auth_info[auth_info_url].get_auth_data()
            except Exception as e:
                logger.warning(f"Failed to refresh HPS token: {e}. Asking user for re-authentication...")
    else:
        logger.info("No existing HPS authentication found, authenticating...")

    async with crud.hps_auth_lock():
        access_token, refresh_token = HpsInteractiveAuthenticator.acquire_token(
            hps_server_url=auth_info_url,
            client_id=client_id or settings.glow_hps_client_id,
        )
        hps_auth_info[auth_info_url] = HpsAuthInfo()
        hps_auth_info[auth_info_url].set_auth_data(access_token, refresh_token)

    return hps_auth_info[auth_info_url].get_auth_data()
