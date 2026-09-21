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

from collections.abc import Generator
from contextlib import contextmanager
import logging

from ansys.hps.client import Client  # pyright: ignore[reportMissingTypeStubs]
from ansys.hps.client.jms import ProjectApi  # pyright: ignore[reportMissingTypeStubs]

from ansys.saf.glow._config.const import (
    GLOW_HPS_HOST,
    GLOW_HPS_PORT,
)
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._executor.local import transaction_local
from ansys.saf.glow._hps_auth.hps_authenticator import create_hps_authenticator
from ansys.saf.glow._hps_auth.ihps_authenticator import IHpsAuthenticator

logger = logging.getLogger(__name__)


class HpsParametricStudySystem:
    @classmethod
    def get_hps_server_url(cls, settings: Settings | None = None) -> str:
        # When this is called during the execution of a transaction, transaction_local
        # already contains settings. However, this can also be called from outside a
        # transaction, for instance, when removing a project. In this cases, settings
        # comes as a parameter.
        settings = getattr(transaction_local, "settings", settings)
        hps_server_url = settings.computed_glow_hps_url  # pyright: ignore[reportOptionalMemberAccess]
        if hps_server_url is None:
            raise RuntimeError(
                "No HPS system is configured. Set the environment variable "
                f"{GLOW_HPS_PORT} and optionally {GLOW_HPS_HOST}, "
                "or pass the hps_server_url argument when starting the job.",
            )

        return hps_server_url

    @classmethod
    @contextmanager
    def get_hps_client(
        cls,
        hps_authenticator: IHpsAuthenticator | None = None,
        settings: Settings | None = None,
        hps_server_url: str | None = None,
        client_id: str | None = None,
    ) -> Generator[Client]:
        hps_server_url = hps_server_url or cls.get_hps_server_url(settings)

        # TODO: should we use settings if transaction_local is not set?
        # like in get_hps_server_url: settings = getattr(transaction_local, "settings", settings)
        internal_hps_authenticator = hps_authenticator or create_hps_authenticator(
            transaction_local.settings,
            transaction_local.access_token,
        )
        if not internal_hps_authenticator:
            raise RuntimeError("HPS authorization not configured.")

        with internal_hps_authenticator.get_hps_client(
            hps_server_url=hps_server_url,
            client_id=client_id,
        ) as hps_client:  # pyright: ignore[reportUnknownVariableType]
            yield hps_client

    @classmethod
    def stop_jobs(
        cls,
        project_id: str,
        hps_authenticator: IHpsAuthenticator | None,
        settings: Settings,
    ) -> None:
        with cls.get_hps_client(hps_authenticator, settings) as hps_client:
            project_api = ProjectApi(hps_client, project_id)
            project_jobs = project_api.get_jobs()  # pyright: ignore[reportUnknownMemberType]
            for job in project_jobs:
                job.eval_status = "aborted"
            project_api.update_jobs(project_jobs)

            job_definitions = project_api.get_job_definitions()  # pyright: ignore[reportUnknownMemberType]
            for definition in job_definitions:
                definition.active = False
            project_api.update_job_definitions(job_definitions)
