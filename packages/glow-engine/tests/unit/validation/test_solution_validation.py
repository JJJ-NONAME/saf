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

import logging
from pathlib import Path
import py_compile
import re
import shutil
from types import ModuleType
from unittest import mock

from pydantic import BaseModel, ValidationError
import pytest

from ansys.saf.glow._core.exceptions import SolutionLoadException
from ansys.saf.glow._crud.solution_configuration_models import SolutionConfiguration
from ansys.saf.glow._server.solution import SolutionService
from ansys.saf.glow._utilities.code import load_python_file
from tests.mocks.solutions import (
    cyclic_dependency,
    empty_steps,
    extended_solution_configuration,
    extended_solution_configuration_different_configs,
    extended_solution_configuration_not_defined,
    extended_solution_configuration_not_used,
    extended_solution_configuration_without_schema_version,
    extended_solution_configuration_wrong_type_schema_version,
    extra_field_solution,
    future_annotations_solution,
    method_create_instance_identifier_overlaps_step_name,
    method_create_instance_manager_is_not_manager_type,
    method_create_instance_method_parameter_wrong_type,
    method_create_instance_name_has_2_parts,
    method_create_instance_name_not_identifier,
    method_create_instance_name_overlaps_step_name,
    method_create_instance_name_refers_to_non_existent_step,
    method_create_instance_twice_mixed_step_instance_ref,
    method_create_instance_twice_same_instance_id,
    method_create_instance_twice_same_instance_ref,
    method_create_instance_twice_same_step_instance_ref,
    method_create_instance_without_transaction,
    method_instance_before_transaction,
    method_instance_manager_type_not_same_as_create,
    method_instance_method_parameter_wrong_type,
    method_instance_name_overlaps_step_name,
    method_instance_name_refers_non_existent_step,
    method_instance_no_create_instance,
    method_instance_step_manager_type_not_same_as_create,
    method_instance_twice_same_instance,
    method_instance_without_transaction,
    method_mixed_instance_decorators_with_same_instance,
    method_mixed_instance_decorators_with_same_step_instance,
    method_param_no_type,
    method_step_instance_no_create_instance,
    method_with_return_value_no_type,
    method_with_wrong_step,
    modify_with_three_migrations_in_wrong_order,
    modify_with_three_migrations_lower_than_1,
    modify_with_three_migrations_missing_last,
    modify_with_three_migrations_missing_middle,
    modify_with_three_migrations_too_high_version,
    multiple_solution_configuration,
    multiple_solution_configuration_v2,
    no_default,
    no_solution,
    no_step,
    solution_configuration,
    transaction_unknown_field,
    two_solutions,
    upload_other_step,
    wrong_steps_field,
)


