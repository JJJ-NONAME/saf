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
"""Expectations about the MCP server surface, shared by the unit and end-to-end test suites."""

import pytest

from tests.mocks.solution_end_to_end.solution.definition import EndToEndSolution

STATIC_TOOL_DESCRIPTIONS = {
    "create_project": "Create a solution project.",
    "list_projects": (
        "List solution projects with pagination, ordering, and optional filtering.\n"
        "\n"
        "Use this to discover existing projects and their resource names before reading,\n"
        "exporting, or deleting them."
    ),
    "delete_projects": (
        "Delete one or more solution projects and their project directories.\n"
        "\n"
        "This is destructive and irreversible. Deletion is attempted for every name, so a\n"
        "failure on one project does not prevent the others from being deleted. Returns the\n"
        "outcome per project name: 'deleted' on success, or the error message on failure."
    ),
    "import_project": (
        "Import a '.safx' project archive as a new solution project.\n"
        "\n"
        "The archive is a binary zip, so its content must be base64-encoded. Returns the\n"
        "resource name of the imported project."
    ),
    "export_project": (
        "Export a solution project as a '.safx' project archive.\n"
        "\n"
        "The archive is a binary zip, so it is returned base64-encoded and must be decoded\n"
        "before being written to a file."
    ),
    "set_fields": "Set field values on a solution step.",
    "get_fields": "Get field values from a solution step.",
    "upload_file": "Upload file content to an entity handle field.",
    "download_file": "Download file content from an entity handle field.",
    "wait_for_longrunning_transaction": "Wait for a started long-running transaction to finish.",
}

STATIC_TOOL_PARAMETER_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "create_project": {
        "display_name": "Project name displayed to the user. If not set, a name is generated automatically.",
    },
    "list_projects": {
        "page_size": "Maximum number of projects to return per page. Defaults to 100, capped at 100.",
        "page": "Page number to return, starting at 1.",
        "order_by": (
            "Comma-separated fields to order by, ascending unless suffixed with ' desc'. "
            "Supported fields: display_name, description, date_created, date_modified, name. "
            "For example: 'date_modified desc, name'."
        ),
        "filter": (
            "Filter expression of the form '<field> <operator> <value> [AND ...]'. "
            "The display_name and description fields only support '=' as a case-insensitive "
            "contains match. The date_created and date_modified fields support =, !=, <, >, <=, >= "
            "with ISO 8601 values. For example: 'display_name = Motor AND date_created >= 2024-01-01'."
        ),
    },
    "delete_projects": {
        "names": "Resource names of the projects to delete, each of the form 'projects/<project_id>'.",
    },
    "import_project": {
        "content": "Base64-encoded content of the '.safx' project archive to import.",
        "display_name": "Project name displayed to the user.",
    },
    "export_project": {"project_name": "Name of the project to export."},
    "set_fields": {
        "project_name": "Name of the project to update.",
        "step_name": "Name of the step containing the fields.",
        "fields": "Field names mapped to their new values.",
    },
    "get_fields": {
        "project_name": "Name of the project to read.",
        "step_name": "Name of the step containing the fields.",
        "field_names": "Names of the fields to read.",
    },
    "upload_file": {
        "project_name": "Name of the project to update.",
        "step_name": "Name of the step containing the entity handle field.",
        "entity_handle_name": "Name of the entity handle field to write.",
        "content": "File content to upload.",
    },
    "download_file": {
        "project_name": "Name of the project to read.",
        "step_name": "Name of the step containing the entity handle field.",
        "entity_handle_name": "Name of the entity handle field to read.",
    },
    "wait_for_longrunning_transaction": {
        "project_name": "Name of the project containing the transaction.",
        "step_name": "Name of the step containing the transaction.",
        "transaction_name": "Name of the long-running transaction to wait for.",
        "timeout": "Maximum time to wait, in seconds.",
    },
}

