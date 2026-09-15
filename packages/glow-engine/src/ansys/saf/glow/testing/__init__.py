# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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
_pytest_available = True
try:
    import httpx2  # noqa: F401  # pyright: ignore[reportUnusedImport]
    import pytest  # noqa: F401  # pyright: ignore[reportUnusedImport]
    import pytest_mock  # noqa: F401  # pyright: ignore[reportUnusedImport]
except ImportError:
    _pytest_available = False

__all__: list[str] = []
if _pytest_available:
    from ansys.saf.glow._testing.solution import (
        # Import private fixtures so that pytest can discover them
        _api_testclient,  # type: ignore   # noqa: F401
        _created_dash_callback_clients,  # type: ignore   # noqa: F401
        _created_method_clients,  # type: ignore   # noqa: F401
        _dash_callback_client_factory,  # type: ignore   # noqa: F401
        _glow_client,  # type: ignore   # noqa: F401
        _method_client_factory,  # type: ignore   # noqa: F401
        _mock_glow_client_internal_clients,  # type: ignore   # noqa: F401
        _shared_test_client_portal,  # type: ignore   # noqa: F401
        _solution_api_client,  # type: ignore   # noqa: F401
        _solution_settings,  # type: ignore   # noqa: F401
        _temporary_app_data,  # type: ignore   # noqa: F401
        # Import public fixtures
        client_project,
        configure_solution,
        dash_http_client,
        init_dashclient,
        is_msg_in_logs,
        mock_product_instance,
        project_display_name,
        project_files_dir,
        project_id,
        project_name,
        solution_logs,
    )

    __all__ += [
        "configure_solution",
        "dash_http_client",
        "init_dashclient",
        "project_display_name",
        "client_project",
        "project_id",
        "project_name",
        "project_files_dir",
        "solution_logs",
        "is_msg_in_logs",
        "mock_product_instance",
    ]
