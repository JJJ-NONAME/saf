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

from typing import Annotated

from pydantic import Field
import pytest

from ansys.saf.glow._core.transaction import SolutionConfigParam, build_pydantic_model_from_transaction_parameters
from ansys.saf.glow.solution import (
    SolutionConfiguration,
    StepModel,
    StepSpec,
    transaction,
)
from tests.mocks.instance_managers.mock_product_manager import MockGrpcProductInstanceManager
from tests.mocks.solutions.transactions import OtherStep


class MyStep(StepModel):
    @transaction(self=StepSpec(upload=["inputs_as_json"]))
    def mock_transaction(
        self,
        param_input: str,
        step: OtherStep,
        instance: MockGrpcProductInstanceManager,
        config: SolutionConfiguration,
        field: Annotated[int, Field(1)],
        default_value: bool = False,
        option: int | None = None,
    ) -> int:
        return option or 1

    @transaction(self=StepSpec())
    def mock_transaction_colliding_param_name(
        self,
        _solution_configuration: SolutionConfiguration,
    ) -> int:
        return 1


def test_dynamic_body_model():
    dynamic_model, solution_config_param = build_pydantic_model_from_transaction_parameters(
        MyStep.mock_transaction,
    )
    model_fields = dynamic_model.model_fields
    assert list(model_fields.keys()) == ["param_input", "field", "default_value", "option"]
    assert str(model_fields["param_input"]) == "annotation=str required=True json_schema_extra={}"
    assert str(model_fields["field"]) == "annotation=int required=False default=1 json_schema_extra={}"
    assert str(model_fields["default_value"]) == "annotation=bool required=False default=False json_schema_extra={}"
    assert (
        str(model_fields["option"])
        == "annotation=Union[int, NoneType] required=False default=None json_schema_extra={}"
    )
    assert solution_config_param == SolutionConfigParam(name="config", type=SolutionConfiguration)


@pytest.mark.xfail(reason="collision between method and transaction decorator params", raises=TypeError)
def test_method_param_name_sam_as_transaction_optional_param():
    _, solution_config_param = build_pydantic_model_from_transaction_parameters(
        MyStep.mock_transaction_colliding_param_name,
    )
    assert solution_config_param == SolutionConfigParam(name="_solution_configuration", type=SolutionConfiguration)
