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
from pathlib import Path
from typing import Any, Generic, TypeVar, cast

import httpx2

from ansys.saf.glow._client.project_proxy import ProjectProxy
from ansys.saf.glow._config.const import Deployment
from ansys.saf.glow._config.settings import Settings
from ansys.saf.glow._core.client_exceptions import check
from ansys.saf.glow._core.gql import GqlClientConnectionPool
from ansys.saf.glow._core.solution import Solution
from ansys.saf.glow._telemetry.inject_trace_http_transport import InjectTraceTransport

T = TypeVar("T", bound=Solution)

logger = logging.getLogger(__name__)


class Client(Generic[T]):
    """Client for enabling access to a remote GLOW Solution.

    Parameters
    ----------
    solution_type: type[Solution]
        The Solution that is being implemented remotely.
        Must be a class that has been derived from :py:class:`~ansys.saf.glow.solution.Solution`.
    url: str
        The URL of the remote Solution GLOW REST API
    external_url: optional[str]
        The URL of the remote Solution GLOW REST API from outside the UI container (e.g. a browser)
        in on-premises deployments.
    access_token: optional[str]
        An optional access token containing the security credentials for a login session.
    api_key: optional[str]
        An optional API key sent via the ``x-api-key`` header. Takes precedence over ``access_token``.
    """

    def __init__(
        self,
        solution_type: type[T],
        url: str,
        external_url: str | None = None,
        access_token: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """Construct a client for the server supporting a specified
        :py:class:`~ansys.saf.glow.solution.Solution` derived class served from a specified URL."""
        self._solution_type = solution_type
        self._url = url
        self._external_url = external_url if external_url else url
        headers: dict[str, str] = {}

        self._settings = Settings(glow_solution_definition=self._solution_type.__module__)
        self._project_files_dir = self._settings.computed_ui_project_files_directory
        if api_key:
            headers["x-api-key"] = api_key
        elif access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        self._access_token = access_token
        self._http_client = httpx2.Client(timeout=300, transport=InjectTraceTransport(), headers=headers)
        if api_key:
            self._graphql_client = GqlClientConnectionPool(url=f"{url}/graphql", api_key=api_key)
        else:
            self._graphql_client = GqlClientConnectionPool(url=f"{url}/graphql", access_token=access_token)
        self._context_mgr_used = False
        self._created_project_proxies: dict[str, ProjectProxy] = {}

    def __enter__(self):
        self._context_mgr_used = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # type: ignore
        self.close()

    @property
    def http_client(self):
        """The http client used to communicate with the GLOW REST API."""
        return self._http_client

    def close(self):
        """Close the transport and proxies."""
        for proxy in self._created_project_proxies.values():
            # close storage scopes on exit so that gc can be triggered.
            if proxy._context_mgr_storage_scope and not proxy._deleted:  # pyright: ignore[reportPrivateUsage]
                proxy._context_mgr_storage_scope.__exit__(None, None, None)  # pyright: ignore[reportPrivateUsage]
        self._http_client.close()

    def create_project(self, display_name: str, description: str = "") -> T:
        """Create a new project with the specified ``display_name``.
        Return a Solution instance with the same fields and
        methods as the Solution specified in the ``Client`` constructor.

        Parameters
        ----------
        display_name : str
            The project name displayed to the user.
        description : str, optional
            The project description. Defaults to an empty string.

        Returns
        -------
        ``T derived from ansys.saf.glow.solution.Solution``
            A Solution instance with the same fields and methods as the
            Solution specified in the ``Client`` constructor.
        """
        response = self._http_client.post(
            f"{self._url}/projects",
            json={"display_name": display_name, "description": description},
        )
        check(response)
        project_resource_name = response.json()["name"]
        return self._create_project_proxy(project_resource_name)

    def import_project(self, safx_path: Path, display_name: str) -> T:
        """Import the given ``.safx`` project archive with the specified
        ``display_name`` and open it.

        Parameters
        ----------
        safx_path : Path
            The path of to the safx project file.

            (A ``.safx`` project file is an archive of a ``.sap`` project with its associated project directory.)

        display_name : str
            The project name displayed to the user.

        Returns
        -------
        ``T derived from ansys.saf.glow.solution.Solution``
            A Solution instance for the imported file
            with the same fields and methods as the Solution specified in the
            ``Client`` constructor.
        """

        with safx_path.open("rb") as f:
            response = self._http_client.post(
                f"{self._url}/projects:import",
                files={"safx_file": f},
                data={"display_name": display_name},
            )
        check(response)
        project_resource_name = response.json()["name"]
        return self._create_project_proxy(project_resource_name)

    def get_project(self, name: str) -> T:
        """Return the Solution instance for a project specified by its
        resource name (``projects/<project_id>``).

        Parameters
        ----------
        name : str
            Resource name of an existing project.

            Has the form ``projects/<project_id>``.

        Returns
        -------
        ``T derived from ansys.saf.glow.solution.Solution``
            Solution instance for the project referred to by ``name``
            with the same fields and methods as the Solution specified in the
            ``Client`` constructor.
        """
        return self._create_project_proxy(name)

    def upgrade_project(self, name: str) -> T:
        """Upgrade the version of the Solution instance for a project specified
        by its resource name (``projects/<project_id>``).

        Parameters
        ----------
        name : str
            Resource name of an existing project.

            Has the form ``projects/<project_id>``.

        Returns
        -------
        ``T derived from ansys.saf.glow.solution.Solution``
            Solution instance for the project referred to by ``name``
            with the same fields and methods as the Solution specified in the
            ``Client`` constructor.
        """
        r = self._http_client.post(f"{self._url}/{name}:upgrade")
        check(r)
        return self._create_project_proxy(name)

    def list_projects(
        self,
        page_size: int | None = None,
        page: int | None = None,
        order_by: str | None = None,
        filter: str | None = None,  # noqa: A002
    ) -> Any:
        """List projects with pagination, ordering, and optional filtering.
        By default, returns the first page of results with a maximum of 100 projects per page.

        Parameters
        ----------
        page_size : optional, int
            The maximum number of projects to return in the response. If not specified, defaults to returning
            at most 100 projects. Values above 100 will be coerced to 100.

        page : optional, int
            The page number to return (1-indexed). If not specified, defaults to returning the first page.

        order_by : optional, str
            Comma-separated list of fields to order by.
            The default sorting order is ascending.
            To specify descending order for a field, append a " desc" suffix;
            for example: ``"date_modified desc, name"``.

            Supported fields are ``display_name``, ``description``, ``date_created``,
            ``date_modified``, and ``name``.

        filter : optional, str
            A filter expression to narrow down the listed projects. Follows the syntax:
            ``<field> <operator> <value> [AND <field> <operator> <value>]...``

            Supported fields:
              - ``display_name``: Only supports ``=`` (case-insensitive, contains match).
              - ``description``: Only supports ``=`` (case-insensitive, contains match).
              - ``date_created``: Supports ``=``, ``!=``, ``<``, ``>``, ``<=``, ``>=``.
              - ``date_modified``: Supports ``=``, ``!=``, ``<``, ``>``, ``<=``, ``>=``.

            Date values must be ISO 8601 strings (e.g., ``2024-01-15T00:00:00``, ``2024-01-15``).

            Examples:
              - ``"display_name = Motor"``
              - ``"description = benchmark"``
              - ``"date_created >= 2024-01-01T00:00:00"``
              - ``"display_name = Motor AND date_created >= 2024-01-01T00:00:00"``

        Returns
        -------
        dict[str, Any]
            JSON response with project information and pagination metadata.

            Example response::

                {
                    "projects": [{"name": "projects/<id>", "display_name": "my project"}],
                    "current_page": 1,
                    "total_pages": 20,
                    "page_size": 100,
                    "total_projects": 2000
                }
        """
        query_params: dict[str, Any] = {
            k: v
            for k, v in {"page_size": page_size, "page": page, "order_by": order_by, "filter": filter}.items()
            if v is not None
        }
        r = self._http_client.get(f"{self._url}/projects", params=query_params)
        check(r)
        return r.json()

    def delete_project(self, name: str) -> None:
        """Delete a project specified by its resource name
        (``projects/<project_id>``).

        Parameters
        ----------
        name : str
            Resource name of an existing project.

            Has the form ``projects/<project_id>``.
        """
        r = self._http_client.delete(f"{self._url}/{name}")
        check(r)
        self._created_project_proxies.pop(name, None)

    def get_schema(self) -> Any:
        """Return the JSON schema structure (dictionary) for the
        Solution passed to the constructor.

        Returns
        -------
        Any
            JSON schema structure (dictionary) for the Solution passed to the constructor.
        """
        r = self._http_client.get(f"{self._url}/schema")
        check(r)
        return r.json()

    def _create_project_proxy(self, name: str) -> T:
        proxy = ProjectProxy(
            name=name,
            solution_type=self._solution_type,
            url=f"{self._url}/{name}",
            external_url=f"{self._external_url}/{name}",
            http_client=self._http_client,
            project_files_dir=self._project_files_dir,
            graphql_client=self._graphql_client,
            settings=self._settings,
            access_token=self._access_token,
            context_mgr_used=self._context_mgr_used,
        )
        self._created_project_proxies[name] = proxy
        return cast("T", proxy)

    @property
    def deployment_type(self) -> Deployment:
        """Return the deployment type derived from the value of the ``GLOW_DEPLOYMENT`` environment variable
        which corresponds to how the server in which the client is running is deployed.

        Returns
        -------
        Deployment
            The deployment type derived from the value of the ``GLOW_DEPLOYMENT`` environment variable
            which corresponds to how the server in which the client is running is deployed.
        """
        return self._settings.glow_deployment
