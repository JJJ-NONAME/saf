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


"""Frontend of the input form page."""

from typing import Any

from ansys.saf.glow.client import callback
from ansys.solutions.dash_super_components import InputForm

from ansys.solutions.showcase_dash_super_components.solution.definition import (
    SuperComponentsExamplesSolution,
)
from ansys.solutions.showcase_dash_super_components.solution.simple_step import SimpleStep

try:
    # dash >=3.2.0
    from dash import NoUpdate
except ImportError:
    # dash >=2.18.2, <3.2.0
    from dash._callback import NoUpdate  # pyright: ignore[reportPrivateImportUsage]

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import (
    ALL,
    MATCH,
    Input,
    Output,
    State,
    Trigger,
    callback_context,
    html,
    no_update,
)
import dash_mantine_components as dmc

from ansys.solutions.showcase_dash_super_components.ui.components.page_template import (
    layout as page_layout,
)
from ansys.solutions.showcase_dash_super_components.ui.utilities.common_colors import CommonColors

INFO_CARD_TEXT = [
    (
        "Input Form simplifies the creation of structured parameter forms. It supports "
        "multiple input field types, customizable column layouts (label, fields, unit, "
        "help, description), hidden fields, and callback-driven interactivity such as "
        "reading values, toggling visibility, enabling/disabling rows, and updating "
        "label colors dynamically."
    ),
]

DEFAULT_WHEEL_MATERIAL = "Rubber"
DEFAULT_WHEEL_DIAMETER = 90


