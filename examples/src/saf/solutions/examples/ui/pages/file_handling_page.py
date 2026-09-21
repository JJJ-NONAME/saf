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

# ©2025, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Frontend of the file handling page."""


import base64

from ansys.saf.glow.client import DashClient, callback
import dash
from dash_extensions.enrich import Input, Output, State, dcc, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from saf.solutions.examples.solution.definition import ExamplesSolution

dash.register_page(
    __name__,
    name="File Handling",
    path_template="/projects/<project_id>/file-handling",
    icon_asset_name="game-icons--crossed-air-flows.svg",
    icon_asset_path="icons",
)


def layout(project: ExamplesSolution) -> html.Div:
    """Layout of the file handling example page."""
    step = project.steps.file_handling_step
    store_and_access_a_file_card = dmc.Card(
        children=[
            dmc.CardSection(
                dmc.Text("Store and access a file", fw=500, style={"font-size": "17px"}),
                withBorder=True,
                inheritPadding=True,
                py="xs",
            ),
            dmc.Space(h=10),
            dmc.Blockquote(
                "This example demonstrates how to store a file in the storage scope and access it later. "
                "Add text to the file via the text area below and click 'Create file'. "
                "A transaction will be started to create the file and store it in the storage scope. "
                "You can then read the file by clicking 'Read file'.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            dmc.Space(h=10),
            dmc.Divider(label="Create and store the file"),
            dmc.Textarea(
                label="Text to add to the file",
                placeholder="Enter text here...",
                autosize=True,
                minRows=2,
                required=True,
                id="create-file-text-area-1",
            ),
            dmc.Space(h=10),
            dmc.Button(
                "Create file",
                id="create-file-button-1",
                style={"font-size": "16px", "background-color": "#2790F1"},
            ),
            dmc.Space(h=10),
            dmc.Divider(label="Access the file"),
            dmc.Space(h=10),
            dmc.Button(
                "Read file",
                id="read-file-button-1",
                style={"font-size": "16px", "background-color": "#2790F1"},
            ),
            dmc.Space(h=10),
            html.Div(
                id="file-content-1",
                style={"maxHeight": "600px", "width": "100%", "overflowY": "scroll"},
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        style={"width": 500},
    )

    modifiy_file_card = dmc.Card(
        children=[
            dmc.CardSection(
                dmc.Text("Access and modify a file", fw=500, style={"font-size": "17px"}),
                withBorder=True,
                inheritPadding=True,
                py="xs",
            ),
            dmc.Space(h=10),
            dmc.Blockquote(
                "This example demonstrates how to access and modify a file. "
                "The EntityHandle is intended to represent an immutable value. "
                "Therefore, you must not modify the file directly. "
                "Instead, you can create a copy using the get_copy() method, modify it, and then store it. "
                "Use the text area below to modify the file content. "
                "Then click 'Modify file' to create a new file with the modified content. ",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            dmc.Space(h=10),
            dmc.Divider(label="Access and modify the file"),
            dmc.Textarea(
                label="Text to add to the existing file",
                placeholder="Enter text here...",
                autosize=True,
                minRows=2,
                required=True,
                id="modify-file-text-area-2",
            ),
            dmc.Space(h=10),
            dmc.Button(
                "Modify file",
                id="modify-file-button-2",
                style={"font-size": "16px", "background-color": "#2790F1"},
            ),
            dmc.Space(h=10),
            dmc.Divider(label="Access the file"),
            dmc.Space(h=10),
            html.Div(
                id="file-content-2",
                style={"maxHeight": "600px", "width": "100%", "overflowY": "scroll"},
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        style={"width": 500},
    )

    access_method_assets_card = dmc.Card(
        children=[
            dmc.CardSection(
                dmc.Text("Access method assets", fw=500, style={"font-size": "17px"}),
                withBorder=True,
                inheritPadding=True,
                py="xs",
            ),
            dmc.Space(h=10),
            dmc.Blockquote(
                "This example demonstrates how to access a method asset from a transaction method. "
                "Click 'Read method asset file' to start a transaction that will read a file from the method asset. "
                "The content of the file will be displayed below. ",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            dmc.Space(h=10),
            dmc.Button(
                "Read method asset file",
                id="read-file-button-2",
                style={"font-size": "16px", "background-color": "#2790F1"},
            ),
            dmc.Space(h=10),
            html.Div(
                id="file-content-3",
                style={"maxHeight": "600px", "width": "100%", "overflowY": "scroll"},
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        style={"width": 500},
    )

    store_uploaded_file_from_ui = dmc.Card(
        children=[
            dmc.CardSection(
                dmc.Text("Store uploaded image", fw=500, style={"font-size": "17px"}),
                withBorder=True,
                inheritPadding=True,
                py="xs",
            ),
            dmc.Space(h=10),
            dmc.Blockquote(
                "This example shows how to store a file (.png) uploaded from the UI. "
                "Use the upload component below to select an image file. "
                "The selected image will be stored in the storage scope and displayed below.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            dmc.Space(h=10),
            dcc.Upload(
                id="upload-file",
                multiple=False,
                accept=".png",
                children=html.Div(
                    "Drag and drop or click to select an image to upload",
                ),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
            ),
            dmc.Space(h=10),
            dmc.Image(id="uploaded-image", fallbackSrc="Placeholder"),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        style={"width": 500},
    )

    store_and_access_a_directory_card = dmc.Card(
        children=[
            dmc.CardSection(
                dmc.Text("Store and access directory content", fw=500, style={"font-size": "17px"}),
                withBorder=True,
                inheritPadding=True,
                py="xs",
            ),
            dmc.Space(h=10),
            dmc.Blockquote(
                "This example demonstrates how to store a directory in the storage scope and access it later. "
                "Use the relative file path input to generate a file under a directory structure. "
                "Add text to the file via the text area below and click 'Create file'. "
                "A transaction will be started to create the file and parent directories and store them in "
                "the storage scope. You can then read the file by clicking 'Read file'.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            dmc.Space(h=10),
            dmc.Divider(label="Create and store the folder and file"),
            dmc.Space(h=10),
            dmc.TextInput(
                label="Relative file path",
                required=True,
                placeholder="/dir-A/dir-B/file.txt",
                id="file-path-input",
            ),
            dmc.Space(h=10),
            dmc.Textarea(
                label="Text to add to the file",
                placeholder="Enter text here...",
                autosize=True,
                minRows=2,
                required=True,
                id="create-file-text-area-5",
            ),
            dmc.Space(h=10),
            dmc.Divider(label="Access the file"),
            dmc.Space(h=10),
            dmc.Button(
                "Create file",
                id="create-file-button-5",
                style={"font-size": "16px", "background-color": "#2790F1"},
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        style={"width": 500},
    )

    return html.Div(
        [
            html.H1("File Handling", className="display-3", style={"font-size": "40px", "font-weight": "bold"}),
            dmc.Blockquote(
                "Use BDM to manipulate files/folders in the storage scope.",
                icon=DashIconify(icon="material-symbols:info", width=30),
                style={"font-size": "18px", "fontStyle": "italic"},
            ),
            html.Br(),
            dmc.Grid(
                [
                    dmc.GridCol(
                        [
                            store_and_access_a_file_card,
                            dmc.Space(h=10),
                            modifiy_file_card,
                        ],
                        span=4,
                    ),
                    dmc.GridCol(
                        [
                            access_method_assets_card,
                            dmc.Space(h=10),
                            store_uploaded_file_from_ui,
                        ],
                        span=4,
                    ),
                    dmc.GridCol(store_and_access_a_directory_card, span=4),
                ],
                gutter="xs",
                grow=True,
            ),
            html.Div(id="notifications-container"),
            DashClient.create_event_listener(step, stream_name="my-stream", id="ws"),
        ],
        style={"paddingLeft": "20px"},
    )


@callback(
    Output("notifications-container", "children"),
    Input("create-file-button-1", "n_clicks"),
    State("create-file-text-area-1", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def create_file(n_clicks: int, text: str, project: ExamplesSolution) -> str:
    """Create a file with the given text."""
    try:
        project.steps.file_handling_step.store_my_file_handle(text=text)
        title, icon, message = "Success", "ep:success-filled", f"File created successfully."
    except Exception as e:
        title, icon, message = "Error", "material-symbols:error", f"Failed to create file: {str(e)}"

    return dmc.Notification(
        title=title,
        message=message,
        icon=DashIconify(icon=icon),
        action="show",
        id="create-file-notification",
    )


@callback(
    Output("notifications-container", "children"),
    Output("file-content-1", "children"),
    Input("read-file-button-1", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def read_file(n_clicks: int, project: ExamplesSolution) -> str:
    """Read the file created in the storage scope."""
    content = ""
    try:
        storage_scope = project.storage_scope
        content = storage_scope.get_text(project.steps.file_handling_step.my_file_handle)
        title, icon, message = "Success", "ep:success-filled", f"File read successfully."
    except Exception as e:
        title, icon, message = "Error", "material-symbols:error", f"Failed to read file: {str(e)}"

    return (
        dmc.Notification(
            title=title,
            message=message,
            icon=DashIconify(icon=icon),
            action="show",
            id="read-file-notification",
        ),
        html.Div(
            [
                html.Pre(
                    content,
                    style={"whiteSpace": "pre-wrap", "wordBreak": "break-all", "fontSize": "10px"},
                )
            ]
        ),
    )


@callback(
    Output("notifications-container", "children"),
    Output("file-content-2", "children"),
    Input("modify-file-button-2", "n_clicks"),
    State("modify-file-text-area-2", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def modify_file(n_clicks: int, text: str, project: ExamplesSolution) -> str:
    """Create a file with the given text."""
    content = ""
    try:
        storage_scope = project.storage_scope
        root = storage_scope.get_storage_root()
        new_file = root / "modified_file.txt"
        storage_scope.get_copy(project.steps.file_handling_step.my_file_handle, new_file)
        content = new_file.read_text()
        content += "\n" + text
        new_file.write_text(content)
        project.steps.file_handling_step.my_file_handle = storage_scope.store(new_file)
        title, icon, message = "Success", "ep:success-filled", f"File modified successfully."
    except Exception as e:
        title, icon, message = "Error", "material-symbols:error", f"Failed to modify file: {str(e)}"

    return (
        dmc.Notification(
            title=title,
            message=message,
            icon=DashIconify(icon=icon),
            action="show",
            id="modify-file-notification",
        ),
        html.Div(
            [
                html.Pre(
                    content,
                    style={"whiteSpace": "pre-wrap", "wordBreak": "break-all", "fontSize": "10px"},
                )
            ]
        ),
    )


@callback(
    Output("notifications-container", "children"),
    Input("read-file-button-2", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def trigger_transaction_with_method_assets(n_clicks: int, project: ExamplesSolution) -> str:
    """Create a file with the given text."""
    try:
        project.steps.file_handling_step.access_and_use_method_asset_file()
        title, icon, message = "Success", "ep:success-filled", f"Transaction started successfully."
    except Exception as e:
        title, icon, message = "Error", "material-symbols:error", f"Failed to start transaction: {str(e)}"

    return dmc.Notification(
        title=title,
        message=message,
        icon=DashIconify(icon=icon),
        action="show",
        id="trigger-transaction-notification",
    )


@callback(
    Output("file-content-3", "children"),
    Input("ws", "message"),
    prevent_initial_call=True,
)
def display_method_asset_content(message: dict) -> str:
    """Create a file with the given text."""
    content = message["data"].strip('"').replace("\\n", "\n")
    return content


@callback(
    Output("uploaded-image", "src"),
    Input("upload-file", "contents"),
    State("upload-file", "filename"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def upload_file(contents: str, filename: str, project: ExamplesSolution) -> str:
    """Create a file with the given text."""
    content_type, content_string = contents.split(",")
    content = base64.b64decode(content_string)
    storage_scope = project.storage_scope
    filepath = storage_scope.get_storage_root() / filename
    filepath.write_bytes(content)
    project.steps.file_handling_step.my_uploaded_file_handle = storage_scope.store(filepath)
    return project.steps.file_handling_step.get_entity_url("my_uploaded_file_handle")


@callback(
    Output("notifications-container", "children"),
    Input("create-file-button-5", "n_clicks"),
    State("file-path-input", "value"),
    State("create-file-text-area-5", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def create_directory(n_clicks: int, relative_path: str, text: str, project: ExamplesSolution) -> str:
    """Create a file with the given text."""
    try:
        project.steps.file_handling_step.store_my_directory_handle(relative_path=relative_path, text=text)
        title, icon, message = "Success", "ep:success-filled", f"Directory created successfully."
    except Exception as e:
        title, icon, message = "Error", "material-symbols:error", f"Failed to create directory: {str(e)}"

    return dmc.Notification(
        title=title,
        message=message,
        icon=DashIconify(icon=icon),
        action="show",
        id="trigger-transaction-notification",
    )
