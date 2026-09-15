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

# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.


from typing import Any

from ansys.saf.glow.solution import MethodState
from dash_extensions.enrich import no_update


def get_fluent_page_controls_with_default() -> dict[str, dict[str, Any]] | Any:
    """Initialize the state of controls on the Fluent instance management page."""
    return {
        "launch_fluent": {"disabled": no_update, "loading": no_update, "transaction": "launch_fluent"},
        "shutdown_fluent": {"disabled": no_update, "loading": no_update, "transaction": "shutdown_fluent"},
        "import_fluent_mesh": {"disabled": no_update, "loading": no_update, "transaction": "import_mesh"},
        "run_fluent_simulation": {"disabled": no_update, "loading": no_update, "transaction": "run_simulation"},
    }


def get_mapdl_page_controls_with_default() -> dict[str, dict[str, Any]] | Any:
    """Initialize the state of controls on the MAPDL instance management page."""
    return {
        "launch_mapdl": {"disabled": no_update, "loading": no_update, "transaction": "launch_mapdl"},
        "shutdown_mapdl": {"disabled": no_update, "loading": no_update, "transaction": "shutdown_mapdl"},
        "solve_model": {"disabled": no_update, "loading": no_update, "transaction": "solve_model"},
        "postprocess_results": {"disabled": no_update, "loading": no_update, "transaction": "postprocessing"},
    }


def get_mechanical_page_controls_with_default() -> dict[str, dict[str, Any]] | Any:
    """Initialize the state of controls on the Mechanical instance management page."""
    return {
        "launch_mechanical": {"disabled": no_update, "loading": no_update, "transaction": "launch_mechanical"},
        "shutdown_mechanical": {"disabled": no_update, "loading": no_update, "transaction": "shutdown_mechanical"},
        "run_script": {"disabled": no_update, "loading": no_update, "transaction": "run_script"},
        "download_output_file": {"disabled": no_update, "loading": no_update, "transaction": "download_output_file"},
    }


def get_optislang_page_controls_with_default() -> dict[str, dict[str, Any]] | Any:
    """Initialize the state of controls on the optiSLang instance management page."""
    return {
        "launch_optislang": {"disabled": no_update, "loading": no_update, "transaction": "launch_optislang"},
        "shutdown_optislang": {"disabled": no_update, "loading": no_update, "transaction": "shutdown_optislang"},
        "evaluate_design": {"disabled": no_update, "loading": no_update, "transaction": "evaluate_design"},
        "refine_design": {"disabled": no_update, "loading": no_update, "transaction": "refine_design"},
    }


def get_aedt_page_controls_with_default() -> dict[str, dict[str, Any]] | Any:
    """Initialize the state of controls on the AEDT instance management page."""
    return {
        "launch_aedt": {"disabled": no_update, "loading": no_update, "transaction": "launch_aedt"},
        "shutdown_aedt": {"disabled": no_update, "loading": no_update, "transaction": "shutdown_aedt"},
        "add_rectangle": {"disabled": no_update, "loading": no_update, "transaction": "add_rectangle"},
        "analyze_design": {"disabled": no_update, "loading": no_update, "transaction": "analyze_design"},
    }


def handle_method_event(
    method_state: MethodState,
    notification_id: str,
    success_msg: str,
    error_msg: str,
    success_auto_close: int | bool = 5000,
    error_auto_close: int | bool = False,
) -> list[dict[str, Any]]:
    """Process a backend method event and update controls/notification accordingly.

    Parameters
    ----------
    method_state : MethodState
        The state of the backend method.
    notification_id : str
        The ID of the notification to update.
    success_msg : str
        The message to display if the method completed successfully.
    error_msg : str
        The message to display if the method failed.
    success_auto_close : int | bool, optional
        Time in milliseconds after which the success notification should auto-close,
        or False to disable auto-close. Default is 5000 (5 seconds).
    error_auto_close : int | bool, optional
        Time in milliseconds after which the error notification should auto-close,
        or False to disable auto-close. Default is False (no auto-close).
    """
    notification = no_update

    if method_state.status.value == "completed":
        notification = [
            dict(
                title="Success",
                id=notification_id,
                action="update",
                message=success_msg,
                color="green",
                autoClose=success_auto_close,
                withCloseButton=True,
                loading=False,
            )
        ]
    elif method_state.status.value == "failed":
        notification = [
            dict(
                title="Error",
                id=notification_id,
                action="update",
                message=error_msg,
                color="red",
                autoClose=error_auto_close,
                withCloseButton=True,
                loading=False,
            )
        ]

    return notification
