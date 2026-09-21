# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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
from typing import Protocol

from ansys.hps.client import Client  # pyright: ignore[reportMissingTypeStubs]
from ansys.hps.client.jms import JmsApi, ProjectApi  # pyright: ignore[reportMissingTypeStubs]
from ansys.hps.client.rms import RmsApi  # pyright: ignore[reportMissingTypeStubs]
import pytest


class GetHpsJobIdsType(Protocol):
    """Interface for a function that retrieves HPS job IDs based on job name, status, and previous job IDs."""

    # Avoid "reportCallIssue" error as Callable doesn't account for
    # default arguments in pylance on arguments passed to methods.
    def __call__(
        self,
        job_name: str,
        status: str,
        previous_job_ids: list[str],
        project_name: str = "GLOW Product Instances",
    ) -> list[str]: ...


@pytest.fixture
def get_hps_job_ids(hps_host: str, hps_port: int | None) -> GetHpsJobIdsType:
    def _get_hps_job_ids(
        job_name: str,
        status: str,
        previous_job_ids: list[str],
        project_name: str = "GLOW Product Instances",
    ) -> list[str]:
        if not hps_port:
            return []

        client = Client(f"https://{hps_host}:{hps_port}/rep", username="repadmin", password="repadmin")
        jms_api = JmsApi(client)

        query_params = {
            "name.contains": project_name,
            "sort": "-creation_time",
        }
        projects = jms_api.get_projects(**query_params)  # type: ignore
        if not projects:
            return []
        job_ids: list[str] = []
        for project in projects:
            project_api = ProjectApi(client, project.id)  # type: ignore
            query_params = {
                "name.contains": job_name,
            }
            if status != "all":
                query_params["eval_status"] = status
            job_ids.extend(
                [
                    str(job.id)
                    for job in project_api.get_jobs(**query_params)  # type: ignore
                    if job.id not in previous_job_ids
                ],
            )
        return job_ids

    return _get_hps_job_ids


@pytest.fixture
def get_hps_job_output(hps_host: str, hps_port: int | None) -> Callable[[str], list[str]]:
    def _get_hps_job_output(job_id: str) -> list[str]:
        if not hps_port:
            return []

        client = Client(f"https://{hps_host}:{hps_port}/rep", username="repadmin", password="repadmin")
        jms_api = JmsApi(client)
        project = jms_api.get_project_by_name("GLOW Product Instances", last_created=True)
        if not project:
            return []
        project_api = ProjectApi(client, project.id)  # type: ignore
        jobs = project_api.get_jobs(id=job_id)  # type: ignore
        if not jobs:
            return []
        files = project_api.get_files(id=jobs[0].file_ids, content=True, name="console_output")  # type: ignore
        if not files:
            return []
        output = str(files[0].content.decode("utf-8"))  # type: ignore
        return output.splitlines()

    return _get_hps_job_output


@pytest.fixture
def get_available_application_on_hps(hps_host: str, hps_port: int | None) -> Callable[[str], str]:
    def _get_available_application_on_hps(application_name: str) -> str:
        if not hps_port:
            raise RuntimeError(f"HPS not running, can't find available {application_name} application.")

        client = Client(f"https://{hps_host}:{hps_port}/rep", username="repadmin", password="repadmin")
        rms_api = RmsApi(client)
        for resource_set in rms_api.get_compute_resource_sets():  # pyright: ignore[reportUnknownMemberType]
            if resource_set.available_applications:
                for application in resource_set.available_applications:
                    if application.name == application_name:
                        # extend in the future if we rather return the list, or prioritize one of the versions
                        # this is enough for the time being.
                        return application.version

        raise RuntimeError(f"No {application_name} application found in HPS scaler.")

    return _get_available_application_on_hps
