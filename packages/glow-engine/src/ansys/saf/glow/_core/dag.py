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

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import networkx

from ansys.saf.glow._core.exceptions import SolutionLoadException

T = TypeVar("T", bound="DependencyNode")


if TYPE_CHECKING:
    from typing import Self

    from ansys.saf.glow._core.solution import Solution
    from ansys.saf.glow._core.step_model import StepModel

    SolutionT = TypeVar("SolutionT", bound=Solution)


class DependencyNode(str):
    @classmethod
    def create(cls, step_name: str, field_name: str) -> Self:
        return cls(f"{step_name}.{field_name}")

    def extract_step_and_field_name(self) -> tuple[str, str]:
        step_name, field_name = self.split(".")
        return step_name, field_name


class DependencyGraph:
    def __init__(self, solution: type[SolutionT]) -> None:
        self._digraph = networkx.DiGraph()  # type: ignore
        for step_name, step_model in solution.get_steps_fields().items():
            self._build_dag(step_name, step_model)

        if self._has_cyclic_dependencies():
            cyclic_nodes = [node[0] for node in networkx.find_cycle(self._digraph)]  # type: ignore
            first_node = cyclic_nodes[0]  # type: ignore
            # append first node to the end of the graph to make the cycle clear.
            cyclic_nodes.append(first_node)  # type: ignore
            cyclic_diagram = " >> ".join(cyclic_nodes)  # type: ignore

            raise SolutionLoadException(f"The solution has cyclic dependency: {cyclic_diagram}")

    def has_ancestors(self, step_name: str, field_name: str) -> bool:
        node = DependencyNode.create(step_name, field_name)
        has_ancestors = bool(self._digraph.in_degree(node))  # type: ignore
        return self._digraph.has_node(node) and has_ancestors  # type: ignore

    def toplogical_sort(self) -> list[tuple[str, str]]:
        return [
            node.extract_step_and_field_name()  # type: ignore
            for node in networkx.topological_sort(self._digraph)  # type: ignore
            if not self._is_method_node(node)  # type: ignore
        ]

    def descendants(self, step_name: str, field_name: str) -> list[tuple[str, str]]:
        return [
            descendant.extract_step_and_field_name()  # type: ignore
            for descendant in networkx.descendants(  # type: ignore
                self._digraph,  # type: ignore
                DependencyNode.create(step_name, field_name),  # type: ignore
            )
            if not self._is_method_node(descendant)  # type: ignore
        ]

    def _has_cyclic_dependencies(self) -> bool:
        return not networkx.is_directed_acyclic_graph(self._digraph)  # type: ignore

    def _build_dag(self, step_name: str, step_type: type[StepModel]) -> None:
        for method_name in step_type.get_transaction_method_names():
            method = getattr(step_type, method_name)
            for step_spec_key, step_spec_value in method._transaction.items():
                step_spec_name = step_name if step_spec_key == "self" else step_spec_key
                method_node = DependencyNode.create(step_name, method_name)
                self._add_field_nodes(
                    step_spec_value.download,
                    step_spec_value.upload,
                    step_spec_name,
                    method_node,
                    False,
                )
                self._add_field_nodes(
                    step_spec_value.upload,
                    step_spec_value.download,
                    step_spec_name,
                    method_node,
                    True,
                )
                if method_node not in self._digraph.nodes:  # type: ignore
                    self._digraph.add_node(method_node)  # type: ignore
                self._digraph.nodes[method_node]["is_field"] = False  # type: ignore

    def _add_field_nodes(
        self,
        fields: list[str],
        opposite_fields: list[str],
        step_name: str,
        method_node: DependencyNode,
        is_downstream: bool,
    ):
        for field in fields:
            # ignore method downloads that create a cycle on the method
            if is_downstream or field not in opposite_fields:
                field_node = DependencyNode.create(step_name, field)
                if is_downstream:
                    self._digraph.add_edge(method_node, field_node)  # pyright: ignore[reportUnknownMemberType]
                else:
                    self._digraph.add_edge(field_node, method_node)  # pyright: ignore[reportUnknownMemberType]
                self._digraph.nodes[field_node]["is_field"] = True  # pyright: ignore[reportUnknownMemberType]

    def _is_method_node(self, node: str) -> bool:
        return not self._digraph.nodes[node]["is_field"]  # type: ignore
