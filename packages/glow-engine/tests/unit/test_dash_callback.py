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

import re
from typing import Any
from unittest.mock import PropertyMock

import httpx2
import pytest
from pytest_mock import MockerFixture

from tests.mocks.dash_callbacks import (
    no_pathname,
    return_entity_url,
    return_pathname,
    return_project,
    return_project_different_annotations,
    return_project_display_name,
    return_project_keyword_args,
    return_project_keyword_args_with_trigger,
    return_project_list_outputs_inputs_states,
    return_project_list_outputs_inputs_states_with_trigger,
    return_project_many_outputs_project_in_middle,
    return_project_no_output_project_first,
    return_project_no_typehint,
    return_project_partial_typehints,
    return_project_trigger_after_pathname,
    return_project_trigger_before_pathname,
    return_solution_type_and_steps,
)
from tests.mocks.dash_callbacks_future_annotations import (
    no_pathname__future__,
    return_entity_url__future__,
    return_pathname__future__,
    return_project__future__,
    return_project_different_annotations__future__,
    return_project_display_name__future__,
    return_project_keyword_args__future__,
    return_project_keyword_args_with_trigger__future__,
    return_project_list_outputs_inputs_states__future__,
    return_project_list_outputs_inputs_states_with_trigger__future__,
    return_project_many_outputs_project_in_middle__future__,
    return_project_no_output_project_first__future__,
    return_project_no_typehint__future__,
    return_project_partial_typehints__future__,
    return_project_trigger_after_pathname__future__,
    return_project_trigger_before_pathname__future__,
    return_solution_type_and_steps__future__,
)
from tests.mocks.solution_with_ui.solution.definition import MySolution
from tests.unit.test_client import VALID_API_URLS

GLOW_API_URL = "http://localhost:1234"
PATHNAME = "projects/12345"
_CORE_VALID_PATHNAMES = [
    "projects/my_project_id",  # bare minimal
    "my_solution/projects/my_project_id",  # prefix before projects
    "my_solution_projects/projects/my_project_id",  # prefix containing "projects" as substring
    "projects/my_project_id/whatever",  # sub-path after project_id
    "projects/my_project_id/xyz/sdhyd/xx",  # deep sub-path after project_id
    "my_solution/projects/my_project_id/page/sub",  # prefix + sub-path
    "projects/solutions/projects/my_project_id",  # multiple "projects" segments (rsplit picks rightmost)
    "projects/projects/my_project_id/other",  # multiple "projects" segments + sub-path
    "projects/my_project_id?tab=settings",  # query parameters
    "projects/my_project_id/page?foo=bar&baz=1",  # sub-path + query parameters
    "app/projects/my_project_id?x=1",  # prefix + query parameters
]
VALID_PATHNAMES = (
    _CORE_VALID_PATHNAMES + ["/" + p for p in _CORE_VALID_PATHNAMES] + [p + "/" for p in _CORE_VALID_PATHNAMES]
)
_CORE_INVALID_PATHNAMES = [
    "my_solution/my_project_id",  # no "projects" segment
    "app/no_projects_here/my_project_id",  # "projects" only as substring of another segment
    "no_projects_here/my_project_id/page",  # "projects" as substring + sub-path
    "projects",  # just "projects" with no ID following
    "app/projects",  # prefix + "projects" with no ID
    "projects/?foo=bar",  # "projects" with no ID + query parameters
]
INVALID_PATHNAMES = (
    _CORE_INVALID_PATHNAMES + ["/" + p for p in _CORE_INVALID_PATHNAMES] + [p + "/" for p in _CORE_INVALID_PATHNAMES]
)