TRANSACTION_TOOL_PARAMETER_DESCRIPTIONS = {
    "project_name": "Name of the project containing the transaction.",
    "field_1": "Transaction argument 'field_1'.",
    "field_2": "Transaction argument 'field_2'.",
}

TRANSACTION_TOOL_DESCRIPTIONS = {
    "transaction_verification_step__get_field_1_and_2_and_set_the_sum_in_result": (
        "Run the documented sync transaction. It completes during the tool call."
    ),
    "transaction_verification_step__sum_two_floats_with_inputs_and_output": (
        "Run transaction 'sum_two_floats_with_inputs_and_output' on step 'transaction_verification_step'. "
        "It completes during the tool call."
    ),
    "transaction_verification_step__lr_get_field_1_and_2_and_set_the_sum_in_result": (
        "Run the documented long-running transaction. It continues after the tool call starts it."
    ),
    "transaction_verification_step__lr_sum_two_floats_with_inputs_and_output": (
        "Run transaction 'lr_sum_two_floats_with_inputs_and_output' on step 'transaction_verification_step'. "
        "It continues after the tool call starts it."
    ),
}

LONG_RUNNING_DESCRIPTION_SUFFIX = " It continues after the tool call starts it."
SYNC_DESCRIPTION_SUFFIX = " It completes during the tool call."

# tools that take no project name; their failure paths are covered by the project management tests.
TOOLS_WITHOUT_PROJECT_NAME = {"create_project", "list_projects", "delete_projects", "import_project"}

NONEXISTENT_STEP_CASES = [
    pytest.param("set_fields", {"fields": {"any_field": 1.0}}, id="set_fields"),
    pytest.param("get_fields", {"field_names": ["any_field"]}, id="get_fields"),
    pytest.param("upload_file", {"entity_handle_name": "any_field", "content": b"data"}, id="upload_file"),
    pytest.param("download_file", {"entity_handle_name": "any_field"}, id="download_file"),
    pytest.param(
        "wait_for_longrunning_transaction",
        {"transaction_name": "any_transaction"},
        id="wait_for_longrunning_transaction",
    ),
]

NONEXISTENT_PROJECT_CASES = [
    pytest.param("export_project", {}, id="export_project"),
    pytest.param(
        "set_fields",
        {"step_name": "transaction_verification_step", "fields": {"field_1": 1.0}},
        id="set_fields",
    ),
    pytest.param(
        "get_fields",
        {"step_name": "transaction_verification_step", "field_names": ["field_1"]},
        id="get_fields",
    ),
    pytest.param(
        "upload_file",
        {"step_name": "transaction_verification_step", "entity_handle_name": "text_file", "content": b"data"},
        id="upload_file",
    ),
    pytest.param(
        "download_file",
        {"step_name": "transaction_verification_step", "entity_handle_name": "text_file"},
        id="download_file",
    ),
    pytest.param(
        "transaction_verification_step__get_field_1_and_2_and_set_the_sum_in_result",
        {},
        id="sync_transaction",
    ),
    pytest.param(
        "transaction_verification_step__lr_get_field_1_and_2_and_set_the_sum_in_result",
        {},
        id="lr_transaction",
    ),
    pytest.param(
        "wait_for_longrunning_transaction",
        {
            "step_name": "transaction_verification_step",
            "transaction_name": "lr_get_field_1_and_2_and_set_the_sum_in_result",
        },
        id="wait_for_longrunning_transaction",
    ),
]


def transaction_tool_names() -> dict[str, bool]:
    """Map every transaction tool name to whether it is long-running."""
    return {
        f"{step_name}__{transaction_name}": transaction_name in step_type.get_long_running_method_names()
        for step_name, step_type in EndToEndSolution.get_steps_fields().items()
        for transaction_name in step_type.get_transaction_method_names()
    }


def parameter_descriptions(input_schema: dict[str, object]) -> dict[str, str]:
    """Extract the description of every parameter of a tool input schema."""
    properties: dict[str, dict[str, str]] = input_schema["properties"]  # type: ignore[assignment]
    return {name: prop["description"] for name, prop in properties.items()}
