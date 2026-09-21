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

from collections.abc import Callable

from fastapi import status
from fastapi.testclient import TestClient
from httpx2 import Response
import pytest

from ansys.saf.glow._config.settings import DatabaseType
from tests.mocks.solutions import minimal_solution

pytestmark = pytest.mark.parametrize(
    "settings",
    [
        {"glow_database_type": DatabaseType.Sqlite},
        {"glow_database_type": DatabaseType.PostgreSql},
    ],
    ids=["sqlite", "postgres"],
    indirect=True,
)
solution = minimal_solution


@pytest.mark.parametrize("str_field", ["display_name", "description"])
@pytest.mark.parametrize(
    ("filter_expr", "matching_projects"),
    [
        ("{str_field} = nonexistent", None),
        ("{str_field} = alpha", {"AlPhA", "Project Alpha"}),
        ("{str_field}=alpha", {"AlPhA", "Project Alpha"}),
        ('{str_field} = "alpha"', {"AlPhA", "Project Alpha"}),
        ("{str_field} = 'alpha'", {"AlPhA", "Project Alpha"}),
        ("{str_field} = 'ject alpha'", {"Project Alpha"}),
    ],
    ids=["no_match", "no_quotes", "no_spaces_around_equals", "double_quotes", "single_quotes", "with_spaces_in_value"],
)
def test_list_projects_filter_by_str_field(
    client: TestClient,
    create_project: Callable[[str, str], Response],
    str_field: str,
    filter_expr: str,
    matching_projects: set[str] | None,
):
    """Test that filtering by a string field (display_name, description) uses case insensitive substring matching."""
    create_project("AlPhA", "Description for AlPhA")
    create_project("Al PhA", "Description for Al PhA")  # should match the whole substring continuously, so it's skipped
    create_project("Project Alpha", "Description for Project Alpha")
    create_project("Beta", "Description for Beta")
    create_project("Gamma", "Description for Gamma")

    response = client.get("/projects", params={"filter": filter_expr.format(str_field=str_field)})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total_projects"] == (len(matching_projects) if matching_projects is not None else 0)
    assert data["total_pages"] == 1
    if not matching_projects:
        assert not data["projects"]
    else:
        assert {p["display_name"] for p in data["projects"]} == matching_projects


@pytest.mark.parametrize("date_field", ["date_created", "date_modified"])
@pytest.mark.parametrize(
    ("filter_expr", "matching_projects"),
    [
        ("{date_field} > {third_date}", None),
        ("{date_field} >= {third_date}", {"Recent Project"}),
        ("{date_field} <= '{first_date}'", {"Old Project"}),
        ('{date_field} > "{second_date}"', {"Recent Project"}),
        ("{date_field}<{second_date}", {"Old Project"}),
        ("{date_field} = {first_date}", {"Old Project"}),
        ("{date_field} != {first_date}", {"Boundary Project", "Recent Project"}),
    ],
    ids=[
        "no_match",
        "date_created_gte",
        "date_created_lte_double_quotes",
        "date_created_gt_single_quotes",
        "date_created_lt_no_spaces_around_operator",
        "date_created_eq",
        "date_created_ne",
    ],
)
def test_list_projects_filter_by_date_created_or_modified(
    client: TestClient,
    create_project: Callable[[str], Response],
    date_field: str,
    filter_expr: str,
    matching_projects: set[str] | None,
):
    """Test filtering projects by date_created or date_modified."""
    first_response = create_project("Old Project")
    first_date = first_response.json()["date_created"]  # upon creation date_created and date_modified are the same
    second_response = create_project("Boundary Project")
    second_date = second_response.json()["date_created"]
    third_response = create_project("Recent Project")
    third_date = third_response.json()["date_created"]
    filter_str = filter_expr.format(
        date_field=date_field,
        first_date=first_date,
        second_date=second_date,
        third_date=third_date,
    )

    response = client.get("/projects", params={"filter": filter_str})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total_projects"] == (len(matching_projects) if matching_projects is not None else 0)
    assert data["total_pages"] == 1
    if not matching_projects:
        assert not data["projects"]
    else:
        assert {p["display_name"] for p in data["projects"]} == matching_projects


def test_list_projects_filter_combined_display_name_and_dates(
    client: TestClient,
    create_project: Callable[[str], Response],
):
    """Test filtering with combined display_name AND date_created AND date_modified conditions."""
    first_response = create_project("Target")
    first_date_created = first_response.json()["date_created"]
    second_response = create_project("Other Two")
    second_date_created = second_response.json()["date_created"]
    third_response = create_project("Target Two")
    # Rename the project to update date_modified
    patch_response = client.patch(f"/{third_response.json()['name']}", json={"display_name": "Target Two Modified"})
    last_date_modified = patch_response.json()["date_modified"]

    # Use a filter that matches name "Target" AND created at or after first_date
    filter_str = f'display_name = "Target" AND date_created >= {first_date_created}'
    response = client.get("/projects", params={"filter": filter_str})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_projects"] == 2
    assert data["total_pages"] == 1
    assert {p["display_name"] for p in data["projects"]} == {"Target", "Target Two Modified"}

    # Use a filter that matches name "Two" AND modified at or before last_date_modified
    filter_str = f'display_name = "Two" AND date_modified <= {last_date_modified}'
    response = client.get("/projects", params={"filter": filter_str})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_projects"] == 2
    assert data["total_pages"] == 1
    assert {p["display_name"] for p in data["projects"]} == {"Other Two", "Target Two Modified"}

    # Use a filter that matches name "Target" AND created at or after second_date_created AND
    # modified at or after last_date_modified
    filter_str = (
        f'display_name = "Target" AND date_created >= {second_date_created} AND date_modified >= {last_date_modified}'
    )
    response = client.get("/projects", params={"filter": filter_str})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_projects"] == 1
    assert data["total_pages"] == 1
    assert {p["display_name"] for p in data["projects"]} == {"Target Two Modified"}


