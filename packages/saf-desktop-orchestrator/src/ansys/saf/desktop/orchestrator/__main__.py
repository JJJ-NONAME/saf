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

# IMPORTANT: Keep this at the top of the entry point. This is needed to redirect all I/O and avoid crashes
# when launching the orchestrator using pythonw.exe in Windows, which is done for installed solutions
# built with ansys-saf-desktop-installer. Similarly, child processes launched should have their I/O redirected
# if they are launched using pythonw.exe.
import os
import platform
import sys

if platform.system() == "Windows" and sys.executable.endswith("pythonw.exe"):
    sys.stdout = open(os.devnull, "w")  # noqa: PTH123, SIM115
    sys.stderr = open(os.devnull, "w")  # noqa: PTH123, SIM115

import argparse
from pathlib import Path

from ansys.saf.desktop.orchestrator._orchestration.run_solution_stack import run_solution_stack

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for running the solution stack")
    parser.add_argument(
        "--solution-main-module-name",
        type=str,
        required=True,
        help=(
            "the full python module name for the module containing the glow main call, e.g. ansys.solutions.simple.main"
        ),
    )
    parser.add_argument(
        "--portal",
        action="store_true",
        help="Whether to run Portal. If set, the portal UI will open instead of the solution UI.",
    )
    parser.add_argument("--no-ui", action="store_true", help="Whether to run the UI server.")
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Whether to open the UI in a browser instead of a window.",
    )
    parser.add_argument("--streamlit-ui", action="store_true", help="Whether to run Streamlit as UI server.")
    parser.add_argument(
        "--project-display-name",
        type=str,
        default=None,
        help="The display_name of the project to open or create. This option cannot be used if Portal is running.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path.cwd() / ".env",
        help="Load environment variables from this file.",
    )
    parser.add_argument(
        "--no-automatic-project-migration",
        action="store_true",
        help="Disable automatic schema migration for old projects.",
    )
    parser.add_argument(
        "--log-to-files",
        action="store_true",
        help=(
            "Log to files and disable OTEL dashboard. "
            "(Note that this sets the GLOW env vars for log config files, overriding any existing value)"
        ),
    )
    parser.add_argument(
        "--pre-load",
        action="store_true",
        help="Whether to run pre-load mode (run everything except don't open window and shutdown immediately).",
    )
    args = parser.parse_args()

    env_file: Path | None = None
    if Path(args.env_file).is_file():
        env_file = Path(args.env_file)

    run_solution_stack(
        solution_main_module_name=args.solution_main_module_name,
        portal=args.portal,
        no_ui=args.no_ui,
        browser=args.browser,
        streamlit_ui=args.streamlit_ui,
        input_project_display_name=args.project_display_name,
        env_file=env_file,
        enable_automatic_project_migration=not args.no_automatic_project_migration,
        log_to_files=args.log_to_files,
        pre_load=args.pre_load,
    )