@pytest.mark.parametrize(
    ("solution_module", "expected_error"),
    [
        (
            cyclic_dependency,
            "The solution has cyclic dependency: a_step.a_method >> a_step.a2 >> b_step.b_method >> b_step.b1 >> a_step.a_method",  # noqa: E501
        ),
        (empty_steps, "The Solution must define at least one step."),
        (
            extended_solution_configuration_without_schema_version,
            "A custom SolutionConfiguration class must have a 'solution_schema_version' field, of type integer and with a default value.",  # noqa: E501
        ),
        (
            extended_solution_configuration_wrong_type_schema_version,
            "A custom SolutionConfiguration class must have a 'solution_schema_version' field, of type integer and with a default value.",  # noqa: E501
        ),
        (
            extended_solution_configuration_not_defined,
            "The solution configuration type used in the transactions is not the one defined in the Solution's solution_configuration field.",  # noqa: E501
        ),
        (
            extended_solution_configuration_different_configs,
            "The solution configuration type used in the transactions is not the one defined in the Solution's solution_configuration field.",  # noqa: E501
        ),
        (extra_field_solution, "extra_field is not an allowed field in the Solution."),
        (
            method_create_instance_identifier_overlaps_step_name,
            "The @transaction parameter 'x' is used as the identifier of an instance.",
        ),
        (
            method_create_instance_manager_is_not_manager_type,
            re.escape(
                "the instance_manager_type argument of @create_instance for instance x is not derived from ProductInstanceManager.",  # noqa: E501
            ),
        ),
        (
            method_create_instance_method_parameter_wrong_type,
            "argument x has type <class 'int'> which does not match the corresponding instance manager type ",
        ),
        (
            method_create_instance_name_has_2_parts,
            re.escape(
                "the name in @create_instance 'my_step.a' is not a valid identifier (use python identifier syntax)",
            ),
        ),
        (
            method_create_instance_name_not_identifier,
            re.escape("the name in @create_instance 'j@unk' is not a valid identifier (use python identifier syntax)"),
        ),
        (
            method_create_instance_name_overlaps_step_name,
            "The @transaction parameter 'x' is used as the identifier of an instance.",
        ),
        (
            method_create_instance_name_refers_to_non_existent_step,
            re.escape(
                "the name in @create_instance 'missing.a' is not a valid identifier (use python identifier syntax)",
            ),
        ),
        (
            method_create_instance_twice_mixed_step_instance_ref,
            "there is more than one instance decorator that refer to each of the following instances: my_step.x",
        ),
        (
            method_create_instance_twice_same_instance_id,
            "the following instance identifiers are used more than once: a",
        ),
        (
            method_create_instance_twice_same_instance_ref,
            "there is more than one instance decorator that refer to each of the following instances: my_step.x",
        ),
        (
            method_create_instance_twice_same_step_instance_ref,
            "there is more than one instance decorator that refer to each of the following instances: other_step.x",
        ),
        (
            method_create_instance_without_transaction,
            "On step 'my_step', the following methods have instance decorators without a transaction decorator: create",
        ),
        (method_instance_before_transaction, "the @instance decorator appears before the @transaction decorator"),
        (
            method_instance_manager_type_not_same_as_create,
            "argument x has type <class 'tests.mocks.instance_managers.empty_instance_manager.OtherInstanceManager'> which does not match the corresponding instance manager type <class 'tests.mocks.instance_managers.empty_instance_manager.EmptyInstanceManager'> declared on the matching @create_instance",  # noqa: E501
        ),
        (
            method_instance_method_parameter_wrong_type,
            "argument x has type <class 'int'> which does not match the corresponding instance manager type ",
        ),
        (
            method_instance_name_overlaps_step_name,
            "The @transaction parameter 'x' is used as the identifier of an instance.",
        ),
        (
            method_instance_name_refers_non_existent_step,
            "@instance refers to non-existent step 'missing' in 'my_step'",
        ),
        (
            method_instance_no_create_instance,
            "The @instance decorator with instance_name argument referring to my_step.x does not have a corresponding @create_instance decorator",  # noqa: E501
        ),
        (
            method_instance_step_manager_type_not_same_as_create,
            "argument x has type <class 'tests.mocks.instance_managers.empty_instance_manager.OtherInstanceManager'> which does not match the corresponding instance manager type <class 'tests.mocks.instance_managers.empty_instance_manager.EmptyInstanceManager'> declared on the matching @create_instance",  # noqa: E501
        ),
        (
            method_instance_twice_same_instance,
            "there is more than one instance decorator that refer to each of the following instances: my_step.x",
        ),
        (
            method_instance_without_transaction,
            "On step 'my_step', the following methods have instance decorators without a transaction decorator: use",
        ),
        (
            method_mixed_instance_decorators_with_same_instance,
            "there is more than one instance decorator that refer to each of the following instances: my_step.x",
        ),
        (
            method_mixed_instance_decorators_with_same_step_instance,
            "there is more than one instance decorator that refer to each of the following instances: other_step.x",
        ),
        (
            method_param_no_type,
            re.escape("The parameter 'no_type_hint' does not have any type hint defined."),
        ),
        (
            method_step_instance_no_create_instance,
            "The @instance decorator with instance_name argument referring to other_step.x does not have a corresponding @create_instance decorator",  # noqa: E501
        ),
        (
            method_with_return_value_no_type,
            re.escape("The @transaction contains a return statement but no return type hint is defined."),
        ),
        (
            method_with_wrong_step,
            "On step 'my_step', method 'increment':\n- The parameter 'wrong_step' does not match any steps in the solution.",  # noqa: E501
        ),
        (
            multiple_solution_configuration,
            "Only one type of solution configuration can be used for all transactions and steps.",
        ),
        (
            multiple_solution_configuration_v2,
            "Only one type of solution configuration can be used for all transactions and steps.",
        ),
        (
            no_default,
            "2 validation errors for NoDefaultStep\nno_int_default\n  Field required",
        ),
        (no_solution, "The solution definition module does not define a 'Solution' class."),
        (no_step, "The solution does not contain any steps. Add a step to the solution."),
        (
            transaction_unknown_field,
            "On step 'my_step', method 'do_unkown_field':\n- The download/upload field: 'unkown_field' does not exist.",
        ),
        (two_solutions, "The solution definition module defines more than one 'Solution' class."),
        (
            upload_other_step,
            "On step 'a_step', method 'a_method':\n- The @transaction parameter 'b_step' cannot contains upload fields. Upload fields are specific to 'self'.",  # noqa: E501
        ),
        (
            wrong_steps_field,
            "Invalid type defined in steps: the field 'wrong_step_field' is not a type derived from StepModel.",
        ),
        (
            modify_with_three_migrations_in_wrong_order,
            re.escape(
                "The migration versions must be an increasing list of integers no lower than 1, without gaps, and reaching up to the current version minus 1. The current version is 4 and the migration version list is [1, 3, 2].",  # noqa: E501
            ),
        ),
        (
            modify_with_three_migrations_missing_last,
            re.escape(
                "The migration versions must be an increasing list of integers no lower than 1, without gaps, and reaching up to the current version minus 1. The current version is 5 and the migration version list is [1, 2, 3].",  # noqa: E501
            ),
        ),
        (
            modify_with_three_migrations_missing_middle,
            re.escape(
                "The migration versions must be an increasing list of integers no lower than 1, without gaps, and reaching up to the current version minus 1. The current version is 5 and the migration version list is [1, 2, 4].",  # noqa: E501
            ),
        ),
        (
            modify_with_three_migrations_too_high_version,
            re.escape(
                "The migration versions must be an increasing list of integers no lower than 1, without gaps, and reaching up to the current version minus 1. The current version is 3 and the migration version list is [1, 2, 3].",  # noqa: E501
            ),
        ),
        (
            modify_with_three_migrations_lower_than_1,
            re.escape(
                "The migration versions must be an increasing list of integers no lower than 1, without gaps, and reaching up to the current version minus 1. The current version is 4 and the migration version list is [0, 1, 2, 3].",  # noqa: E501
            ),
        ),
    ],
)
def test_solution_validation(solution_module: ModuleType, expected_error: str):
    with pytest.raises(SolutionLoadException, match=expected_error):  # noqa: PT012
        solution_service = SolutionService(solution_module)
        solution_service.build_and_validate()


