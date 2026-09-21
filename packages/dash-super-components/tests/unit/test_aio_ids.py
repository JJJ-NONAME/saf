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

"""Unit tests for the AIOIds base class and ``make_id_dict`` utility."""

from typing import Any

import pytest

from ansys.solutions.dash_super_components.utils.aio_ids import AIOIds

# ---------------------------------------------------------------------------
# Tests for AIOIds.make_id_dict
# ---------------------------------------------------------------------------


def test_returns_dict_with_correct_keys():
    """Return value must contain exactly the three expected keys."""
    result = AIOIds.make_id_dict("my-component", "label", "some-id")

    assert set(result.keys()) == {"component", "subcomponent", "aio_id"}


def test_component_value_is_set_correctly():
    """``component`` field must match the value passed as ``component``."""
    result = AIOIds.make_id_dict("my-component", "label", "some-id")

    assert result["component"] == "my-component"


def test_subcomponent_value_is_set_correctly():
    """``subcomponent`` field must match the value passed as ``subcomponent``."""
    result = AIOIds.make_id_dict("my-component", "label", "some-id")

    assert result["subcomponent"] == "label"


def test_aio_id_value_is_set_correctly():
    """``aio_id`` field must match the value passed as ``aio_id``."""
    result = AIOIds.make_id_dict("my-component", "label", "some-id")

    assert result["aio_id"] == "some-id"


def test_component_and_subcomponent_are_independent():
    """``component`` and ``subcomponent`` must be stored as separate values."""
    result = AIOIds.make_id_dict("my-component", "my-subcomponent", "some-id")

    assert result["component"] != result["subcomponent"]


@pytest.mark.parametrize(
    ("component", "subcomponent", "aio_id"),
    [
        ("comp", "sub", "id-1"),
        ("my-component", "label", "abc-123"),
        ("transaction-supervisor", "activate-monitoring", "uuid-xyz"),
        ("comp", "sub", 42),  # aio_id may also be an integer wildcard
    ],
)
def test_various_inputs(component: str, subcomponent: str, aio_id: Any):
    """Return the correct dict for a range of valid inputs."""
    result = AIOIds.make_id_dict(component, subcomponent, aio_id)

    assert result == {"component": component, "subcomponent": subcomponent, "aio_id": aio_id}


def test_callable_as_class_method_and_static_method():
    """``make_id_dict`` must be callable both via the class and via an instance."""
    expected = {"component": "c", "subcomponent": "s", "aio_id": "x"}

    assert AIOIds.make_id_dict("c", "s", "x") == expected

    class _Ids(AIOIds):
        pass

    assert _Ids.make_id_dict("c", "s", "x") == expected


# ---------------------------------------------------------------------------
# Tests for AIOIds as a base class
# ---------------------------------------------------------------------------


def test_subclass_inherits_make_id_dict():
    """A concrete subclass must be able to call ``AIOIds.make_id_dict``."""

    class _SampleIds(AIOIds):
        @classmethod
        def label(cls, aio_id: str) -> dict[str, Any]:
            return cls.make_id_dict("my-component", "label", aio_id)

    result = _SampleIds.label("test-id")

    assert result == {"component": "my-component", "subcomponent": "label", "aio_id": "test-id"}
