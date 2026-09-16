# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from dataclasses import dataclass, field
import inspect
from typing import Annotated, Any, get_type_hints

from fastmcp.server import Context
from pydantic import Field

from ansys.saf.glow._core.transaction import categorize_transaction_parameters


@dataclass(frozen=True)
class TransactionMetadata:
    step_name: str
    transaction_name: str
    step_type: type[Any]
    transaction: Any = field(init=False)
    type_hints: dict[str, Any] = field(init=False)
    signature: inspect.Signature = field(init=False)
    transaction_parameter_names: list[str] = field(init=False)
    return_type: Any = field(init=False)
    download_fields: list[str] = field(init=False)
    upload_fields: list[str] = field(init=False)
    is_long_running: bool = field(init=False)
    tool_signature: inspect.Signature = field(init=False)

    def __post_init__(self) -> None:
        transaction = getattr(self.step_type, self.transaction_name)
        type_hints = get_type_hints(transaction)
        signature = inspect.signature(transaction)
        transaction_body_params, _ = categorize_transaction_parameters(type_hints, signature)
        transaction_parameter_names = list(transaction_body_params)
        transaction_spec = getattr(transaction, "_transaction", {}).get("self")
        download_fields = getattr(transaction_spec, "download", []) if transaction_spec else []
        upload_fields = getattr(transaction_spec, "upload", []) if transaction_spec else []
        is_long_running = self.transaction_name in self.step_type.get_long_running_method_names()

        object.__setattr__(self, "transaction", transaction)
        object.__setattr__(self, "type_hints", type_hints)
        object.__setattr__(self, "signature", signature)
        object.__setattr__(self, "transaction_parameter_names", transaction_parameter_names)
        object.__setattr__(self, "return_type", type_hints.get("return", type(None)))
        object.__setattr__(self, "download_fields", download_fields)
        object.__setattr__(self, "upload_fields", upload_fields)
        object.__setattr__(self, "is_long_running", is_long_running)
        object.__setattr__(self, "tool_signature", self._make_tool_signature())

    def _make_tool_signature(self) -> inspect.Signature:
        custom_parameters: list[inspect.Parameter] = []
        for param_name in self.transaction_parameter_names:
            param = self.signature.parameters[param_name]
            param_type = self.type_hints.get(param_name, Any)
            custom_parameters.append(
                param.replace(
                    annotation=Annotated[
                        param_type,
                        Field(description=f"Transaction argument '{param_name}'."),
                    ],
                ),
            )

        return inspect.Signature(
            [
                inspect.Parameter(
                    "ctx",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[Context, Field(description="MCP request context.")],
                ),
                inspect.Parameter(
                    "project_name",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[str, Field(description="Name of the project containing the transaction.")],
                ),
                *custom_parameters,
            ],
            return_annotation=self.return_type if not self.is_long_running else type(None),
        )

    @property
    def description(self) -> str:
        details = [
            f"Download step fields: {self._format_field_names(self.download_fields)}.",
            f"Upload step fields: {self._format_field_names(self.upload_fields)}.",
            f"Transaction args: {self._format_field_names(self.transaction_parameter_names)}.",
            f"Return type: {self._format_return_type()}.",
        ]
        base_description = inspect.getdoc(self.transaction) or (
            f"Run transaction '{self.transaction_name}' on step '{self.step_name}'."
        )
        suffix = (
            " It continues after the tool call starts it."
            if self.is_long_running
            else " It completes during the tool call."
        )
        return f"{base_description} {' '.join(details)}{suffix}"

    @staticmethod
    def _format_field_names(field_names: list[str]) -> str:
        return ", ".join(field_names) if field_names else "none"

    def _format_return_type(self) -> str:
        if self.return_type is type(None):
            return "None"
        return inspect.formatannotation(self.return_type)
