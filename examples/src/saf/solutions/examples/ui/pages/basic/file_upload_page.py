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

# ©2023, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.
"""Frontend of the File upload step."""
import base64
import io
from urllib import parse, request

from ansys.saf.glow.client import callback
import dash
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, dcc, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from saf.solutions.examples.solution.definition import ExamplesSolution

dash.register_page(
    __name__,
    name="File Upload",
    path_template="/projects/<project_id>/file-upload",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout() -> html.Div:
    """Layout of the File upload example page."""

    return html.Div(
        [
            html.H1("File upload", className="display-3", style={"font-size": "40px", "font-weight": "bold"}),
            dmc.Blockquote(
                "Use SAF GLOW's uploader to upload files to a solution project\
                and display the file sizes in a file a solution UI.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            html.Br(),
            html.Br(),
            dcc.Upload(
                id="dcc-file-upload",
                children="Drag-and-drop your sample files here",
                multiple=True,
                style={
                    "width": "100%",
                    "height": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "backgroundColor": "#f8f9fa",  # light grey color
                    "textAlign": "center",
                    "lineHeight": "50px",
                    "backgroundColor": "var(--mantine-color-body)",
                    "color": "var(--mantine-color-text)",
                },
            ),
            html.Div(
                id="upload-output",
                children="",
                style={"padding": "5px"},
            ),
            dmc.Button(
                "Check file size",
                id="check-size-button",
                variant="filled",
                radius="sm",
                style={
                    "font-size": "16px",
                    "background-color": "#2790F1",
                    "width": "20%",
                },
                leftSection=DashIconify(icon="fa-solid:info-circle"),
            ),
            html.Div(
                id="file-size",
                style={
                    "height": "600px",
                    "width": "100%",
                    "overflowY": "scroll",
                    "border": "1px solid #d9d9d9",
                    "borderRadius": "4px",
                    "padding": "8px",
                    "marginTop": "10px",
                },
            ),
            html.Br(),
            html.Br(),
        ],
        style={"paddingLeft": "20px"},
    )


@callback(
    Output("upload-output", "children"),
    Input("dcc-file-upload", "contents"),
    State("dcc-file-upload", "filename"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def upload_files_to_the_project(uploaded_file_contents, uploaded_filenames, project: ExamplesSolution) -> html.P:
    """Upload files to the project with the Dash Core Components Upload component."""
    if uploaded_filenames:
        uploaded_files = []
        if uploaded_file_contents:
            for filename, content in zip(uploaded_filenames, uploaded_file_contents):
                data = base64.decodebytes(content.encode("utf8").split(b";base64,")[1])
                _upload_data_to_project(project, filename, "ProjectFiles", data)
                uploaded_files.append(filename)
            return html.P(f"Successfully uploaded files: {', '.join(uploaded_files)}")
    raise PreventUpdate


def _upload_data_to_project(project: ExamplesSolution, filename: str, upload_folder_path: str, data) -> None:
    """Upload file data to the project."""
    return project.upload_file(f"{upload_folder_path}/{filename}", io.BytesIO(data))


@callback(
    Output("file-size", "children"),
    Input("check-size-button", "n_clicks"),
    State("url", "pathname"),
)
def get_file_size(n_clicks, project: ExamplesSolution) -> list[html.P | html.Ul]:
    """Get the file size of the uploaded files."""
    if n_clicks:
        step = project.steps.basic_step
        uploaded_files = step.project_files.list_files()
        if uploaded_files:
            file_sizes = []
            for file in uploaded_files:
                file_size = _get_file_size(file.url)
                filename = _get_file_name(file.url)
                file_sizes.append((filename, file_size))
            return [
                html.P("Project file details:", className="lead", style={"font-size": "20px"}),
                html.Ul([html.Li(f"{file[0]} (Size: {file[1]} bytes)") for file in file_sizes]),
            ]
    return []


def _get_file_name(url: str) -> str:
    """Get the file name from the URL."""
    return parse.urlsplit(url).path.split("/")[-1]


def _get_file_size(url: str) -> int:
    """Get the file size from the URL."""
    return len(request.urlopen(url).read())
