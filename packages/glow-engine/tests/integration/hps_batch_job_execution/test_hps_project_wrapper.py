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
from pathlib import Path
import re

from ansys.hps.client.jms import JmsApi  # pyright: ignore[reportMissingTypeStubs]
import pytest
import pytest_mock

from ansys.saf.glow._hps_auth.ihps_authenticator import IHpsAuthenticator
from ansys.saf.glow._hps_parametric_studies.api import HpsSimpleProject
from ansys.saf.glow._hps_parametric_studies.project_wrapper import HpsProjectWrapper, ProjectNotFoundError
import tests.mocks.solution_with_hps_python_script.hps_parametric_study as hps_parametric_study_module

METHOD_ASSETS = Path(hps_parametric_study_module.__file__).parent / "method_assets"
pytestmark = [pytest.mark.use_batch_job]


@pytest.mark.parametrize("instance_system_type", [pytest.param("HPS", marks=pytest.mark.use_hps)], indirect=True)
@pytest.mark.usefixtures("hps_authentication")
class TestProjectWrapper:
    def test_exception_raised_when_hps_project_not_initialized(
        self,
        tmp_path: Path,
        hps_authentication: IHpsAuthenticator,
        mocker: pytest_mock.MockerFixture,
    ):
        hps_project = HpsSimpleProject(hps_project_identifier="non_existent_project_id")
        get_projects = mocker.patch.object(JmsApi, "get_projects", return_value=[])
        project_wrapper = HpsProjectWrapper(hps_project, hps_authentication)
        file_id = "02zFYG9EeKvfJdRgwDQxPL"

        with pytest.raises(ProjectNotFoundError, match="Project not found for ID: non_existent_project_id"):
            project_wrapper.copy_file(file_id, tmp_path / "mock_dir")

        get_projects.assert_called_once()

    def test_exception_raised_when_file_not_exists(self, tmp_path: Path, hps_authentication: IHpsAuthenticator):
        hps_project = HpsSimpleProject.start_hps_job(
            input_values={"script": METHOD_ASSETS / "echo_input_sources.py", "x": 3, "y": 5},
            output_parameters={"result": float},
        )
        project_wrap = HpsProjectWrapper(hps_project, hps_authentication)
        file_id = "02zFYT9EeDvjRdRgwxQxPa"
        with pytest.raises(RuntimeError, match=re.escape(f"Unable to find file with id {file_id} in HPS")):
            project_wrap.copy_file(file_id, tmp_path / "mock_dir")

    def test_read_input_file(self, tmp_path: Path, hps_authentication: IHpsAuthenticator):
        hps_project = HpsSimpleProject.start_hps_job(
            input_values={"script": METHOD_ASSETS / "echo_input_sources.py", "x": 3, "y": 5},
            output_parameters={"result": float},
        )
        project_wrap = HpsProjectWrapper(hps_project, hps_authentication)

        with project_wrap._get_project_api() as project_api:  # pyright: ignore[reportPrivateUsage]
            file = project_api.get_files()[0]  # pyright: ignore[reportUnknownMemberType]

        dst_dir = tmp_path / "mock_dir"
        filename = file.evaluation_path if file.evaluation_path else file.name
        dst_file = dst_dir / filename
        project_wrap.copy_file(file.id, dst_dir)
        assert "class EchoInputSources" in dst_file.read_text()

    def test_exception_raised_when_file_not_exists_in_hps(
        self,
        tmp_path: Path,
        hps_authentication: IHpsAuthenticator,
    ):
        hps_project = HpsSimpleProject.start_hps_job(
            input_values={"script": METHOD_ASSETS / "echo_input_sources.py", "x": 3, "y": 5},
            output_parameters={"result": float},
        )
        project_wrap = HpsProjectWrapper(hps_project, hps_authentication)

        with project_wrap._get_project_api() as project_api:  # pyright: ignore[reportPrivateUsage]
            file = project_api.get_files()[2]  # pyright: ignore[reportUnknownMemberType]

        with pytest.raises(RuntimeError, match=re.escape(f"File '{file.name}' ({file.id}) does not exist in HPS.")):
            project_wrap.copy_file(file.id, tmp_path / "mock_dir")

    def test_hps_project_not_exists(self, hps_authentication: IHpsAuthenticator):
        hps_project = HpsSimpleProject()
        project_wrapper = HpsProjectWrapper(hps_project, hps_authentication)
        assert not project_wrapper.exists
