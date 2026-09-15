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
from typing import Any

from ansys.saf.glow.solution import (
    NO_ENTITY,
    BadRequestError,
    EntityHandle,
    Solution,
    StepModel,
    StepsModel,
    StepSpec,
    long_running,
    transaction,
)

logger = logging.getLogger(__name__)


class ExceptionsStep(StepModel):
    x: int = 99
    result: EntityHandle = NO_ENTITY
    directory: EntityHandle = NO_ENTITY

    @transaction(self=StepSpec())
    def raise_bad_request_error(self):
        raise BadRequestError("State of project invalid")

    @transaction(self=StepSpec())
    @long_running
    def raise_bad_request_error_long(self):
        raise BadRequestError("State of project invalid")

    @transaction(self=StepSpec())
    def raise_runtime_error(self) -> None:
        raise RuntimeError("Runtime Error!")

    @transaction(self=StepSpec())
    @long_running
    def raise_runtime_error_long(self) -> None:
        raise RuntimeError("Runtime Error!")

    @transaction(self=StepSpec())
    def raise_wrong_attribute_error(self) -> None:
        _ = self.wrong  # type: ignore

    @transaction(self=StepSpec())
    @long_running
    def raise_wrong_attribute_error_long(self) -> None:
        _ = self.wrong  # type: ignore

    @transaction(self=StepSpec(upload=["x"]))
    def raise_upload_wrong_field_within_method(self):
        self.transaction.upload("y")  # type: ignore

    @transaction(self=StepSpec(upload=["x"]))
    @long_running
    def raise_upload_wrong_field_within_method_long(self):
        self.transaction.upload("y")  # type: ignore

    @transaction(self=StepSpec())
    def raise_import_wrong_module(self) -> None:
        import wrong_module  # noqa: F401 # type: ignore

    @transaction(self=StepSpec())
    @long_running
    def raise_import_wrong_module_long(self) -> None:
        import wrong_module  # noqa: F401 # type: ignore

    @transaction(self=StepSpec())
    def no_exception(self) -> None:
        pass

    @transaction(self=StepSpec())
    def return_unjsonable(self) -> int:
        return StepSpec()  # type: ignore

    @transaction(self=StepSpec())
    def wrong_return_value(self) -> dict[str, Any]:
        return 1  # type: ignore  intentional wrong type

    @transaction(self=StepSpec(upload=["result"]))
    def store_result(self) -> None:
        result_file = self.storage_scope.get_storage_root() / "result.txt"
        result_file.write_text("hello world!")
        self.result = self.storage_scope.store(result_file)

    @transaction(self=StepSpec(upload=["directory"]))
    def store_directory(self) -> None:
        top = self.storage_scope.get_storage_root() / "top"
        top.mkdir()
        self.directory = self.storage_scope.store(top)

    @transaction(self=StepSpec(download=["result"]))
    def get_cached_result(self) -> Path:
        path = self.storage_scope.get_cached(self.result)
        return path

    @transaction(self=StepSpec(download=["directory"]))
    def get_cached_directory(self) -> Path:
        path = self.storage_scope.get_cached(self.directory)
        return path

    @transaction(self=StepSpec(download=["result"]))
    def raise_get_cached(self) -> None:
        self.storage_scope.get_cached(self.result)

    @transaction(self=StepSpec(download=["result"]))
    def raise_get_copy(self) -> None:
        destination = self.storage_scope.get_storage_root() / "destination.txt"
        self.storage_scope.get_copy(self.result, destination)

    @transaction(self=StepSpec(download=["result"]))
    def raise_get_stream_result(self) -> None:
        self.storage_scope.get_stream(self.result)

    @transaction(self=StepSpec(download=["result"]))
    def raise_get_parent(self) -> None:
        self.storage_scope.get_parent(self.result)

    @transaction(self=StepSpec(download=["result"]))
    def raise_get_children_result(self) -> None:
        self.storage_scope.get_children(self.result)

    @transaction(self=StepSpec(download=["result"]))
    @long_running
    def raise_get_children_result_long_running(self) -> None:
        self.storage_scope.get_children(self.result)

    @transaction(self=StepSpec(download=["result"]))
    def raise_get_child(self) -> None:
        self.storage_scope.get_child(self.result, "random_name")

    @transaction(self=StepSpec(download=["directory"]))
    def raise_get_stream_directory(self) -> None:
        self.storage_scope.get_stream(self.directory)

    @transaction(self=StepSpec(download=["directory"]))
    def raise_get_children_directory(self) -> None:
        self.storage_scope.get_children(self.directory)

    @transaction(self=StepSpec(download=["result"]))
    def raise_store(self) -> None:
        result_path = self.storage_scope.get_cached(self.result)
        self.storage_scope.store(result_path)

    @transaction(self=StepSpec(upload=["x"]))
    def assign_string_to_int_field(self) -> None:
        self.x = "foo"  # type: ignore

    @transaction(self=StepSpec(upload=["x"]))
    @long_running
    def assign_string_to_int_field_long(self) -> None:
        self.x = "foo"  # type: ignore


class Steps(StepsModel):
    exceptions_step: ExceptionsStep


class ExceptionsSolution(Solution):
    display_name: str = "Exceptions"
    steps: Steps