def test_module_not_found(tmp_path: Path):
    orig_file = tmp_path / "method_with_return_value_compiled.p"

    match_exception = re.escape(f"Cannot import python file: {orig_file}: Module name not found for file {orig_file}.")

    with pytest.raises(Exception, match=match_exception):
        load_python_file(orig_file)


def test_method_return_type_validation_compiled(tmp_path: Path):
    # If we directly compile the existing module, python somehow is able to find the original source file
    # even if we load the compiled one.
    orig_file = tmp_path / "method_with_return_value_compiled.py"
    shutil.copyfile(method_with_return_value_no_type.__file__, orig_file)
    dest_file = tmp_path / "method_with_return_value_compiled.pyc"
    py_compile.compile(str(orig_file), str(dest_file))
    orig_file.unlink()
    method_with_return_value_compiled = load_python_file(dest_file)
    solution_service = SolutionService(method_with_return_value_compiled)
    with mock.patch.object(logging.Logger, "debug") as mocked_logger:
        solution_service.build_and_validate()
        mocked_logger.assert_called_once_with("Can't validate return type of increment: source code is unavailable.")


def test_public_product_instance_manager_no_initialize():
    """Test that if the derived class of ProductInstanceManager does not contain a 'initialize' method,
    it must raise a proper exception."""
    expected_error = "MockProductInstanceManagerNoInitialize must implement a 'initialize' method."
    with pytest.raises(SolutionLoadException, match=re.escape(expected_error)):
        from tests.mocks.solutions import (
            product_instance_no_initialize,  # pyright: ignore[reportUnusedImport] # noqa: F401
        )


