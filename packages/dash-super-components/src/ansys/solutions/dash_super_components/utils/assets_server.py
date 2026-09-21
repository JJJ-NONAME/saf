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


"""
Provides a helper function for adding asset endpoints to a Dash application.

Some components in this library (for example, :class:`LogsSupervisor`) rely on
custom JavaScript and other static assets that are shipped with the package.
Rather than requiring consumers to copy those files into their application's
assets folder, this helper module allows to register a simple Flask route that
serves files directly from the package's bundled ``assets`` directory.
"""

from pathlib import Path

from dash_extensions.enrich import DashProxy
from flask import send_from_directory
from flask.wrappers import Response


def add_super_components_assets(app: DashProxy) -> None:
    """
    Add a Flask endpoint to serve static assets from the library.

    This allows components to reference assets like JavaScript or CSS files
    without requiring the user to manually copy them to their app's assets folder.

    Parameters
    ----------
    app : DashProxy
        The ``DashProxy`` application instance (from ``dash_extensions.enrich``).
    """
    assets_folder = str(Path(__file__).parent.parent / "assets")

    @app.server.route(app.get_relative_path("/super-components/<path:filename>"))
    def serve_super_components_assets(filename: str) -> Response:
        """Serve static assets from the super-components assets folder."""
        return send_from_directory(assets_folder, filename)