@pytest.mark.parametrize("date_field", ["date_created", "date_modified"])
@pytest.mark.parametrize(
    ("filter_expr", "matching_projects"),
    [
        ("{date_field} >= {second_date} AND {date_field} <= {last_date}", {"Project 1", "Project 2"}),
        ("{date_field} >= {last_date} AND {date_field} <= {first_date}", {}),
    ],
    ids=["last_two", "inverted_range"],
)
def test_list_projects_filter_date_ranges(
    client: TestClient,
    create_project: Callable[[str], Response],
    date_field: str,
    filter_expr: str,
    matching_projects: set[str],
):
    """Test filtering with date ranges of the same field, including inverted ranges that return no results."""
    responses = [create_project(f"Project {i}") for i in range(3)]
    dates = [r.json()["date_created"] for r in responses]
    filter_str = filter_expr.format(
        date_field=date_field,
        first_date=dates[0],
        second_date=dates[1],
        last_date=dates[2],
    )

    response = client.get("/projects", params={"filter": filter_str})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total_projects"] == len(matching_projects)
    assert data["total_pages"] == 1
    if not matching_projects:
        assert not data["projects"]
    else:
        assert {p["display_name"] for p in data["projects"]} == matching_projects


@pytest.mark.parametrize(
    ("filter_expr", "error_message"),
    [
        ("invalid_field = value", "Input should be 'display_name', 'description', 'date_created' or 'date_modified'"),
        ("display_name ~ value", "Invalid condition syntax: display_name ~ value"),
        ("date_created >= not-a-date", "Invalid isoformat string: 'not-a-date'"),
        ("date_created >= 2024-01-01T00:00:00+00:00", "Datetime values must be timezone-naive"),
        ("date_created >", "Invalid condition syntax: date_created >"),
        ("AND display_name=x", "Invalid condition syntax: AND display_name=x"),
        ("display_name=x AND", "Invalid condition syntax: display_name=x AND"),
        (
            "display_name=x AND AND date_created >= 2024-01-01T00:00:00",
            "Invalid condition syntax: AND date_created >= 2024-01-01T00:00:00",
        ),
    ],
    ids=[
        "invalid_field",
        "invalid_operator",
        "invalid_date",
        "timezone_aware_datetime",
        "missing_value",
        "leading_and",
        "trailing_and",
        "double_and",
    ],
)
def test_list_projects_filter_invalid_filter_returns_422(
    client: TestClient,
    create_project: Callable[[str], Response],
    filter_expr: str,
    error_message: str,
):
    """Test that an invalid filter expression returns 422."""
    create_project("x")
    response = client.get("/projects", params={"filter": filter_expr})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert error_message in response.json()["detail"]


def test_list_projects_filter_empty_string_returns_all(
    client: TestClient,
    create_project: Callable[[str], Response],
):
    """Test that an empty filter string returns all projects."""
    create_project("Alpha")
    create_project("Beta")
    response = client.get("/projects", params={"filter": ""})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_projects"] == 2
    assert data["total_pages"] == 1


def test_list_projects_filter_with_pagination(
    client: TestClient,
    create_project: Callable[[str], Response],
):
    """Test that filter works correctly together with pagination parameters."""
    for i in range(7):
        create_project(f"Target {i}")
    # Create non-matching projects that should be excluded by the filter
    for i in range(3):
        create_project(f"Other {i}")
    # Verify total without filter includes all projects
    response = client.get("/projects")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_projects"] == 10
    assert data["total_pages"] == 1
    assert len(data["projects"]) == 10
    # Verify filtering is applied before pagination: total_projects reflects filtered count
    response = client.get("/projects", params={"filter": "display_name = Target"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_projects"] == 7
    assert data["total_pages"] == 1
    assert len(data["projects"]) == 7
    # All returned projects must match the filter
    assert all("Target" in p["display_name"] for p in data["projects"])
    # Verify using filtering value that produces more than 1 page and asking for second page
    response = client.get("/projects", params={"filter": "display_name = Target", "page_size": 3, "page": 2})
    data = response.json()
    assert data["total_projects"] == 7
    assert data["total_pages"] == 3
    assert data["current_page"] == 2
    assert len(data["projects"]) == 3
    assert all("Target" in p["display_name"] for p in data["projects"])