def layout(simple_step: SimpleStep) -> html.Div:
    """Layout of the input form page."""
    basic_form = InputForm(
        [
            {
                "fields": [
                    {
                        "type": "TextInput",
                        "id": "basic-name",
                        "label": "Project Name",
                        "placeholder": "Enter project name",
                    },
                ],
            },
            {
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "basic-iterations",
                        "label": "Iterations",
                        "value": 10,
                        "min": 1,
                        "max": 100,
                    },
                ],
            },
        ],
        aio_id="basic-form",
        columns=["fields"],
    )

    sim_job_form = InputForm(
        [
            {
                "id": "job_name",
                "label": "Job Name",
                "fields": [
                    {
                        "type": "TextInput",
                        "id": "job_name",
                        "placeholder": "e.g. turbine-run-001",
                        "required": True,
                        "value": simple_step.sim_job_name,
                    },
                ],
                "description": "Unique identifier for this simulation job.",
            },
            {
                "id": "solver_engine",
                "label": "Solver Engine",
                "fields": [
                    {
                        "type": "Select",
                        "id": "solver_engine",
                        "value": simple_step.sim_job_solver,
                        "data": ["Fluent", "CFX", "Mechanical"],
                        "required": True,
                    },
                ],
                "description": "Simulation backend to use.",
            },
            {
                "id": "output_fields",
                "label": "Output Fields",
                "fields": [
                    {
                        "type": "MultiSelect",
                        "id": "output_fields",
                        "value": simple_step.sim_job_output_fields,
                        "data": ["Velocity", "Pressure", "Temperature", "Stress", "Strain"],
                        "placeholder": "Select output quantities",
                    },
                ],
                "description": "Physical quantities to write to the results file.",
            },
            {
                "id": "mesh_resolution",
                "label": "Mesh Resolution",
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "mesh_x",
                        "value": simple_step.sim_job_mesh_resolution_x,
                        "min": 0.001,
                        "step": 0.005,
                        "decimalScale": 3,
                        "label": "X",
                        "required": True,
                    },
                    {
                        "type": "NumberInput",
                        "id": "mesh_y",
                        "value": simple_step.sim_job_mesh_resolution_y,
                        "min": 0.001,
                        "step": 0.005,
                        "decimalScale": 3,
                        "label": "Y",
                        "required": True,
                    },
                ],
                "unit": "m",
                "description": "Base element size in X and Y directions.",
            },
            {
                "id": "max_runtime",
                "label": "Max Runtime",
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "max_runtime",
                        "value": simple_step.sim_job_max_runtime,
                        "min": 0.5,
                        "max": 72,
                        "step": 0.5,
                        "decimalScale": 1,
                        "required": True,
                    },
                ],
                "unit": "h",
                "description": "Wall-clock time limit before the job is terminated.",
            },
            {
                "id": "save_checkpoints",
                "label": "Save Checkpoints",
                "fields": [
                    {
                        "type": "Checkbox",
                        "id": "save_checkpoints",
                        "checked": simple_step.sim_job_save_checkpoints,
                        "label": "Enabled",
                        "styles": {"label": {"fontSize": "12px"}},
                    },
                ],
                "description": "Write restart files at regular intervals.",
            },
            {
                "id": "email_notifications",
                "label": "Email Notifications",
                "fields": [
                    {
                        "type": "Switch",
                        "id": "email_notifications",
                        "checked": simple_step.sim_job_email_notification,
                        "size": "xs",
                        "radius": "xl",
                        "styles": {"label": {"fontSize": "12px"}},
                    },
                ],
                "description": "Send email on job completion or failure.",
            },
            {
                "id": "cpu_allocation",
                "label": "CPU Allocation",
                "fields": [
                    {
                        "type": "Slider",
                        "id": "cpu_allocation",
                        "value": simple_step.sim_job_cpu_allocation,
                        "min": 10,
                        "max": 100,
                        "step": 10,
                        "size": "sm",
                        "radius": "sm",
                        "updatemode": "drag",
                        "style": {"width": "100%"},
                    },
                ],
                "unit": "%",
                "description": "Share of available HPC cores to allocate.",
            },
            {
                "id": "hpc_token",
                "label": "HPC Token",
                "fields": [
                    {
                        "type": "PasswordInput",
                        "id": "hpc_token",
                        "placeholder": "Paste cluster token",
                        "value": simple_step.sim_job_hpc_token,
                    },
                ],
                "description": "Authentication token for the HPC cluster.",
            },
        ],
        aio_id="sim-job",
        title="Simulation Job Configuration",
        columns=["label", "fields", "unit", "description"],
        column_widths={"label": 2, "fields": 3, "unit": 1, "description": 4},
    )

    solver_settings_form = InputForm(
        [
            {
                "id": "time_step",
                "label": "Time Step",
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "time_step",
                        "value": 0.001,
                        "min": 1e-6,
                        "step": 0.001,
                        "decimalScale": 6,
                        "required": True,
                    },
                ],
                "unit": "s",
                "description": "Integration time step for the solver.",
                "help": [
                    dmc.Image(src="/assets/images/solution-workflow-sketch.png"),
                ],
            },
            {
                "id": "solver_type",
                "label": "Solver Type",
                "fields": [
                    {
                        "type": "Select",
                        "id": "solver_type",
                        "value": "Implicit",
                        "data": ["Explicit", "Implicit"],
                        "required": True,
                    },
                ],
                "description": "Time integration scheme.",
                "help": [
                    dmc.Image(src="/assets/images/solution-workflow-sketch.png"),
                ],
            },
            {
                "id": "convergence_tol",
                "label": "Convergence Tolerance",
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "convergence_tol",
                        "value": 1e-6,
                        "min": 1e-12,
                        "step": 1e-7,
                        "decimalScale": 9,
                        "required": True,
                    },
                ],
                "description": "Residual threshold for Newton–Raphson convergence.",
                "help": [html.Div("Typical values: 1e-4 (coarse) to 1e-8 (fine).")],
            },
            {
                "id": "max_iterations",
                "label": "Max Iterations",
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "max_iterations",
                        "value": 50,
                        "min": 1,
                        "max": 10000,
                        "step": 1,
                        "required": True,
                    },
                ],
                "description": "Maximum Newton–Raphson iterations per time step.",
                "help": [html.Div("Increase for strongly nonlinear problems.")],
            },
        ],
        aio_id="solver-settings",
        title="Solver Settings",
        columns=["label", "fields", "unit", "description", "help"],
        column_widths={"label": 2, "fields": 3, "unit": 1, "description": 3, "help": 1},
        title_props={"style": {"fontSize": "22px", "color": CommonColors.ORANGE}},
        card_props={"shadow": "none", "withBorder": False},
        persistence=True,
        persistence_type="memory",
    )

    front_wheels_form = InputForm(
        [
            {
                "label": "Use default values",
                "fields": [
                    {
                        "type": "Checkbox",
                        "id": "use_defaults",
                        "checked": True,
                    },
                ],
            },
            {
                "label": "Wheel diameter",
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "diameter",
                        "value": DEFAULT_WHEEL_DIAMETER,
                        "min": 0,
                        "max": 180,
                    }
                ],
                "unit": "mm",
            },
            {
                "label": "Wheel material",
                "fields": [
                    {
                        "type": "Select",
                        "value": DEFAULT_WHEEL_MATERIAL,
                        "data": ["Rubber", "Plastic", "Metal"],
                        "id": "wheel_material",
                    }
                ],
            },
        ],
        aio_id="front-wheels",
        title="Front Wheels",
        columns=["label", "fields", "unit"],
        column_widths={"label": 3, "fields": 3, "unit": 1},
        with_card=False,
    )

    rear_wheels_form = InputForm(
        [
            {
                "label": "Use default values",
                "fields": [
                    {
                        "type": "Checkbox",
                        "id": "use_defaults",
                        "checked": True,
                    },
                ],
            },
            {
                "label": "Wheel diameter",
                "fields": [
                    {
                        "type": "NumberInput",
                        "id": "diameter",
                        "value": DEFAULT_WHEEL_DIAMETER,
                        "min": 0,
                        "max": 180,
                    }
                ],
                "unit": "mm",
            },
            {
                "label": "Wheel material",
                "fields": [
                    {
                        "type": "Select",
                        "value": DEFAULT_WHEEL_MATERIAL,
                        "data": ["Rubber", "Plastic", "Metal"],
                        "id": "wheel_material",
                    }
                ],
            },
        ],
        aio_id="rear-wheels",
        title="Rear Wheels",
        columns=["label", "fields", "unit"],
        column_widths={"label": 3, "fields": 3, "unit": 1},
        with_card=False,
    )

    optional_fields_form = InputForm(
        [
            {
                "label": "Bolt Diameter",
                "fields": [
                    {
                        "type": "Select",
                        "value": "M20",
                        "data": ["M20", "M30", "M40", "M50"],
                        "id": "predefined_diameters",
                    },
                    {
                        "type": "Checkbox",
                        "id": "use_custom_bolt_diameter",
                        "checked": False,
                        "label": "Custom size",
                        "styles": {"label": {"fontSize": "12px"}},
                    },
                    {
                        "type": "NumberInput",
                        "id": "custom_diameter",
                        "value": 20,
                        "min": 5,
                        "max": 100,
                    },
                ],
                "unit": "mm",
                "description": (
                    "Use the checkbox to switch between a dropdown or a number input for the bolt"
                    " diameter."
                ),
            },
        ],
        aio_id="optional-fields",
        title="Optional Fields",
        columns=["label", "fields", "unit", "description"],
        column_widths={"label": 1, "fields": 3, "unit": 1, "description": 4},
    )

    main_content = html.Div(
        [
            html.Div(
                [
                    dmc.Text("Example 1 - Basic InputForm", fw=700, size="xl"),
                    dmc.Text(
                        "Minimal usage with the default column layout. Labels are embedded "
                        "directly in each field definition via the field's own label property.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Space(h=10),
                    html.Div(basic_form, style={"maxWidth": "500px"}),
                ],
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text(
                        "Example 2 - Simulation Job Form (All Field Types + Callbacks, values "
                        "stored on backend)",
                        fw=700,
                        size="xl",
                    ),
                    dmc.Text(
                        "Demonstrates all supported field types in a single form: TextInput, "
                        "Select, MultiSelect, NumberInput (including a row with two inputs), "
                        "Checkbox, Switch, Slider, and PasswordInput. Row IDs are named "
                        "strings.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Text(
                        "Values are stored on the backend when the 'Store Values on Backend' "
                        "button is clicked. The backend values are used to populate the form "
                        "fields, so they persist across page and project reloads. "
                        "The other buttons show three callback patterns: reading all fields "
                        "as a summary, retrieving one specific field, and reading all inputs "
                        "from a single multi-field row.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Space(h=10),
                    sim_job_form,
                    dmc.Space(h=12),
                    dmc.Button("Store Values on Backend", id="store-sim-job-btn"),
                    dmc.Space(h=12),
                    dmc.Group(
                        [
                            dmc.Button("Get Summary", id="sim-job-summary-btn"),
                            dmc.Button(
                                "Get Solver Engine",
                                id="sim-job-solver-btn",
                            ),
                            dmc.Button(
                                "Get Mesh Resolution",
                                id="sim-job-mesh-btn",
                            ),
                        ],
                    ),
                    dmc.Space(h=6),
                    html.Div(id="sim-job-summary"),
                    dmc.Space(h=6),
                    html.Div(id="sim-job-solver-output"),
                    dmc.Space(h=6),
                    html.Div(id="sim-job-mesh-output"),
                ],
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text(
                        "Example 3 - Solver Settings Form (All Columns + Custom Appearance + UI "
                        "Persistence)",
                        fw=700,
                        size="xl",
                    ),
                    dmc.Text(
                        "Uses all five columns: label, fields, unit, description, and help, "
                        "with images in the help column. The card appearance is customized "
                        "via title_props (larger blue title) and card_props (no border, no "
                        "shadow). UI persistence is enabled for this form, so entered values "
                        "persist in the browser's memory when navigating within the app. "
                        "Use the button to collect all NumberInput values at once "
                        "using the ALL wildcard.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Space(h=10),
                    solver_settings_form,
                    dmc.Space(h=10),
                    dmc.Button(
                        "Collect All Number Inputs",
                        id="solver-settings-collect-btn",
                    ),
                    html.Div(id="solver-settings-all-numbers"),
                ],
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text(
                        "Example 4 - Optional Fields with Conditional Visibility",
                        fw=700,
                        size="xl",
                    ),
                    dmc.Text(
                        "Shows how to toggle the visibility of individual fields within a row "
                        "using a checkbox. The checkbox controls whether a Select or a "
                        "NumberInput is shown for the bolt diameter.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Space(h=10),
                    optional_fields_form,
                ],
            ),
            dmc.Space(h=40),
            html.Div(
                [
                    dmc.Text(
                        "Example 5 - Composed Forms with Conditional Logic",
                        fw=700,
                        size="xl",
                    ),
                    dmc.Text(
                        "Two InputForm instances composed inside a card to create a grouped "
                        "form. Checking 'Use default values' disables the other fields and "
                        "dims their labels and units. Label and unit colors also change based "
                        "on the entered value relative to its min/max range.",
                        size="sm",
                        c=CommonColors.MANTINE_DIMMED,
                        mb="sm",
                    ),
                    dmc.Space(h=10),
                    dmc.Card(
                        [
                            front_wheels_form,
                            html.Br(),
                            rear_wheels_form,
                        ],
                        withBorder=True,
                        shadow="sm",
                        radius="md",
                        style={"maxWidth": "600px"},
                    ),
                ],
            ),
        ],
        style={"maxWidth": "900px"},
    )
    return page_layout(
        page_title="Input Form",
        info_card_text=INFO_CARD_TEXT,
        main_content=main_content,
    )


@callback(
    Input("store-sim-job-btn", "n_clicks"),
    State(InputForm.ids.field("sim-job", "TextInput", "job_name", "job_name"), "value"),
    State(InputForm.ids.field("sim-job", "Select", "solver_engine", "solver_engine"), "value"),
    State(
        InputForm.ids.field("sim-job", "MultiSelect", "output_fields", "output_fields"),
        "value",
    ),
    State(InputForm.ids.field("sim-job", "NumberInput", "mesh_x", "mesh_resolution"), "value"),
    State(InputForm.ids.field("sim-job", "NumberInput", "mesh_y", "mesh_resolution"), "value"),
    State(InputForm.ids.field("sim-job", "NumberInput", "max_runtime", "max_runtime"), "value"),
    State(
        InputForm.ids.field("sim-job", "Checkbox", "save_checkpoints", "save_checkpoints"),
        "checked",
    ),
    State(
        InputForm.ids.field("sim-job", "Switch", "email_notifications", "email_notifications"),
        "checked",
    ),
    State(InputForm.ids.field("sim-job", "Slider", "cpu_allocation", "cpu_allocation"), "value"),
    State(InputForm.ids.field("sim-job", "PasswordInput", "hpc_token", "hpc_token"), "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def store_sim_job_fields(
    n_clicks: int,
    job_name: str,
    solver: str,
    outputs: list[str],
    mesh_x: float,
    mesh_y: float,
    runtime: float,
    checkpoints: bool,
    email: bool,
    cpu: float,
    hpc_token: str,
    project: SuperComponentsExamplesSolution,
) -> None:
    """Store simulation job fields on the backend."""
    if callback_context.triggered_id is None or not n_clicks:
        raise PreventUpdate

    simple_step = project.steps.simple_step

    simple_step.sim_job_name = job_name
    simple_step.sim_job_solver = solver
    simple_step.sim_job_output_fields = outputs
    simple_step.sim_job_mesh_resolution_x = mesh_x
    simple_step.sim_job_mesh_resolution_y = mesh_y
    simple_step.sim_job_max_runtime = runtime
    simple_step.sim_job_save_checkpoints = checkpoints
    simple_step.sim_job_email_notification = email
    simple_step.sim_job_cpu_allocation = cpu
    simple_step.sim_job_hpc_token = hpc_token


@callback(
    Output("sim-job-summary", "children"),
    Trigger("sim-job-summary-btn", "n_clicks"),
    State(InputForm.ids.field("sim-job", "TextInput", "job_name", "job_name"), "value"),
    State(InputForm.ids.field("sim-job", "Select", "solver_engine", "solver_engine"), "value"),
    State(
        InputForm.ids.field("sim-job", "MultiSelect", "output_fields", "output_fields"),
        "value",
    ),
    State(InputForm.ids.field("sim-job", "NumberInput", "mesh_x", "mesh_resolution"), "value"),
    State(InputForm.ids.field("sim-job", "NumberInput", "mesh_y", "mesh_resolution"), "value"),
    State(InputForm.ids.field("sim-job", "NumberInput", "max_runtime", "max_runtime"), "value"),
    State(
        InputForm.ids.field("sim-job", "Checkbox", "save_checkpoints", "save_checkpoints"),
        "checked",
    ),
    State(
        InputForm.ids.field("sim-job", "Switch", "email_notifications", "email_notifications"),
        "checked",
    ),
    State(InputForm.ids.field("sim-job", "Slider", "cpu_allocation", "cpu_allocation"), "value"),
    prevent_initial_call=True,
)
def get_sim_job_summary(
    job_name: str,
    solver: str,
    outputs: list[str],
    mesh_x: float,
    mesh_y: float,
    runtime: float,
    checkpoints: bool,
    email: bool,
    cpu: float,
) -> str:
    """Build a full summary of all simulation job fields using specific field IDs."""
    return (
        f"Job: {job_name} | Engine: {solver} | Outputs: {outputs} | "
        f"Mesh: {mesh_x}×{mesh_y} m | Runtime: {runtime} h | "
        f"Checkpoints: {checkpoints} | Email: {email} | CPU: {cpu}%"
    )


@callback(
    Output("sim-job-solver-output", "children"),
    Trigger("sim-job-solver-btn", "n_clicks"),
    State(InputForm.ids.field("sim-job", "Select", "solver_engine", "solver_engine"), "value"),
    prevent_initial_call=True,
)
def get_solver_engine(solver: str) -> str:
    """Retrieve a single specific field value — the solver engine — by its field ID."""
    return f"Selected solver engine: {solver}"


@callback(
    Output("sim-job-mesh-output", "children"),
    Trigger("sim-job-mesh-btn", "n_clicks"),
    State(InputForm.ids.field("sim-job", "NumberInput", "mesh_x", "mesh_resolution"), "value"),
    State(InputForm.ids.field("sim-job", "NumberInput", "mesh_y", "mesh_resolution"), "value"),
    prevent_initial_call=True,
)
def get_mesh_resolution(mesh_x: float, mesh_y: float) -> str:
    """Retrieve all fields from the multi-field Mesh Resolution row by their field IDs."""
    return f"Mesh resolution — X: {mesh_x} m, Y: {mesh_y} m"


@callback(
    Output("solver-settings-all-numbers", "children"),
    Trigger("solver-settings-collect-btn", "n_clicks"),
    State(
        InputForm.ids.field("solver-settings", "NumberInput", field_id=ALL, row_index=ALL),
        "value",
    ),
    prevent_initial_call=True,
)
def collect_all_solver_number_inputs(values: list[Any]) -> str:
    """Collect all NumberInput values from the solver settings form using the ALL wildcard."""
    return f"All number inputs: {values}"


@callback(
    Output(
        InputForm.ids.field(
            aio_id=MATCH,
            field_type="NumberInput",
            field_id="diameter",
            row_index=ALL,
        ),
        "disabled",
    ),
    Output(
        InputForm.ids.field(
            aio_id=MATCH,
            field_type="NumberInput",
            field_id="diameter",
            row_index=ALL,
        ),
        "value",
    ),
    Output(
        InputForm.ids.field(
            aio_id=MATCH,
            field_type="Select",
            field_id="wheel_material",
            row_index=ALL,
        ),
        "disabled",
    ),
    Output(
        InputForm.ids.field(
            aio_id=MATCH,
            field_type="Select",
            field_id="wheel_material",
            row_index=ALL,
        ),
        "value",
    ),
    Input(
        InputForm.ids.field(
            aio_id=MATCH,
            field_type="Checkbox",
            field_id="use_defaults",
            row_index=ALL,
        ),
        "checked",
    ),
)
def enable_disable_wheel_parameters(
    use_defaults: list[bool],
) -> tuple[list[bool], list[float | NoUpdate], list[bool], list[str | NoUpdate]]:
    """Disable/enable wheel parameters and reset their values when 'use_defaults' is toggled."""
    disabled = bool(use_defaults[0])  # Assuming only one checkbox per form
    return (
        [disabled],
        [DEFAULT_WHEEL_DIAMETER if disabled else no_update],
        [disabled],
        [DEFAULT_WHEEL_MATERIAL if disabled else no_update],
    )


@callback(
    Output(InputForm.ids.label(aio_id=MATCH, row_index=MATCH), "c", allow_duplicate=True),
    Output(InputForm.ids.unit(aio_id=MATCH, row_index=MATCH), "c", allow_duplicate=True),
    Input(
        InputForm.ids.field(
            aio_id=MATCH, field_type="Select", field_id="wheel_material", row_index=MATCH
        ),
        "disabled",
    ),
)
def grey_out_wheel_material_row_when_parameter_is_disabled(is_disabled: bool) -> tuple[str, str]:
    """Set label and unit color to dimmed when parameters are disabled."""
    if is_disabled:
        return CommonColors.MANTINE_DIMMED, CommonColors.MANTINE_DIMMED
    else:
        return CommonColors.MANTINE_TEXT, CommonColors.MANTINE_TEXT


@callback(
    Output(InputForm.ids.label(aio_id=MATCH, row_index=MATCH), "c", allow_duplicate=True),
    Output(InputForm.ids.unit(aio_id=MATCH, row_index=MATCH), "c", allow_duplicate=True),
    Input(
        InputForm.ids.field(
            aio_id=MATCH, field_type="NumberInput", field_id="diameter", row_index=MATCH
        ),
        "value",
    ),
    Input(
        InputForm.ids.field(
            aio_id=MATCH, field_type="NumberInput", field_id="diameter", row_index=MATCH
        ),
        "min",
    ),
    Input(
        InputForm.ids.field(
            aio_id=MATCH, field_type="NumberInput", field_id="diameter", row_index=MATCH
        ),
        "max",
    ),
    Input(
        InputForm.ids.field(
            aio_id=MATCH, field_type="NumberInput", field_id="diameter", row_index=MATCH
        ),
        "disabled",
    ),
)
def adjust_diameter_row_color_depending_on_value(
    value: float,
    min_value: float,
    max_value: float,
    is_disabled: bool,
) -> tuple[str, str]:
    """Adjust label and unit color based on diameter value relative to min/max."""
    value_range = max_value - min_value
    if is_disabled:
        return CommonColors.MANTINE_DIMMED, CommonColors.MANTINE_DIMMED
    elif value < min_value + 0.2 * value_range or value > min_value + 0.8 * value_range:
        return CommonColors.ORANGE, CommonColors.ORANGE
    else:
        return CommonColors.GREEN, CommonColors.GREEN


@callback(
    Output(
        InputForm.ids.field("optional-fields", "NumberInput", "custom_diameter", row_index=MATCH),
        "style",
    ),
    Output(
        InputForm.ids.field("optional-fields", "Select", "predefined_diameters", row_index=MATCH),
        "style",
    ),
    Output(
        InputForm.ids.unit("optional-fields", row_index=MATCH),
        "c",
    ),
    Input(
        InputForm.ids.field(
            "optional-fields", "Checkbox", "use_custom_bolt_diameter", row_index=MATCH
        ),
        "checked",
    ),
    State(
        InputForm.ids.field("optional-fields", "NumberInput", "custom_diameter", row_index=MATCH),
        "style",
    ),
    State(
        InputForm.ids.field("optional-fields", "Select", "predefined_diameters", row_index=MATCH),
        "style",
    ),
)
def toggle_parameter_visibility_in_single_row(
    use_custom_size: bool,
    style_custom_diameter: dict[str, Any],
    style_predefined_diameters: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], str]:
    """Toggle between number input and select visibility based on checkbox state."""
    if use_custom_size:
        style_custom_diameter["display"] = "block"
        style_predefined_diameters["display"] = "none"
        color_unit = CommonColors.MANTINE_TEXT
    else:
        style_custom_diameter["display"] = "none"
        style_predefined_diameters["display"] = "block"
        color_unit = CommonColors.MANTINE_DIMMED
    return style_custom_diameter, style_predefined_diameters, color_unit
