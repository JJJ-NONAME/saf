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

from types import ModuleType
from typing import Any

import ansys.saf.glow._testing.solution as internal_testing_solution
import ansys.saf.glow.testing as public_testing


def _extract_fixture_metadata(symbol: Any) -> Any | None:
    fixture_marker = getattr(symbol, "_fixture_function_marker", None)
    if fixture_marker is not None:
        return fixture_marker

    fixture_definition = getattr(symbol, "_pytestfixturefunction", None)
    if fixture_definition is None:
        return None

    fixture_marker = getattr(fixture_definition, "_fixture_function_marker", None)
    return fixture_marker if fixture_marker is not None else fixture_definition


def _fixture_names_from_module(module: ModuleType) -> set[str]:
    fixture_names: set[str] = set()
    module_symbols: dict[str, Any] = module.__dict__
    for symbol_name, symbol in module_symbols.items():
        if symbol_name.startswith("__"):
            continue
        if _extract_fixture_metadata(symbol) is not None:
            fixture_names.add(symbol_name)
    return fixture_names


def test_fixtures_are_not_autouse_and_at_most_module_scoped() -> None:
    for fixture_name in public_testing.__all__:
        fixture_symbol = getattr(public_testing, fixture_name)
        fixture_metadata = _extract_fixture_metadata(fixture_symbol)
        assert fixture_metadata is not None
        autouse = bool(getattr(fixture_metadata, "autouse", False))
        scope = str(getattr(fixture_metadata, "scope", "function"))
        # Exposed fixtures must not be autouse to allow users to control their usage and override behavior
        assert not autouse
        # Higher scopes leave no room for users to override fixtures, add new ones on top or orchestrate their
        # execution.
        assert scope in {"function", "class", "module"}


def test_public_testing_exposes_all_internal_fixtures() -> None:
    internal_fixture_names = _fixture_names_from_module(internal_testing_solution)
    public_fixture_names = _fixture_names_from_module(public_testing)
    assert internal_fixture_names == public_fixture_names
