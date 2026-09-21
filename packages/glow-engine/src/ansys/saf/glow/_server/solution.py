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

import inspect
import logging
from types import ModuleType
from typing import get_type_hints

from pydantic import BaseModel, ValidationError

from ansys.saf.glow._core.exceptions import SolutionLoadException
from ansys.saf.glow._core.solution import Solution
from ansys.saf.glow._core.step_model import StepModel
from ansys.saf.glow._core.transaction import categorize_transaction_parameters
from ansys.saf.glow._crud.solution_configuration_models import SolutionConfiguration
from ansys.saf.glow._server.exceptions import NotFoundError
from ansys.saf.glow._utilities.solution_modules import find_solution

logger = logging.getLogger(__name__)


class SolutionService:
    def __init__(self, solution_module: ModuleType) -> None:
        self._module = solution_module
        self._solution_type: type[Solution] = find_solution(solution_module)
        self._default_instance: Solution
        self._solution_configuration_type: type[SolutionConfiguration] | None = None

    def build_and_validate(self) -> None:
        self._solution_type = find_solution(self._module)
        self._rebuild_solution_models()
        self._default_instance = self._build_default_solution_instance()
        for step_name, step in self._default_instance.get_steps():
            self._validate_methods(step_name, step)
        if solution_configuration := self._default_instance.model_fields.get(  # pyright: ignore[reportDeprecated]
            "solution_configuration",
        ):
            self._solution_configuration_type = solution_configuration.annotation
        self._validate_solution_configuration()

    def _rebuild_solution_models(self) -> None:
        """Rebuild solution Pydantic models to resolve postponed annotations.

        User solution modules may use ``from __future__ import annotations`` which leaves
        model annotations unevaluated until rebuild time.
        """

        for name, obj in self._module.__dict__.items():
            if not (isinstance(obj, type) and issubclass(obj, BaseModel)):
                continue

            # Rebuild only models defined in the loaded solution module.
            if obj.__module__ != self._module.__name__:
                continue

            try:
                obj.model_rebuild(_types_namespace=vars(self._module))
            except Exception as exc:
                logger.warning("Could not rebuild model '%s': %s", name, exc, exc_info=True)

    @property
    def solution_type(self) -> type[Solution]:
        return self._solution_type

    @property
    def solution_module(self) -> ModuleType:
        return self._module

    @property
    def default_instance(self) -> Solution:
        return self._default_instance

    @property
    def name(self) -> str:
        return self._solution_type.__name__

    @property
    def has_shared_product_instances(self) -> bool:
        for step in self._solution_type.get_steps_fields().values():
            for _ in step.get_instance_method_names():
                return True
        return False

    @property
    def solution_configuration_type(self) -> type[SolutionConfiguration] | None:
        return self._solution_configuration_type

    def _build_default_solution_instance(self) -> Solution:
        try:
            return self._solution_type.initialize()
        except ValidationError as exc:
            for error in exc.errors():
                if error["msg"] == "field required":
                    error["msg"] = (
                        "Field required: provide a default value or use 'Optional[type]' to mark it as optional."
                    )
            raise SolutionLoadException(str(exc)) from None

    def _validate_methods(self, step_name: str, step: StepModel) -> None:
        methods_without_transaction = set(step.get_instance_method_names()) - set(step.get_transaction_method_names())
        if methods_without_transaction:
            raise SolutionLoadException(
                f"On step '{step_name}', the following methods have instance decorators without "
                f"a transaction decorator: {','.join(methods_without_transaction)}",
            )

        for method_name in step.get_transaction_method_names():
            method = getattr(step, method_name)
            try:
                method._validate(step_name, self._default_instance)
            except SolutionLoadException as ex:
                raise SolutionLoadException(f"On step '{step_name}', method '{method_name}':\n- {ex.errors}") from None

    def get_step_model(self, step_name: str) -> type[StepModel]:
        step_type = self.solution_type.get_steps_fields().get(step_name)
        if step_type is None:
            raise NotFoundError(f"Step '{step_name}' not found.")
        return step_type

    def _validate_solution_configuration(self):
        transaction_solution_configuration_types: set[type[SolutionConfiguration]] = set()
        for step in self._solution_type.get_steps_fields().values():
            for method_name in step.get_transaction_method_names():
                method = getattr(step, method_name)
                method_type_hints = get_type_hints(method, include_extras=True)
                signature = inspect.signature(method)
                _, solution_configuration_param = categorize_transaction_parameters(method_type_hints, signature)
                if solution_configuration_param:
                    transaction_solution_configuration_types.add(solution_configuration_param.type)

        if len(transaction_solution_configuration_types) > 1:
            raise SolutionLoadException(
                "Only one type of solution configuration can be used for all transactions and steps.",
            ) from None

        if (
            len(transaction_solution_configuration_types) == 1
            and self._solution_configuration_type not in transaction_solution_configuration_types
        ):
            raise SolutionLoadException(
                "The solution configuration type used in the transactions is not the one defined in the Solution's "
                "solution_configuration field.",
            ) from None

        # we use inspect.get_annotations so it only contains the fields explicitly defined in the custom class,
        # since solution_schema_version is also part of the base class but we want them to override it.
        if (
            self._solution_configuration_type
            and self._solution_configuration_type != SolutionConfiguration
            and (
                "solution_schema_version" not in inspect.get_annotations(self._solution_configuration_type)
                or self._solution_configuration_type.model_fields["solution_schema_version"].annotation is not int
                or not isinstance(
                    self._solution_configuration_type.model_fields["solution_schema_version"].default,
                    int,
                )
            )
        ):
            raise SolutionLoadException(
                "A custom SolutionConfiguration class must have a 'solution_schema_version' field, "
                "of type integer and with a default value.",
            )
