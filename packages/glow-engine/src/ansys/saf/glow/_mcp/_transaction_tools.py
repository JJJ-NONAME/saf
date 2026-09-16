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
from collections.abc import Callable
from typing import Annotated, Any, get_type_hints

from fastmcp import FastMCP
from fastmcp.server import Context
from fastmcp.tools import ToolResult
from pydantic import Field

from ansys.saf.glow._mcp._resolution import get_solution_config, get_step
from ansys.saf.glow._mcp._transaction_metadata import TransactionMetadata
from ansys.saf.glow._utilities.conversion import python_identifier_to_url_part
from ansys.saf.glow.client import LongRunning
from ansys.saf.glow.solution import MethodStatus, Solution


def _make_tool_func(metadata: TransactionMetadata, client_factory: Callable[..., Any]) -> Callable[..., Any]:
    tool_signature = metadata.tool_signature

    def _run(*args: Any, **kwargs: Any) -> Any:
        bound = tool_signature.bind_partial(*args, **kwargs)
        ctx = bound.arguments["ctx"]
        project_name = bound.arguments["project_name"]
        transaction_kwargs = {
            name: bound.arguments[name] for name in metadata.transaction_parameter_names if name in bound.arguments
        }

        sol_class, sol_api_url = get_solution_config(ctx)

        with client_factory(sol_class, sol_api_url) as client:
            project = client.get_project(project_name)
            step = get_step(project, metadata.step_name)
            transaction_obj = getattr(step, metadata.transaction_name, None)
            if not transaction_obj:
                raise ValueError(
                    f"Transaction '{metadata.transaction_name}' not found on step '{metadata.step_name}'.",
                )
            return_valued = transaction_obj(**transaction_kwargs)
            if isinstance(return_valued, LongRunning):
                return None
            return return_valued

    _run.__signature__ = tool_signature  # pyright: ignore[reportFunctionMemberAccess]
    # pydantic's TypeAdapter resolves parameter types from __annotations__, not just __signature__.
    _run.__annotations__ = {name: param.annotation for name, param in tool_signature.parameters.items()}
    _run.__annotations__["return"] = tool_signature.return_annotation

    return _run


def register_transaction_tools(
    app: FastMCP,
    solution_class: type[Solution],
    client_factory: Callable[..., Any],
) -> None:
    @app.tool()
    def wait_for_longrunning_transaction(  # pyright: ignore[reportUnusedFunction]
        ctx: Annotated[Context, Field(description="MCP request context.")],
        project_name: Annotated[str, Field(description="Name of the project containing the transaction.")],
        step_name: Annotated[str, Field(description="Name of the step containing the transaction.")],
        transaction_name: Annotated[str, Field(description="Name of the long-running transaction to wait for.")],
        timeout: Annotated[int, Field(description="Maximum time to wait, in seconds.")] = 600,
    ) -> Any | None:
        """Wait for a started long-running transaction to finish."""
        configured_solution_class, solution_api_url = get_solution_config(ctx)

        with client_factory(configured_solution_class, solution_api_url) as client:
            project = client.get_project(project_name)
            step = get_step(project, step_name)
            if transaction_name not in step._step_model_type.get_long_running_method_names():
                raise ValueError(
                    f"Transaction '{transaction_name}' on step '{step_name}' is not a long-running transaction.",
                )
            # We manually build the LongRunning object due to a Client limitation.
            # longrunning's wait()/return value cannot be retrieved from a different context where it's launched.
            # For example, another callback or another MCP tool. In the future We would like to have
            # something like `return_value = step.my_transaction_method.wait()`, assuming that somewhere else
            # we have already done `step.my_transaction_method()`.
            method_id = python_identifier_to_url_part(transaction_name)
            method_url = f"{step._url}:{method_id}"
            method = getattr(step._step_model_type, transaction_name)  # already validated to exist above
            return_type = get_type_hints(method).get("return")
            long_running = LongRunning(
                step._step_model_type,
                step._step_name,
                transaction_name,
                method_url,
                client.http_client,
                return_type,
            )
            if long_running.get_state().status == MethodStatus.RunRequired:
                raise RuntimeError(
                    f"Transaction '{transaction_name}' on step '{step_name}' has not been started.",
                )
            return_value = long_running.wait(timeout=timeout)

        # This tool is shared by every long-running transaction, so its declared output schema
        # can't reflect each transaction's actual return type. Mirror behaviour of sync transactions,
        # so callers still get structured content matching the transaction's real return value,
        # instead of only text content.
        if return_value is None or isinstance(return_value, dict):
            return return_value  # pyright: ignore[reportUnknownVariableType]
        return ToolResult(content=return_value, structured_content={"result": return_value})

    for step_name, step_type in solution_class.get_steps_fields().items():
        for transaction_name in step_type.get_transaction_method_names():
            tool_name = f"{step_name}__{transaction_name}"
            metadata = TransactionMetadata(step_name, transaction_name, step_type)
            tool_func = _make_tool_func(metadata, client_factory)
            tool_func.__name__ = tool_name
            tool_func.__qualname__ = tool_name
            app.tool(name=tool_name, description=metadata.description)(tool_func)