def test_product_instance_wrong_initialize_parameters():
    """Test that if the ProductInstanceManager.initialize signature is not the same as InstanceManager.initialize,
    it must raise a proper exception."""
    expected_error = (
        "The signature of the 'initialize' method from MockProductInstanceManagerWrongParameter does not match the "
        "'initialize' method from InternalMockGrpcProductInstanceManagerImpl."
    )
    with pytest.raises(SolutionLoadException, match=expected_error):
        from tests.mocks.solutions import (
            product_instance_wrong_param,  # pyright: ignore[reportUnusedImport] # noqa: F401
        )


def test_solution_configuration_without_default_values():
    """Test that if the solution developers does not set default values in their extended SolutionConfiguration class,
    the solution fails to fload."""
    expected_error = (
        "1 validation error for WrongSolutionConfiguration\nsolution_schema_version\n  "
        "Field required [type=missing, input_value={}, input_type=dict]"
    )
    with pytest.raises(ValidationError, match=re.escape(expected_error)):
        from tests.mocks.solutions import (
            extended_solution_configuration_without_default_value,  # pyright: ignore[reportUnusedImport]  # noqa: F401
        )


@pytest.mark.parametrize(
    ("solution_module", "expected_type"),
    [
        (solution_configuration, SolutionConfiguration),
        (extended_solution_configuration, extended_solution_configuration.ExtendedSolutionConfiguration),
        (extended_solution_configuration_not_used, None),
    ],
)
def test_find_solution_configuration(solution_module: ModuleType, expected_type: BaseModel):
    solution_service = SolutionService(solution_module)
    solution_service.build_and_validate()
    assert solution_service.solution_configuration_type == expected_type


def test_custom_recovery_state_info_without_default_values():
    """Test that recovery state info types must be instantiable without arguments. Only enforced for BDM."""

    expected_error = (
        "InvalidRecoveryStateInfo must be instantiable without arguments: 1 validation error for "
        "InvalidRecoveryStateInfo"
    )
    with pytest.raises(SolutionLoadException, match=expected_error):
        from tests.mocks.solutions import (
            invalid_recovery_state_info,  # pyright: ignore[reportUnusedImport]  # noqa: F401
        )

    with pytest.raises(SolutionLoadException, match=expected_error):
        from tests.mocks.solutions import (
            invalid_recovery_state_info_unused,  # pyright: ignore[reportUnusedImport]  # noqa: F401
        )


def test_rebuild_solution_models_calls_model_rebuild_on_module_models():
    solution_service = SolutionService(future_annotations_solution)

    future_annotations_solution.FutureAnnotationsPayload.rebuild_called = False
    solution_service._rebuild_solution_models()  # pyright: ignore[reportPrivateUsage]

    assert future_annotations_solution.FutureAnnotationsPayload.rebuild_called


def test_build_and_validate_calls_rebuild_solution_models():
    solution_service = SolutionService(future_annotations_solution)

    with mock.patch.object(solution_service, "_rebuild_solution_models") as rebuild_spy:
        solution_service.build_and_validate()

    rebuild_spy.assert_called_once()


def test_build_and_validate_succeeds_with_future_annotations():
    solution_service = SolutionService(future_annotations_solution)

    # Should not raise even though the module uses from __future__ import annotations
    solution_service.build_and_validate()
