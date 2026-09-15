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
from pathlib import Path
import tempfile
from typing import Any
import uuid

from ansys.hps.client.jms import (  # pyright: ignore[reportMissingTypeStubs]
    File,
    JmsApi,
    Job,
    JobDefinition,
    Project,
    ProjectApi,
    ResourceRequirements,
    SuccessCriteria,
    TaskDefinition,
)

from ansys.saf.glow._core.instance.healthcheck import create_health_client_factory
from ansys.saf.glow._core.instance.hps_job_script_str import HPS_JOB_SCRIPT_CONTENT
from ansys.saf.glow._core.instance.iinstance_system import (
    GenericProductInstance,
    IHealthClientFactory,
    IProductInstance,
    IProductInstanceService,
    IProductInstanceSystem,
    IProductInstanceSystemFactory,
    IProductInstanceVersionDefinition,
)
from ansys.saf.glow._hps_auth.hps_authentication_type import HpsAuthenticationType
from ansys.saf.glow._hps_auth.ihps_authenticator import IHpsAuthenticator

logger = logging.getLogger(__name__)


class HpsProductInstanceService(IProductInstanceService):
    def __init__(self, connection_data: dict[str, str]) -> None:
        self._connection_data = connection_data
        self._port = int(self._connection_data["port"])
        self._host = self._connection_data["host"]
        self._uds_id = self._connection_data["uds_id"] or None
        self._uds_dir = self._connection_data["uds_dir"] or None
        self._secure_flags = self._connection_data["secure_flags"] or None

    @property
    def port(self) -> int:
        return self._port

    @property
    def host(self) -> str:
        return self._host

    @property
    def uds_id(self) -> str | None:
        return self._uds_id

    @property
    def uds_dir(self) -> str | None:
        return self._uds_dir

    @property
    def secure_flags(self) -> str | None:
        return self._secure_flags


class HpsProductInstance(GenericProductInstance):
    def __init__(
        self,
        hps_authenticator: IHpsAuthenticator,
        hps_uri: str,
        project_id: str,
        job_definition_id: Any,
        health_client_factory: IHealthClientFactory,
        service_name: str,
        product_name: str,
        product_version: str,
    ) -> None:
        self._hps_authenticator = hps_authenticator
        self._hps_uri = hps_uri
        self._project_id = project_id
        self._job_definition_id = job_definition_id
        self._product_name = product_name
        self._product_version = product_version
        super().__init__(health_client_factory, service_name, wait_attempts=240)

    @property
    def name(self) -> str:
        return f"instances/{self._product_name}/{self._product_version}/{self._job_definition_id}"

    @property
    def definition_name(self) -> str:
        return HpsProductInstanceVersionDefinition.get_name(self._product_name, self._product_version)

    @contextmanager
    def get_project_api(self) -> Generator[ProjectApi, None, None]:
        with self._hps_authenticator.get_hps_client(
            self._hps_uri,
        ) as hps_client:  # pyright: ignore[reportUnknownVariableType]
            yield ProjectApi(hps_client, self._project_id)  # pyright: ignore[reportUnknownArgumentType]

    def _get_job_definition(self, project_api: ProjectApi) -> JobDefinition:
        return project_api.get_job_definitions(id=self._job_definition_id, fields="all")[0]  # type: ignore

    def wait_for_ready(self) -> None:
        # assume a single service
        self._wait(
            lambda: len(self.services) == 1,
            lambda: None,
            "wait_for_ready timed out waiting for HPS job to publish connection information",
        )
        self._wait_for_healthy()

    @property
    def version(self) -> str:
        return self._product_version

    @property
    def services(self) -> dict[str, IProductInstanceService]:
        with self.get_project_api() as project_api:
            # here we are assuming there is only one service
            job_definition = self._get_job_definition(project_api)
            task_definition_ids = job_definition.task_definition_ids  # type: ignore
            task_definition_id = task_definition_ids[0]  # type: ignore
            tasks = project_api.get_tasks(task_definition_id=task_definition_id, fields="all")  # type: ignore

        if len(tasks) != 1:
            raise RuntimeError(f"HPS instance not correctly configured got {len(tasks)=}")

        task = tasks[0]
        connection_data = task.custom_data  # type: ignore
        if connection_data is None:  # type: ignore
            return {}
        service = HpsProductInstanceService(connection_data)  # type: ignore
        return {self._service_name: service}

    def delete(self, missing_ok: bool = False) -> None:
        with self.get_project_api() as project_api:
            job = self.get_running_or_pending_job(project_api)
            if not job:
                if missing_ok:
                    return
                raise RuntimeError("Instance not found, cannot be deleted.")

            job.eval_status = "aborted"
            project_api.update_jobs([job])

            if self.get_running_or_pending_job(project_api) is not None:
                raise RuntimeError("job not aborted as expected")

            job_definition = self._get_job_definition(project_api)
            job_definition.active = False
            project_api.update_job_definitions([job_definition])
        self._wait_for_removal()

    def get_running_or_pending_job(self, project_api: ProjectApi) -> Job | None:
        jobs = project_api.get_jobs(job_definition_id=self._job_definition_id)  # type: ignore
        if not jobs:
            return None

        job = jobs[0]
        if job.eval_status in ["evaluated", "failed", "aborted", "timeout"]:
            return None

        return job


