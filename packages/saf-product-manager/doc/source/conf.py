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

"""Sphinx documentation configuration file."""

from datetime import datetime
import os
from pathlib import Path
import shutil
import subprocess
import sys

from ansys_sphinx_theme import (  # pyright: ignore[reportMissingTypeStubs]
    ansys_favicon,
    ansys_logo_dark_mode,
    ansys_logo_light_mode,
    get_version_match,
)
from sphinx.builders.latex import LaTeXBuilder

# Add source to path to import package version
sys.path.insert(0, str(Path(__file__).parent.parent.parent.absolute() / "src"))
from ansys.saf.product_manager import __version__

THIS_PATH = Path(__file__).parent.resolve()

# ============================================================================
# Project information
# ============================================================================

project = "ansys-saf-product-manager"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"  # noqa: A001
author = "ANSYS, Inc."
release = version = __version__
cname = os.getenv("CNAME")
switcher_version = get_version_match(__version__)

# ============================================================================
# General Sphinx configuration
# ============================================================================

source_suffix = ".rst"
master_doc = "index"

# AutoAPI fails to resolve many imports despite them being present in the environment
# AutoAPI fails to generate files for classes that are exposed manually in the __init__.py file of the package.
suppress_warnings = ["autoapi.python_import_resolution", "toc.not_readable"]

# ============================================================================
# Extensions
# ============================================================================

extensions = [
    "ansys_sphinx_theme.extension.autoapi",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
]

# ============================================================================
# Intersphinx
# ============================================================================

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

# ============================================================================
# LaTeX configuration
# ============================================================================

LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml"]

# ============================================================================
# Link check
# ============================================================================

linkcheck_ignore = [
    r"https://sphinxdocs.ansys.com/version/*",
]
if switcher_version != "dev":
    linkcheck_ignore.append(
        f"https://github.com/ansys/saf-product-manager/releases/tag/v{__version__}",
    )

# ============================================================================
# HTML output
# ============================================================================

html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "SAF Product Manager for Python"
html_favicon = ansys_favicon
templates_path = ["_templates"]
html_show_sourcelink = False
html_compact_lists = False

html_context = {
    "github_user": "ansys",
    "github_repo": "saf-product-manager",
    "github_version": "main",
    "doc_path": "doc/source",
}

html_theme_options = {
    "github_url": "https://github.com/ansys/saf-product-manager",
    "contact_mail": "solution-applications.maintainers@ansys.com",
    "use_edit_page_button": False,
    "logo": {
        "image_light": ansys_logo_light_mode,
        "image_dark": ansys_logo_dark_mode,
    },
    "search_filters": {
        "User guide": [
            "user-guide/",
            "getting-started/",
            "index/",
        ],
        "Release notes": ["changelog"],
        "Examples": ["examples/"],
        "Contributing": ["contribute/"],
    },
    "show_breadcrumbs": True,
    "show_prev_next": False,
    "additional_breadcrumbs": [
        ("SAF", f"https://{cname}/version/stable/api/index.html"),
    ],
    "ansys_sphinx_theme_autoapi": {
        "project": project,
        "output": ".",
        "add_toctree_entry": False,
        "options": [
            "members",
            "undoc-members",
            "show-inheritance",
            "show-module-summary",
            "special-members",
            "imported-members",
        ],
    },
    "check_switcher": False,
}

html_theme_options["switcher"] = {
    "json_url": f"https://{cname}/version/stable/api/saf-product-manager/versions.json",
    "version_match": switcher_version,
}

# ============================================================================
# Jinja configuration
# ============================================================================

jinja_globals = {"version": version}

tox_command = shutil.which("tox")
tox_envs = []
if tox_command:
    tox_envs = subprocess.run(
        [tox_command, "list", "-d", "-q"],
        capture_output=True,
        text=True,
    ).stdout.splitlines()[1:]

jinja_contexts = {
    "toxenvs": {
        "envs": tox_envs,
    },
}

# ============================================================================
# Sphinx event hooks
# ============================================================================


def _rename_api_title(app, docname, source):
    """Replace the default autoapi module title with 'API reference'."""
    if docname == "ansys/saf/product_manager/index":
        old_title = "The ``ansys.saf.product_manager`` library"
        old_underline = "=" * len(old_title)
        new_title = "API reference"
        new_underline = "=" * len(new_title)
        source[0] = source[0].replace(
            f"{old_title}\n{old_underline}",
            f"{new_title}\n{new_underline}",
            1,
        )


def setup(app):
    """Connect Sphinx events."""
    app.connect("source-read", _rename_api_title)
