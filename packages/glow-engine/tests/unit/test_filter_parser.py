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

from pydantic import ValidationError
import pytest
import pytest_mock

from ansys.saf.glow._server.filter_parser import (
    ComparisonOp,
    FilterableFields,
    FilteringOperators,
    ParsedProjectFilter,
)


def _to_sql(result: ParsedProjectFilter) -> str:
    expr = result.as_sqlalchemy_expr()
    assert expr is not None
    return str(expr.compile(compile_kwargs={"literal_binds": True}))


@pytest.mark.parametrize(
    "filter_str",
    ["", "   "],
    ids=["empty_string", "whitespace_only"],
)
def test_empty_or_whitespace_returns_empty_conditions(filter_str: str):
    result = ParsedProjectFilter.from_str(filter_str)
    assert result.conditions == []
    assert result.as_sqlalchemy_expr() is None


def test_empty_string_str_representation():
    result = ParsedProjectFilter.from_str("")
    assert str(result) == ""


@pytest.mark.parametrize("str_field", ["display_name", "description"])
@pytest.mark.parametrize(
    ("filter_str", "expected_value", "expected_sql"),
    [
        (
            "{str_field} = MyProject",
            "MyProject",
            "(lower(projects.{str_field}) LIKE '%' || 'myproject' || '%')",
        ),
        (
            '{str_field} = "Project Alpha"',
            "Project Alpha",
            "(lower(projects.{str_field}) LIKE '%' || 'project alpha' || '%')",
        ),
        (
            "{str_field} = 'Project Alpha'",
            "Project Alpha",
            "(lower(projects.{str_field}) LIKE '%' || 'project alpha' || '%')",
        ),
        (
            """{str_field} = "Project 'Alpha'" """,
            "Project 'Alpha'",
            "(lower(projects.{str_field}) LIKE '%' || 'project ''alpha''' || '%')",
        ),
        (
            "{str_field} = MiXeDcAsE",
            "MiXeDcAsE",
            "(lower(projects.{str_field}) LIKE '%' || 'mixedcase' || '%')",
        ),
    ],
    ids=[
        "unquoted",
        "double_quotes",
        "single_quotes",
        "inner_quotes",
        "case_insensitive",
    ],
)
def test_str_field_condition_parsing(str_field: str, filter_str: str, expected_value: str, expected_sql: str):
    result = ParsedProjectFilter.from_str(filter_str.format(str_field=str_field))
    assert len(result.conditions) == 1
    assert result.conditions[0].field == getattr(FilterableFields, str_field)
    assert result.conditions[0].operator == FilteringOperators.eq
    assert result.conditions[0].value == expected_value
    sql_field = "project_display_name" if str_field == "display_name" else str_field
    assert _to_sql(result) == expected_sql.format(str_field=sql_field)


@pytest.mark.parametrize("str_field", ["display_name", "description"])
@pytest.mark.parametrize("operator", [">", "<", ">=", "<=", "!="])
def test_str_field_rejects_non_eq_operators(str_field: str, operator: str):
    with pytest.raises(ValidationError, match="Only '=' is allowed"):
        ParsedProjectFilter.from_str(f"{str_field} {operator} value")


@pytest.mark.parametrize("date_field", ["date_created", "date_modified"])
@pytest.mark.parametrize(
    ("operator", "value", "expected_sql_op_and_value"),
    [
        (FilteringOperators.gte, "2024-01-15T00:00:00", ">= '2024-01-15 00:00:00'"),
        (FilteringOperators.lte, "2024-12-31T23:59:59", "<= '2024-12-31 23:59:59'"),
        (FilteringOperators.gt, "2024-06-01T12:00:00", "> '2024-06-01 12:00:00'"),
        (FilteringOperators.lt, "2024-06-01T12:00:00", "< '2024-06-01 12:00:00'"),
        (FilteringOperators.eq, "2024-06-01T12:00:00", "= '2024-06-01 12:00:00'"),
        (FilteringOperators.neq, "2024-06-01T12:00:00", "!= '2024-06-01 12:00:00'"),
        (FilteringOperators.gte, "2024-01-15", ">= '2024-01-15 00:00:00'"),
    ],
    ids=["gte", "lte", "gt", "lt", "eq", "neq", "date_only"],
)
def test_date_condition_parsing(
    date_field: str,
    operator: FilteringOperators,
    value: str,
    expected_sql_op_and_value: str,
):
    filter_str = f"{date_field} {operator.value} {value}"
    result = ParsedProjectFilter.from_str(filter_str)
    assert len(result.conditions) == 1
    assert result.conditions[0].field == FilterableFields(date_field)
    assert result.conditions[0].operator == operator
    assert result.conditions[0].value == value
    assert _to_sql(result) == f"projects.{date_field} {expected_sql_op_and_value}"