class HpsProductInstanceVersionDefinition(IProductInstanceVersionDefinition):
    def __init__(self, product_name: str, product_version: str) -> None:
        self._product_name = product_name
        self._version = product_version

    @classmethod
    def get_name(cls, product_name: str, product_version: str) -> str:
        return f"{product_name} : {product_version}"

    @property
    def name(self) -> str:
        return self.get_name(self._product_name, self._version)

    @property
    def product_version(self) -> str:
        return self._version


class HpsSystem(IProductInstanceSystem):
    GLOW_PRODUCT_INSTANCES_HPS_PROJECT_NAME = "GLOW Product Instances"

    def __init__(self, uri: str, hps_authenticator: IHpsAuthenticator) -> None:
        self._uri = uri
        self._hps_authenticator = hps_authenticator

    @property
    def auth_type(self) -> HpsAuthenticationType:
        return self._hps_authenticator.auth_type

    def list_definitions(self, product_name: str) -> list[IProductInstanceVersionDefinition]:
        return [
            HpsProductInstanceVersionDefinition(product_name, version)
            for version in self._configurations_manager.list_versions(product_name)
        ]

    def _create_file_from_content(self, project_api: ProjectApi, content: str, file_name: str) -> File:
        with tempfile.TemporaryDirectory() as directory_name:
            hps_input_file = Path(directory_name) / file_name
            hps_input_file.write_text(content)
            file = File(
                name=file_name,
                evaluation_path=file_name,
                type="text/plain",
                src=hps_input_file.as_posix(),
            )
            files = project_api.create_files([file])
            file_with_id = files[0]
            return file_with_id

    def _get_first_project(self, jms_api: JmsApi) -> Project | None:
        projects = jms_api.get_project_by_name(self.GLOW_PRODUCT_INSTANCES_HPS_PROJECT_NAME)

        if not isinstance(projects, list):
            return projects

        first_project: Project | None = None
        for project in projects:
            if first_project is None or first_project.creation_time > project.creation_time:
                first_project = project

        return first_project

    def create_instance(
        self,
        product_name: str,
        max_execution_time: int,
        product_version: str | None = None,
    ) -> IProductInstance:
        product_version, version_configuration = self._configurations_manager.get_version_configuration(
            product_name,
            product_version,
        )
        with self._hps_authenticator.get_hps_client(
            hps_server_url=self._uri,
        ) as hps_client:  # pyright: ignore[reportUnknownVariableType]
            jms_api = JmsApi(hps_client)  # pyright: ignore[reportUnknownArgumentType]
            proj = self._get_first_project(jms_api)

            if proj is None:
                project_specification = Project(
                    name=self.GLOW_PRODUCT_INSTANCES_HPS_PROJECT_NAME,
                    priority=1,
                    active=True,
                )
                created_project = jms_api.create_project(project_specification)
                proj = self._get_first_project(jms_api)

                if proj is None:
                    raise RuntimeError("unable to find created project")

                if proj.id != created_project.id:  # type: ignore
                    jms_api.delete_project(created_project)  # type: ignore

            project_id: str = proj.id  # type: ignore
            project_api = ProjectApi(hps_client, project_id)  # pyright: ignore[reportUnknownArgumentType]

            # we upload a new script each time because the project in HPS is reused for different
            # versions of GLOW. We don't try to update the file because an old version may be being executed
            # at the time of the upgrade.
            script_file = self._create_file_from_content(
                project_api,
                HPS_JOB_SCRIPT_CONTENT,
                f"hps_job_script_{uuid.uuid4()}.py",
            )
            script_file_id = script_file.id  # type: ignore
            name = f"{product_name}-{product_version}-GLOW-Instance"
            environment = version_configuration.environment
            if version_configuration.enable_secure_flags:
                environment["_GLOW_LINUX_LOCAL_SECURE_FLAGS"] = version_configuration.linux_local_secure_flags
                environment["_GLOW_LINUX_UDS_ID"] = version_configuration.linux_uds_id
                environment["_GLOW_WINDOWS_LOCAL_SECURE_FLAGS"] = version_configuration.windows_local_secure_flags
                environment["_GLOW_INSECURE_FLAGS"] = version_configuration.insecure_flags
                environment["_GLOW_REMOTE_SECURE_FLAGS"] = version_configuration.remote_secure_flags

            task_def = TaskDefinition(
                name=name,
                software_requirements=version_configuration.software_requirements,  # type: ignore
                execution_command=version_configuration.execution_command,
                resource_requirements=ResourceRequirements(
                    num_cores=1,  # cores seem to be mandatory even if typed as optional
                ),
                execution_level=0,
                input_file_ids=[script_file_id],
                environment=environment,
                execution_context={},
                # TODO - consider removing max_execution_time, shouldn't be required with GLOW driven GC
                #        (support for omission for indefinite execution in next version of HPS evaluator).
                #        removing max_execution_time requires GLOW driven GC to be implemented.
                max_execution_time=max_execution_time,
                success_criteria=SuccessCriteria(return_code=0),
            )
            task_def.use_execution_script = True
            task_def.execution_script_id = script_file_id
            task_def = project_api.create_task_definitions([task_def])[0]
            job_def = JobDefinition(name=name, active=True)
            task_def_id = task_def.id  # type: ignore
            job_def.task_definition_ids = [task_def_id]
            job_def = project_api.create_job_definitions([job_def])[0]
            job_def_id = job_def.id  # type: ignore
            jobs = [Job(name=name, eval_status="pending", job_definition_id=job_def_id)]
            project_api.create_jobs(jobs)
            health_client_factory = create_health_client_factory(version_configuration)
            instance = HpsProductInstance(
                self._hps_authenticator,
                self._uri,
                project_id,
                job_def_id,
                health_client_factory,
                version_configuration.service_name,
                product_name,
                product_version,
            )

        try:
            instance.wait_for_ready()
        except Exception:
            try:
                logger.error(f"The product {product_name} failed to initialize.")
                instance.delete(missing_ok=True)  # if job failed, it will be already not running or pending.
            finally:
                raise

        return instance

    def get_instance(self, instance_name: str) -> IProductInstance | None:
        if instance_name == "":
            return None

        instance_name_parts = instance_name.split("/")

        if len(instance_name_parts) != 4:
            raise RuntimeError(
                f"unable to parse instance name. {instance_name=} "
                "expecting name in the form instances/<product name>/<version>/<id>",
            )

        product_name = instance_name_parts[1]
        product_version = instance_name_parts[2]
        job_def_id = instance_name_parts[3]

        _, version_configuration = self._configurations_manager.get_version_configuration(product_name, product_version)

        with self._hps_authenticator.get_hps_client(
            hps_server_url=self._uri,
        ) as hps_client:  # pyright: ignore[reportUnknownVariableType]
            jms_api = JmsApi(hps_client)  # pyright: ignore[reportUnknownArgumentType]
            proj = self._get_first_project(jms_api)

            # if there is no project then no instances have been created
            if proj is None:
                return None

            project_id: str = proj.id  # type: ignore
            project_api = ProjectApi(hps_client, project_id)  # pyright: ignore[reportUnknownArgumentType]

            job_definitions = project_api.get_job_definitions(id=job_def_id, fields="all")  # type: ignore

            # if there is no job definition then the instance isn't known to the system
            if not job_definitions:
                return None

            health_client_factory = create_health_client_factory(version_configuration)
            instance = HpsProductInstance(
                self._hps_authenticator,
                self._uri,
                project_id,
                job_def_id,
                health_client_factory,
                version_configuration.service_name,
                product_name,
                product_version,
            )

            # the instance is not known to the system if it has been shutdown
            if instance.get_running_or_pending_job(project_api) is None or not instance.is_healthy():
                return None

        return instance

    def close(self) -> None:
        pass


class HpsSystemFactory(IProductInstanceSystemFactory):
    def __init__(self, hps_authenticator: IHpsAuthenticator) -> None:
        self._hps_authenticator = hps_authenticator

    def create_system(self, uri: str) -> IProductInstanceSystem:
        return HpsSystem(uri, self._hps_authenticator)
