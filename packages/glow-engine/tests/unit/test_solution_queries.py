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

from ansys.saf.glow.solution import MethodIdentifier
from tests.mocks.solutions.async_instances import AsyncInstancesSolution


def test_method_equality():
    assert MethodIdentifier("a", "b") == MethodIdentifier("a", "b")


def test_get_other_methods_with_same_instance_returns_expected_results():
    solution = AsyncInstancesSolution
    method_alone = MethodIdentifier("instance_step", "alone")
    method_create = MethodIdentifier("instance_step", "create")
    method_a = MethodIdentifier("instance_step", "long_method_a")
    method_b = MethodIdentifier("instance_step", "long_method_b")

    others_of_alone = solution.get_other_methods_with_same_instance(method_alone)
    others_of_a = solution.get_other_methods_with_same_instance(method_a)
    others_of_b = solution.get_other_methods_with_same_instance(method_b)

    assert len(others_of_alone) == 0
    assert len(others_of_a) == 2
    assert len(others_of_b) == 2

    assert set(others_of_a) == {method_create, method_b}
    assert set(others_of_b) == {method_create, method_a}


def test_get_step_instance_names():
    solution = AsyncInstancesSolution
    names = solution.get_step_instance_names("instance_step")
    assert names == {"a_b", "x_y"}


def test_get_instance_references():
    solution = AsyncInstancesSolution
    references = solution.get_steps_fields()["instance_step"].get_instance_references()
    assert references == ["a_b", "x_y", "x_y", "x_y"]