@pytest.mark.parametrize(
    ("filter_str", "expected_value", "expected_sql"),
    [
        (
            "date_created>=2024-01-01T00:00:00",
            "2024-01-01T00:00:00",
            "projects.date_created >= '2024-01-01 00:00:00'",
        ),
        (
            "date_created   >=   2024-01-01T00:00:00",
            "2024-01-01T00:00:00",
            "projects.date_created >= '2024-01-01 00:00:00'",
        ),
        (
            "   display_name = Test   ",
            "Test",
            "(lower(projects.project_display_name) LIKE '%' || 'test' || '%')",
        ),
    ],
    ids=["no_spaces_around_operator", "extra_spaces_around_operator", "leading_trailing_whitespace"],
)
def test_whitespace_tolerance(filter_str: str, expected_value: str, expected_sql: str):
    result = ParsedProjectFilter.from_str(filter_str)
    assert len(result.conditions) == 1
    assert result.conditions[0].value == expected_value
    assert _to_sql(result) == expected_sql


@pytest.mark.parametrize(
    ("filter_str", "expected_count", "expected_fields", "expected_sql"),
    [
        (
            "date_created >= 2024-01-01T00:00:00 AND date_created <= 2024-12-31T23:59:59",
            2,
            [FilterableFields.date_created, FilterableFields.date_created],
            "projects.date_created >= '2024-01-01 00:00:00' AND projects.date_created <= '2024-12-31 23:59:59'",
        ),
        (
            'display_name = "Test" AND date_created >= 2024-01-01T00:00:00 AND date_modified <= 2024-12-31T23:59:59',
            3,
            [FilterableFields.display_name, FilterableFields.date_created, FilterableFields.date_modified],
            "(lower(projects.project_display_name) LIKE '%' || 'test' || '%') AND "
            "projects.date_created >= '2024-01-01 00:00:00' AND "
            "projects.date_modified <= '2024-12-31 23:59:59'",
        ),
        (
            "display_name = A AND display_name = B",
            2,
            [FilterableFields.display_name, FilterableFields.display_name],
            "(lower(projects.project_display_name) LIKE '%' || 'a' || '%') AND "
            "(lower(projects.project_display_name) LIKE '%' || 'b' || '%')",
        ),
        (
            "date_created >= 2024-01-01T00:00:00 AND date_created <= 2024-06-01T00:00:00 AND "
            "date_created != 2024-03-15T00:00:00",
            3,
            [FilterableFields.date_created, FilterableFields.date_created, FilterableFields.date_created],
            "projects.date_created >= '2024-01-01 00:00:00' AND "
            "projects.date_created <= '2024-06-01 00:00:00' AND "
            "projects.date_created != '2024-03-15 00:00:00'",
        ),
    ],
    ids=[
        "two_date_conditions_and",
        "three_conditions_name_and_dates",
        "duplicated_display_name_field",
        "duplicated_date_created_three_times",
    ],
)
def test_multiple_conditions_and(
    filter_str: str,
    expected_count: int,
    expected_fields: list[FilterableFields],
    expected_sql: str,
):
    result = ParsedProjectFilter.from_str(filter_str)
    assert len(result.conditions) == expected_count
    assert [c.field for c in result.conditions] == expected_fields
    assert _to_sql(result) == expected_sql


def test_quoted_value_containing_and_is_not_split():
    """A quoted value containing ' AND ' must not be split into multiple conditions."""
    result = ParsedProjectFilter.from_str('display_name = "Foo AND Bar"')
    assert len(result.conditions) == 1
    assert result.conditions[0].field == FilterableFields.display_name
    assert result.conditions[0].value == "Foo AND Bar"
    assert _to_sql(result) == "(lower(projects.project_display_name) LIKE '%' || 'foo and bar' || '%')"


def test_unknown_logical_operator_is_ignored():
    """OR is not supported; the entire text after '=' is treated as the value."""
    result = ParsedProjectFilter.from_str("display_name = value OR display_name = another")
    assert len(result.conditions) == 1
    assert result.conditions[0].field == FilterableFields.display_name
    assert result.conditions[0].operator == FilteringOperators.eq
    assert result.conditions[0].value == "value OR display_name = another"
    assert (
        _to_sql(result) == "(lower(projects.project_display_name) LIKE '%' || 'value or display_name = another' || '%')"
    )


