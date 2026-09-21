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

"""Filter parser for projects list endpoint following AIP-160 guidelines and EBNF grammar as syntax.
See https://google.aip.dev/160 and https://google.aip.dev/assets/misc/ebnf-filtering.txt.

Missing support for:
- Parentheses for grouping: (condition1 AND condition2) OR condition3
- Logical Operators: OR
- Negation Operators: NOT, -
- Comparison Operators: *
- Traversal Operators: a.b, a.b.c
- Has Operator: :
- Functions

Differences:
- = for string is fuzzy search instead of exact match, and it's case insensitive.
"""

from collections.abc import Callable
import datetime
from enum import StrEnum
import re
from typing import Any, Self

from pydantic import BaseModel, model_validator
from sqlalchemy import ColumnElement, and_, func

from ansys.saf.glow._repository.relational_models import PROJECT_MAPPING_FIELDS


def _parse_iso_datetime(value: str) -> datetime.datetime:
    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"
    return datetime.datetime.fromisoformat(value)


class FilterableFields(StrEnum):
    """Enumeration of fields that can be used in project filter expressions."""

    display_name = "display_name"
    description = "description"
    date_created = "date_created"
    date_modified = "date_modified"


class FilteringOperators(StrEnum):
    """Enumeration of comparison operators supported in filter expressions."""

    eq = "="
    neq = "!="
    lt = "<"
    gt = ">"
    lte = "<="
    gte = ">="


# Pre-compiled regex for parsing a single condition expression.
# Pattern: FIELD OPERATOR VALUE
# Operators are sorted longest-first so that "!=" and ">=" match before "=" and ">".
# Supports spaces in VALUE, but not in FIELD. Also supports optional spaces around the operator.
_sorted_ops = sorted(FilteringOperators, key=lambda o: len(o.value), reverse=True)
_CONDITION_PATTERN: re.Pattern[str] = re.compile(
    rf"^(\w+)\s*({'|'.join(re.escape(op.value) for op in _sorted_ops)})\s*(.+)$",
)

# Dispatch table mapping each operator to a SQLAlchemy comparison expression builder.
_OPERATOR_DISPATCH: dict[FilteringOperators, Callable[[Any, Any], ColumnElement[bool]]] = {
    FilteringOperators.eq: lambda col, val: col == val,
    FilteringOperators.neq: lambda col, val: col != val,
    FilteringOperators.lt: lambda col, val: col < val,
    FilteringOperators.gt: lambda col, val: col > val,
    FilteringOperators.lte: lambda col, val: col <= val,
    FilteringOperators.gte: lambda col, val: col >= val,
}


def _split_and_conditions(filter_str: str) -> list[str]:
    """Split a filter string on ' AND ' delimiters, respecting quoted values.

    Quoted segments (single or double quotes) are treated as opaque — any ' AND '
    occurring inside quotes is not treated as a delimiter.
    """
    parts: list[str] = []
    current: list[str] = []
    quote_char: str | None = None
    i = 0
    while i < len(filter_str):
        ch = filter_str[i]
        if quote_char is not None:
            current.append(ch)
            if ch == quote_char:
                quote_char = None
        elif ch in ('"', "'"):
            quote_char = ch
            current.append(ch)
        elif filter_str[i : i + 5] == " AND " and quote_char is None:
            parts.append("".join(current))
            current = []
            i += 5
            continue
        elif filter_str[i : i + 4] == " AND" and i + 4 == len(filter_str) and quote_char is None:
            parts.append("".join(current))
            current = []
            i += 4
            continue
        else:
            current.append(ch)
        i += 1
    parts.append("".join(current))
    return parts


class ComparisonOp(BaseModel):
    """A single parsed comparison operation extracted from a filter expression."""

    field: FilterableFields
    operator: FilteringOperators
    value: str

    @model_validator(mode="after")
    def validate_field_operator_compatibility(self) -> Self:
        if (
            self.field in (FilterableFields.display_name, FilterableFields.description)
            and self.operator != FilteringOperators.eq
        ):
            raise ValueError(f"Invalid operator '{self.operator}' for field '{self.field}'. Only '=' is allowed.")
        return self

    @model_validator(mode="after")
    def validate_datetime_values(self) -> Self:
        if self.field in (FilterableFields.date_created, FilterableFields.date_modified):
            dt = _parse_iso_datetime(self.value)  # will raise ValueError if not a valid ISO datetime string
            if dt.tzinfo is not None:
                raise ValueError("Datetime values must be timezone-naive (no offset/Z).")
        return self


