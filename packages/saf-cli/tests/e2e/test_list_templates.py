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

import pytest

from tests.conftest import get_template_path, get_template_plugin_path
from tests.e2e.conftest import ListTemplates


@pytest.mark.use_custom_plugins
class TestListTemplates:
    """
    Test class for ``saf templates`` command, testing that it lists the available templates from the default and custom
    plugin both in verbose and non-verbose mode, and outputs any errors related to loading plugins and templates.
    """

    @pytest.mark.usefixtures(
        "install_custom_template_plugin",
        "install_custom_template_plugin_empty_toml",
        "install_custom_template_plugin_no_toml",
        "install_custom_template_plugin_same_name_step",
        "install_custom_template_plugin_invalid_template",
        "install_custom_template_plugin_with_glow_and_ui_deps",
    )
    @pytest.mark.parametrize("verbose", [True, False], ids=["verbose", "not_verbose"])
    def test_saf_templates(self, list_templates: ListTemplates, verbose: bool):
        output = "\n".join(list_templates(args=["--verbose"] if verbose else []))
        if verbose:
            expected_output = [
                "Templates in ansys.saf.templates\n"
                "    calculator-step (step): a step that performs calculator operations\n"
                f"        location: {get_template_path('templates', 'calculator')}\n\n",
                "Templates in ansys.saf.test_custom_templates\n"
                "    several-deps-step (step): a step that performs custom calculator operations\n"
                f"        location: {get_template_path('test_custom_templates', 'several_deps_step')}\n"
                "        main dependencies:\n"
                "          - humanize: ^4.15.0\n"
                "          - msgpack: {'version': '^1.0.0', 'allow-prereleases': True}\n\n"
                "    second-step (step): a step that is second to another step\n"
                f"        location: {get_template_path('test_custom_templates', 'second_step')}\n\n",
                "Templates in ansys.saf.test_custom_templates_with_glow_and_ui_deps\n"
                "    several-deps-step (step): a step that performs custom calculator operations\n"
                "        location: "
                f"{get_template_path('test_custom_templates_with_glow_and_ui_deps', 'several_deps_step')}\n"
                "        main dependencies:\n"
                "          - humanize: ^4.15.0\n"
                "          - msgpack: {'version': '^1.0.0', 'allow-prereleases': True}\n\n"
                "    second-step (step): a step that is second to another step\n"
                f"        location: {get_template_path('test_custom_templates_with_glow_and_ui_deps', 'second_step')}\n"
                "        main dependencies:\n"
                "          - ansys-saf-sdk: {'version': '^0.1.0', 'allow-prereleases': True, "
                "'extras': ['core-hps']}\n"
                "        ui dependencies:\n"
                "          - streamlit: ^1.58.0\n",
            ]
        else:
            expected_output = [
                "Templates in ansys.saf.templates\n"
                "    calculator-step (step): a step that performs calculator operations\n\n",
                "Templates in ansys.saf.test_custom_templates\n"
                "    several-deps-step (step): a step that performs custom calculator operations\n\n"
                "    second-step (step): a step that is second to another step\n\n",
                "Warning: 3 template plugin(s) could not be loaded. Use --verbose flag for more details.\n"
                "Warning: 2 template(s) could not be loaded. Use --verbose flag for more details.",
                "Templates in ansys.saf.test_custom_templates_with_glow_and_ui_deps\n"
                "    several-deps-step (step): a step that performs custom calculator operations\n\n"
                "    second-step (step): a step that is second to another step\n\n",
            ]
        assert all(block in output for block in expected_output)

        if verbose:
            assert "Error in plugin module 'ansys.saf.test_custom_templates_empty_toml':" in output
            assert "Error in plugin module 'ansys.saf.test_custom_templates_no_toml':" in output
            assert "Error in plugin module 'ansys.saf.test_custom_templates_same_name_step':" in output
            assert "Error in template 'several-deps-step':" in output
            assert "Error in template 'second-step':" in output
            assert (
                "No templates in templates configuration file for plugin module "
                "'ansys.saf.test_custom_templates_empty_toml'"
            ) in output
            assert (
                f"Config file 'templates.toml' not found for plugin module 'ansys.saf.test_custom_templates_no_toml' "
                f"at expected location {get_template_plugin_path('test_custom_templates_no_toml') / 'templates.toml'}"
            ) in output
            assert (
                f"Error loading config file 'templates.toml' for plugin module "
                f"'ansys.saf.test_custom_templates_same_name_step' at location "
                f"{get_template_plugin_path('test_custom_templates_same_name_step') / 'templates.toml'}: "
                f'Key "several-deps-step" already exists'
            ) in output

    @pytest.mark.usefixtures(
        "install_custom_template_plugin",
        "install_custom_template_plugin_with_glow_and_ui_deps",
    )
    @pytest.mark.parametrize("verbose", [True, False], ids=["verbose", "not_verbose"])
    def test_saf_templates_with_steps_flag(self, list_templates: ListTemplates, verbose: bool):
        args = ["--steps"] + (["--verbose"] if verbose else [])
        output = "\n".join(list_templates(args=args))
        if verbose:
            expected_output = [
                "Step templates in ansys.saf.templates\n"
                "    calculator-step (step): a step that performs calculator operations\n"
                f"        location: {get_template_path('templates', 'calculator')}\n\n",
                "Step templates in ansys.saf.test_custom_templates\n"
                "    several-deps-step (step): a step that performs custom calculator operations\n"
                f"        location: {get_template_path('test_custom_templates', 'several_deps_step')}\n"
                "        main dependencies:\n"
                "          - humanize: ^4.15.0\n"
                "          - msgpack: {'version': '^1.0.0', 'allow-prereleases': True}\n\n"
                "    second-step (step): a step that is second to another step\n"
                f"        location: {get_template_path('test_custom_templates', 'second_step')}\n",
                "Step templates in ansys.saf.test_custom_templates_with_glow_and_ui_deps\n"
                "    several-deps-step (step): a step that performs custom calculator operations\n"
                "        location: "
                f"{get_template_path('test_custom_templates_with_glow_and_ui_deps', 'several_deps_step')}\n"
                "        main dependencies:\n"
                "          - humanize: ^4.15.0\n"
                "          - msgpack: {'version': '^1.0.0', 'allow-prereleases': True}\n\n"
                "    second-step (step): a step that is second to another step\n"
                f"        location: {get_template_path('test_custom_templates_with_glow_and_ui_deps', 'second_step')}\n"
                "        main dependencies:\n"
                "          - ansys-saf-sdk: {'version': '^0.1.0', 'allow-prereleases': True, "
                "'extras': ['core-hps']}\n"
                "        ui dependencies:\n"
                "          - streamlit: ^1.58.0\n",
            ]
        else:
            expected_output = [
                "Step templates in ansys.saf.templates\n"
                "    calculator-step (step): a step that performs calculator operations\n\n",
                "Step templates in ansys.saf.test_custom_templates\n"
                "    several-deps-step (step): a step that performs custom calculator operations\n\n"
                "    second-step (step): a step that is second to another step\n\n",
                "Step templates in ansys.saf.test_custom_templates_with_glow_and_ui_deps\n"
                "    several-deps-step (step): a step that performs custom calculator operations\n\n"
                "    second-step (step): a step that is second to another step\n",
            ]
        assert all(block in output for block in expected_output)

    @pytest.mark.usefixtures("install_custom_template_plugin")
    @pytest.mark.parametrize("verbose", [True, False], ids=["verbose", "not_verbose"])
    def test_saf_templates_with_solutions_flag(self, list_templates: ListTemplates, verbose: bool):
        args = ["--solutions"] + (["--verbose"] if verbose else [])
        output = "\n".join(list_templates(args=args))
        expected_output = (
            "Solution templates in ansys.saf.templates\nSolution templates in ansys.saf.test_custom_templates"
        )
        assert expected_output in output
