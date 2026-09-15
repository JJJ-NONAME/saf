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

# Configuration file for the Sphinx documentation builder.
#


"""Sphinx documentation configuration file."""

from datetime import datetime
import os
from pathlib import Path
import sys

from ansys_sphinx_theme import (
    ansys_favicon,
    ansys_logo_dark_mode,
    ansys_logo_light_mode,
    get_version_match,
)
import toml

# Add local Sphinx extensions directory to the Python path.
sys.path.insert(0, str(Path(__file__).parent / "_ext"))

# Get version from pyproject.toml
package_configuration = toml.load(Path(__file__).parent.parent.parent.absolute() / "pyproject.toml")
version = package_configuration["project"]["version"]

# Project information
project = "Super Components for Dash"
start_year = "2025"
copyright_year = (
    f"{start_year}"
    if start_year == str(datetime.today().year)
    else f"{start_year}-{datetime.today().year}"
)
ansys_copyright = f"(c) {copyright_year} ANSYS, Inc. and/or its affiliates"
author = "ANSYS, Inc."
cname = os.getenv("CNAME")

html_favicon = ansys_favicon
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = project  # necessary for proper breadcrumb title
html_context = {
    "github_user": "ansys",
    "github_repo": "super-components-for-dash",
    "github_version": "main",
    "doc_path": "doc/source",
    "version": version,
}

# Omit the generation of genindex.html
html_use_index = False

html_theme_options = {
    "logo": {
        "image_dark": ansys_logo_dark_mode,
        "image_light": ansys_logo_light_mode,
    },
    # "logo_link": "https://docs.pyansys.com",
    "github_url": "https://github.com/ansys/super-components-for-dash",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": False,
    "header_links_before_dropdown": 7,
    "switcher": {
        "json_url": f"https://{cname}/version/stable/api/dash-super-components/versions.json",
        "version_match": get_version_match(version),
    },
    "static_search": {
        "threshold": 0.5,
        "limit": 10,
        "minMatchCharLength": 2,
        "ignoreLocation": True,
    },
    "check_switcher": False,
}

# Sphinx extensions
extensions = [
    "sphinx_copybutton",
    "sphinx_code_tabs",
    "sphinx_design",
    "sphinxcontrib.video",
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "super_components_icons_table",
    "sphinx_gallery.gen_gallery",
]

# sphinx-gallery configuration
# ``plot_gallery=False`` prevents sphinx-gallery from executing the example
# scripts during the doc build (Dash apps cannot run headlessly).
# The extension still parses the ``# %%`` text blocks and generates the
# gallery pages, download buttons and cross-reference targets.
sphinx_gallery_conf = {
    # path to your examples scripts
    "examples_dirs": ["../../examples/gallery_apps"],
    # path where to save gallery generated examples
    "gallery_dirs": ["examples"],
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Sort gallery example by file name instead of number of lines (default)
    "within_subsection_order": "FileNameSortKey",
    "image_scrapers": (),
    "remove_config_comments": True,
}

# Autosummary configuration
autosummary_generate = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    # kept here as an example
    # "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # "numpy": ("https://numpy.org/devdocs", None),
    # "matplotlib": ("https://matplotlib.org/stable", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    # "pyvista": ("https://docs.pyvista.org/", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True
# Override numpydoc's default link for ``bool`` (which would point to the
# ``python:bltin-boolean-values`` intersphinx label) with a direct Python
# class reference so that the docs build cleanly even when the Python
# intersphinx inventory cannot be reached. This is necessary for copilot
# agents that attempt to build the docs in an environment without network access
# or access restrictions through firewall rules etc.
numpydoc_xref_aliases = {
    "bool": ":py:class:`bool`",
    "boolean": ":py:class:`bool`",
}
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    "SS03",  # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    "SS05",  # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# static path
html_static_path = ["_static"]

# css files
html_css_files = [
    "svg_icons.css",
]
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# Generate section labels up to four levels deep
autosectionlabel_maxdepth = 4

exclude_patterns = ["links_and_refs.rst"]

suppress_warnings = ["toc.excluded"]