class ParsedProjectFilter(BaseModel):
    """A parsed project filter containing zero or more conditions combined with AND logic.

    This class parses filter expressions following a subset of the AIP-160 filtering
    specification. Multiple conditions are joined with the ``AND`` keyword.

    Supported filter syntax (EBNF)::

        filter     = condition { " AND " condition } ;
        condition  = field operator value ;
        field      = "display_name" | "description" | "date_created" | "date_modified" ;
        operator   = "=" | "!=" | "<" | ">" | "<=" | ">=" ;
        value      = quoted_string | unquoted_string | iso_datetime ;

    Examples
    --------
    >>> ParsedProjectFilter.from_str("display_name = Motor")
    >>> ParsedProjectFilter.from_str("date_created >= 2024-01-01T00:00:00")
    >>> ParsedProjectFilter.from_str('display_name = "My Project" AND date_created >= 2024-01-01T00:00:00')

    Attributes
    ----------
    filter : str
        The original filter string.
    conditions : list[ComparisonOp]
        The list of parsed comparison operations.
    """

    filter: str = ""
    conditions: list[ComparisonOp] = []

    # TODO: validate that ranges built based on dates make sense,
    # e.g., date_created >= 2024-01-01 AND date_created <= 2024-12-31

    def __str__(self) -> str:
        return self.filter

    @classmethod
    def from_str(cls, filter: str) -> Self:  # noqa: A002
        """Parse a filter expression string into a ``ParsedProjectFilter``.

        Parameters
        ----------
        filter : str
            The filter expression to parse. An empty or whitespace-only string
            returns an instance with no conditions. Multiple conditions can be
            combined using the ``AND`` keyword.

        Returns
        -------
        ParsedProjectFilter
            The parsed filter with extracted conditions.
        """
        if not filter or not filter.strip():
            return cls()

        conditions: list[ComparisonOp] = []
        for condition_str in _split_and_conditions(filter.strip()):
            if not condition_str.strip():
                raise ValueError(f"Invalid condition syntax: {filter.strip()}")
            conditions.append(cls._parse_condition(condition_str.strip()))
        return cls(filter=filter, conditions=conditions)

    @staticmethod
    def _parse_condition(condition_str: str) -> ComparisonOp:
        match = _CONDITION_PATTERN.match(condition_str)
        if not match:
            raise ValueError(f"Invalid condition syntax: {condition_str}")

        field, operator, value_str = match.groups()
        value_str = value_str.strip()
        # Remove quotes if value is a quoted string (e.g., 'Project Alpha', "Project Alpha")
        # Don't remove quotes if they are part of the value (e.g., 'Project "Alpha"', "Project 'Alpha'")
        if len(value_str) >= 2 and value_str[0] in {'"', "'"} and value_str[-1] == value_str[0]:
            value = value_str[1:-1]
            if not value:
                raise ValueError("Value cannot be an empty string.")
        else:
            value = value_str

        return ComparisonOp(field=field, operator=operator, value=value)  # pyright: ignore[reportArgumentType]

    def as_sqlalchemy_expr(self) -> ColumnElement[bool] | None:
        """Convert the parsed conditions into a SQLAlchemy filter expression.

        Returns
        -------
        ColumnElement[bool] | None
            A SQLAlchemy boolean expression combining all conditions with AND logic,
            or ``None`` if there are no conditions.
        """
        sql_conditions: list[ColumnElement[bool]] = []
        for condition in self.conditions:
            project_attr = PROJECT_MAPPING_FIELDS[condition.field]
            if condition.field in (FilterableFields.display_name, FilterableFields.description):
                # fuzzy search, case insensitive
                sql_conditions.append(func.lower(project_attr).contains(condition.value.lower()))
            elif condition.field in (FilterableFields.date_created, FilterableFields.date_modified):
                dt = _parse_iso_datetime(condition.value)
                op_fn = _OPERATOR_DISPATCH.get(condition.operator)
                if op_fn is None:
                    raise ValueError(f"Unhandled operator: {condition.operator}")
                sql_conditions.append(op_fn(project_attr, dt))
            else:
                raise ValueError(f"Unhandled filterable field: {condition.field}")

        if not sql_conditions:
            return None

        return and_(*sql_conditions)