@pytest.fixture
def glow_api_url(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> str:
    api_url = getattr(request, "param", GLOW_API_URL)
    if api_url is None:
        api_url = GLOW_API_URL
    monkeypatch.setenv("GLOW_API_URL", api_url)
    return api_url


@pytest.fixture
def glow_external_api_url(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> str:
    external_api_url = getattr(request, "param", GLOW_API_URL)
    if external_api_url is None:
        external_api_url = GLOW_API_URL
    monkeypatch.setenv("GLOW_EXTERNAL_API_URL", external_api_url)
    return external_api_url


@pytest.fixture(autouse=True)
def setup(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    glow_api_url: str,
    glow_external_api_url: str,
) -> None:
    monkeypatch.setenv("GLOW_SOLUTION_DEFINITION", "tests.mocks.solution_with_ui.solution.definition")
    monkeypatch.setenv("GLOW_PORTAL_URL", "http://localhost:1234")
    ctx_mock = mocker.patch("dash.ctx")
    type(ctx_mock).headers = PropertyMock(return_value={})


@pytest.mark.parametrize("func", [return_project, return_project__future__])
def test_callback_decorator(func: Any):
    response = func(1, 2, 3, PATHNAME)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize(
    "func",
    [return_project_many_outputs_project_in_middle, return_project_many_outputs_project_in_middle__future__],
)
def test_callback_many_outputs_project_in_middle(func: Any):
    response = func(1, 2, PATHNAME, 3)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize(
    "func",
    [return_project_list_outputs_inputs_states, return_project_list_outputs_inputs_states__future__],
)
def test_callback_list_outputs_inputs(func: Any):
    response = func(1, 2, 3, PATHNAME)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize(
    "func",
    [return_project_keyword_args, return_project_keyword_args__future__],
)
def test_callback_keyword_args(func: Any):
    response = func(1, 2, 3, PATHNAME)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize(
    "func",
    [return_project_no_output_project_first, return_project_no_output_project_first__future__],
)
def test_callback_no_output_project_first(func: Any):
    response = func(PATHNAME, 1, 2, 3)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize(
    "func",
    [return_pathname, return_pathname__future__],
)
def test_callback_without_project(func: Any):
    response = func(1, 2, 3, PATHNAME)
    assert response == PATHNAME


@pytest.mark.parametrize(
    "func",
    [no_pathname, no_pathname__future__],
)
def test_callback_no_pathname(func: Any):
    response = func(1, 2, 3)
    assert response is None


@pytest.mark.parametrize(
    "func",
    [return_project_no_typehint, return_project_no_typehint__future__],
)
def test_no_typehint(func: Any):
    response = func(1, 2, 3, PATHNAME)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize(
    "func",
    [return_project_partial_typehints, return_project_partial_typehints__future__],
)
def test_partial_typehint(func: Any):
    response = func(1, 2, 3, PATHNAME)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize(
    "func",
    [return_project_trigger_before_pathname, return_project_trigger_before_pathname__future__],
)
def test_callback_trigger_before_pathname(func: Any):
    response = func(2, 3, PATHNAME)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize(
    "func",
    [return_project_trigger_after_pathname, return_project_trigger_after_pathname__future__],
)
def test_callback_trigger_after_pathname(func: Any):
    response = func(2, 3, PATHNAME)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize(
    "func",
    [return_project_keyword_args_with_trigger, return_project_keyword_args_with_trigger__future__],
)
def test_callback_keyword_args_with_trigger(func: Any):
    response = func(2, 3, PATHNAME)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize(
    "func",
    [
        return_project_list_outputs_inputs_states_with_trigger,
        return_project_list_outputs_inputs_states_with_trigger__future__,
    ],
)
def test_callback_list_outputs_inputs_states_with_trigger(func: Any):
    response = func(2, 3, PATHNAME)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize(
    "func",
    [return_project_different_annotations, return_project_different_annotations__future__],
)
def test_callback_different_annotations(func: Any):
    response = func(1, [1, 2], {"key": 5}, (3, {"key": 4}), None, PATHNAME)
    assert response == f"project.url='{GLOW_API_URL}/{PATHNAME}'"


@pytest.mark.parametrize("pathname", VALID_PATHNAMES)
@pytest.mark.parametrize("func", [return_project, return_project__future__])
def test_callback_with_valid_pathnames(func: Any, pathname: str):
    response = func(1, 2, 3, pathname)
    assert response == f"project.url='{GLOW_API_URL}/projects/my_project_id'"


@pytest.mark.parametrize("pathname", INVALID_PATHNAMES)
@pytest.mark.parametrize("func", [return_project, return_project__future__])
def test_callback_with_invalid_pathnames(func: Any, pathname: str):
    with pytest.raises(
        RuntimeError,
        match=re.escape(f"Invalid pathname='{pathname}'. It should contain ``projects/<project_id>``."),
    ):
        func(1, 2, 3, pathname)


@pytest.mark.parametrize("glow_api_url", [None] + VALID_API_URLS, indirect=True)
@pytest.mark.parametrize("func", [return_project, return_project__future__])
def test_configuring_api_url(glow_api_url: str | None, func: Any):
    if glow_api_url is None:
        glow_api_url = GLOW_API_URL
    response = func(1, 2, 3, PATHNAME)
    assert response == f"project.url='{glow_api_url.rstrip('/')}/{PATHNAME}'"


@pytest.mark.parametrize("glow_external_api_url", [None, "http://api.my_solution"], indirect=True)
@pytest.mark.parametrize("func", [return_entity_url, return_entity_url__future__])
def test_configuring_api_external_url(glow_external_api_url: str | None, func: Any):
    if glow_external_api_url is None:
        glow_external_api_url = GLOW_API_URL
    response = func(PATHNAME)
    assert response == f"{glow_external_api_url}/projects/12345/steps/my-step/blobs/file-entity"


@pytest.mark.parametrize(
    "func",
    [return_solution_type_and_steps, return_solution_type_and_steps__future__],
)
def test_solution_type_properly_set_in_underlying_client(func: Any):
    solution_type, solution_steps = func(1, PATHNAME)
    assert solution_type == MySolution
    assert set(solution_steps._solution_type.get_steps_fields().keys()) == {"my_step"}


@pytest.mark.parametrize(
    "func",
    [return_project_display_name, return_project_display_name__future__],
)
def test_auth_header_injected_into_requests(func: Any, mocker: MockerFixture):
    """Test that auth headers from ctx are properly available during callback execution."""

    def mocked_get(request: httpx2.Request) -> httpx2.Response:
        if request.url.path == "/projects/my_project_id_without_auth":
            if not request.headers.get("Authorization"):
                return httpx2.Response(200, json={"display_name": "test_without_auth"})
            else:
                return httpx2.Response(200, json={"display_name": "test_with_unused_auth"})
        else:
            if request.headers.get("Authorization") != "Bearer XXXXX":
                return httpx2.Response(401, json={"error": "Unauthorized"})
            return httpx2.Response(200, json={"display_name": "test_with_auth"})

    mocked_get = mocker.patch.object(httpx2.Client, "_send_single_request", side_effect=mocked_get)

    # Create a mock ctx without headers attribute
    class OldDashCtx:
        pass

    mocker.patch("dash.ctx", new=OldDashCtx())
    response = func(1, "projects/my_project_id_without_auth")
    assert response == "test_without_auth"
    with pytest.raises(RuntimeError, match="""{"error":"Unauthorized"}"""):
        response = func(1, PATHNAME)

    # mock ctx with headers attr but no headers set
    ctx_mock = mocker.patch("dash.ctx")
    type(ctx_mock).headers = PropertyMock(return_value={})
    response = func(1, "projects/my_project_id_without_auth")
    assert response == "test_without_auth"
    with pytest.raises(RuntimeError, match="""{"error":"Unauthorized"}"""):
        response = func(1, PATHNAME)

    # mock ctx with headers set
    type(ctx_mock).headers = PropertyMock(return_value={"Authorization": "Bearer XXXXX"})
    response = func(1, "projects/my_project_id_without_auth")
    assert response == "test_with_unused_auth"
    response = func(1, PATHNAME)
    assert response == "test_with_auth"
