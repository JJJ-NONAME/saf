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

# ©2026, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.
"""This module defines the routes needed to serve ADR media and static assets for the beam bending report."""
import flask

from saf.solutions.examples.solution.scripts.beam_bending.report.adr_config import get_adr_config


def serve_report_media_assets(app):
    """Serve media assets, such as images, for the ADR report."""

    @app.server.route("/media/<path:filename>")
    def serve_media_assets(filename):
        path_to_media = get_adr_config()["PATH_TO_MEDIA"]
        return flask.send_from_directory(str(path_to_media), filename)


def serve_report_static_assets(app):
    """Serve static assets, such as CSS and JavaScript files, for the ADR report."""

    @app.server.route("/static_assets/<path:filename>")
    def serve_static_files(filename):
        path_to_static = get_adr_config()["PATH_TO_STATIC"]
        return flask.send_from_directory(str(path_to_static), filename)


def register_adr_asset_routes(app):
    """Register the routes to serve ADR media and static assets."""
    serve_report_media_assets(app)
    serve_report_static_assets(app)
