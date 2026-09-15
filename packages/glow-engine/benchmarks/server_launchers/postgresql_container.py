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
import subprocess

import docker  # pyright: ignore[reportMissingTypeStubs]
import yaml

from ansys.saf.glow._utilities.ip_utilities import get_random_free_port

logger = logging.getLogger(__name__)


class PostgresContainer:
    _container_port = 5432
    _max_tries = 10
    _time_sleep_before_try = 2

    def __init__(self, tmp_dir: Path):
        self._tmp_dir = tmp_dir
        self._compose_path = tmp_dir / "docker-compose.yaml"

    def _start_container(self) -> str:
        self._create_compose_file()

        cmd = ["docker", "compose", "-f", self._compose_path.as_posix(), "up", "--detach", "--wait"]
        try:
            subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except subprocess.CalledProcessError as err:
            logger.exception(err.output)
            raise

        return f"postgresql://glow:glow@127.0.0.1:{self._postgres_port}/postgres"

    def _create_compose_file(self) -> None:
        compose_content = {
            "services": {
                "postgres": {
                    "image": "postgres:16.0",
                    "environment": [
                        "POSTGRES_USER=glow",
                        "POSTGRES_PASSWORD=glow",
                    ],
                    "ports": [f"{self._postgres_port}:{self._container_port}"],
                    "volumes": ["postgres:/var/lib/postgresql/data"],
                    "networks": ["postgres"],
                    "healthcheck": {
                        "test": ["CMD", "pg_isready", "-U", "glow"],
                        "interval": "5s",
                        "retries": 20,
                    },
                },
            },
            "networks": {
                "postgres": {
                    "driver": "bridge",
                },
            },
            "volumes": {"postgres"},
        }

        with self._compose_path.open("w", encoding="utf-8") as f:
            yaml.dump(compose_content, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def _cleanup_container(self) -> None:
        cmd = ["docker", "compose", "-f", self._compose_path.as_posix(), "down", "-v"]
        try:
            subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except subprocess.CalledProcessError as err:
            logger.exception(err.output)
            raise

    def _is_docker_running(self):
        try:
            with docker.APIClient() as client:
                client.ping()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def __enter__(self) -> str:
        if not self._is_docker_running():
            raise Exception("Docker is not running.")

        self._postgres_port = get_random_free_port()
        try:
            return self._start_container()
        except Exception:
            self._cleanup_container()
            raise

    def __exit__(self, exc_type, exc_value, traceback):  # type: ignore
        self._cleanup_container()