@pytest.mark.parametrize(
    ("filter_str", "expected_exception", "expected_message"),
    [
        (
            "invalid_field = value",
            ValidationError,
            "Input should be 'display_name', 'description', 'date_created' or 'date_modified'",
        ),
        ("date_created >= not-a-date", ValidationError, "Invalid isoformat string: 'not-a-date'"),
        ("date_modified >= 99/01/2024", ValidationError, "Invalid isoformat string: '99/01/2024'"),
        ("date_created >= 2024-01-01T00:00:00+00:00", ValidationError, "Datetime values must be timezone-naive"),
        ("date_modified >= 2024-06-01T12:00:00Z", ValidationError, "Datetime values must be timezone-naive"),
        ("display_name ~ value", ValueError, "Invalid condition syntax: display_name ~ value"),
        ("display_name =", ValueError, "Invalid condition syntax: display_name ="),
        ("display_name value", ValueError, "Invalid condition syntax: display_name value"),
        ("!!!", ValueError, "Invalid condition syntax: !!!"),
        ('display_name = ""', ValueError, "Value cannot be an empty string."),
        ("display_name = ''", ValueError, "Value cannot be an empty string."),
        ("AND display_name = x", ValueError, "Invalid condition syntax: AND display_name = x"),
        ("display_name = x AND", ValueError, "Invalid condition syntax: display_name = x AND"),
        (
            "display_name = x AND AND date_created >= 2024-01-01T00:00:00",
            ValueError,
            "Invalid condition syntax: AND date_created >= 2024-01-01T00:00:00",
        ),
    ],
    ids=[
        "invalid_field",
        "invalid_date_value",
        "non_iso_date_format",
        "timezone_aware_utc_offset",
        "timezone_aware_z_suffix",
        "invalid_operator_tilde",
        "missing_value",
        "missing_operator",
        "completely_invalid_syntax",
        "empty_double_quoted_value",
        "empty_single_quoted_value",
        "leading_and",
        "trailing_and",
        "double_and",
    ],
)
def test_invalid_filter_raises_error(filter_str: str, expected_exception: type, expected_message: str):
    with pytest.raises(expected_exception, match=expected_message):
        ParsedProjectFilter.from_str(filter_str)


@pytest.mark.parametrize("date_attr", ["date_created", "date_modified"])
def test_contradictory_date_range_does_not_raise(date_attr: str):
    """No error is raised when gte value is greater than lt value (impossible range)."""
    result = ParsedProjectFilter.from_str(
        f"{date_attr} >= 2024-06-01T00:00:00 AND {date_attr} < 2024-01-01T00:00:00",
    )
    assert len(result.conditions) == 2
    expected_sql = f"projects.{date_attr} >= '2024-06-01 00:00:00' AND projects.{date_attr} < '2024-01-01 00:00:00'"
    assert _to_sql(result) == expected_sql


def test_date_modified_before_date_created_does_not_raise():
    """No error is raised when date_modified upper bound is earlier than date_created lower bound."""
    result = ParsedProjectFilter.from_str(
        "date_created >= 2024-06-01T00:00:00 AND date_modified <= 2024-01-01T00:00:00",
    )
    assert len(result.conditions) == 2
    expected_sql = "projects.date_created >= '2024-06-01 00:00:00' AND projects.date_modified <= '2024-01-01 00:00:00'"
    assert _to_sql(result) == expected_sql


def test_str_returns_original_filter_string():
    filter_str = 'display_name = "Alpha" AND date_created >= 2024-01-01T00:00:00'
    result = ParsedProjectFilter.from_str(filter_str)
    assert str(result) == filter_str


def test_unhandled_filterable_field_raises_value_error(mocker: pytest_mock.MockerFixture):
    """Exhaustiveness guard raises when a field is not handled in as_sqlalchemy_expr."""
    condition = ComparisonOp.model_construct(field="unknown_field", operator=FilteringOperators.eq, value="test")
    parsed = ParsedProjectFilter.model_construct(filter="unknown_field = test", conditions=[condition])
    mocker.patch("ansys.saf.glow._server.filter_parser.PROJECT_MAPPING_FIELDS", {"unknown_field": "unknown_field"})
    with pytest.raises(ValueError, match="Unhandled filterable field: unknown_field"):
        parsed.as_sqlalchemy_expr()


def test_unhandled_operator_raises_value_error():
    """Exhaustiveness guard raises when an operator is not in the dispatch table."""
    condition = ComparisonOp.model_construct(
        field=FilterableFields.date_created,
        operator="unsupported_op",
        value="2024-01-01T00:00:00",
    )
    parsed = ParsedProjectFilter.model_construct(
        filter="date_created unsupported_op 2024-01-01T00:00:00",
        conditions=[condition],
    )
    with pytest.raises(ValueError, match="Unhandled operator: unsupported_op"):
        parsed.as_sqlalchemy_expr()
