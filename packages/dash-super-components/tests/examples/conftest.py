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

"""Fixtures and helpers shared across the gallery example tests."""

import importlib.util
from pathlib import Path
import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Locate runnable single-file example apps.
#
# Included directories:
#   - examples/gallery_apps/**  (all sub-folders, recursive)
#   - examples/user_guide/      (top-level files only, NOT sub-folders)
#
# Excluded directories:
#   - examples/showcase_all/                    (multi-file SAF solution)
#   - examples/user_guide/super_components_with_saf/  (multi-file SAF solution)
# ---------------------------------------------------------------------------

EXAMPLES_ROOT = Path(__file__).parent.parent.parent / "examples"

_EXAMPLE_FILES: list[Path] = sorted(
    [
        # examples/gallery_apps/ — all sub-folders, recursive
        *(EXAMPLES_ROOT / "gallery_apps").rglob("example_*.py"),
        # examples/user_guide/ — top-level files only (no sub-folders)
        *(EXAMPLES_ROOT / "user_guide").glob("example_*.py"),
    ]
)


def _module_name_for(path: Path) -> str:
    """Return a unique, importable module name derived from *path*.

    The name is built from the path relative to *EXAMPLES_ROOT*, with path
    separators replaced by dots and the ``.py`` suffix stripped, so that
    each file gets an unambiguous name even when different sub-folders
    contain files with the same stem (e.g. ``gallery_apps/general/example_tree.py``
    and ``user_guide/example_tree.py`` produce distinct keys).

    Hyphens in directory or file names are replaced with underscores to keep
    the resulting string a valid Python identifier.
    """
    relative = path.relative_to(EXAMPLES_ROOT)
    parts = list(relative.parent.parts) + [relative.stem]
    return "examples." + ".".join(p.replace("-", "_") for p in parts)


def load_example_module(path: Path) -> types.ModuleType:
    """Import and return the module at *path*.

    Why this complexity is required
    --------------------------------
    The example files live outside the installed package tree and are not on
    ``sys.path``, so a plain ``import`` statement cannot find them.
    ``importlib.util.spec_from_file_location`` is the standard library
    mechanism for loading an arbitrary file by its absolute path.  A synthetic
    but unique module name (built by ``_module_name_for``) is required so that
    two files with the same stem in different sub-folders are kept as separate
    entries in ``sys.modules`` and do not overwrite each other.

    Caching and shared state
    ------------------------
    Each call reuses a previously imported module (cached in ``sys.modules``).
    The module is inserted into ``sys.modules`` *before* ``exec_module`` is
    called so that any circular imports within the example resolve correctly.

    Important: tests must **not** mutate module-level state (e.g.
    ``module.app.layout = ...``).  Because all parametrized test functions for
    the same ``example_path`` share the same cached module object, a mutation
    made by one test will be visible to every subsequent test in the session,
    causing hard-to-diagnose order-dependent failures.
    """
    module_name = _module_name_for(path)
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise ImportError(f"Cannot load spec for {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Pytest parametrize fixtures / ids
# ---------------------------------------------------------------------------


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrize any test that requests the ``example_path`` fixture.

    This hook auto-discovers every ``example_*.py`` file in:

    - ``examples/gallery_apps/`` (all sub-folders, recursive), and
    - ``examples/user_guide/`` (top-level files only, sub-folders excluded)

    so that no manual updates are required when new single-file examples are
    added.  Multi-file SAF-based solutions (``showcase_all/``,
    ``user_guide/super_components_with_saf/``) are intentionally excluded.
    """
    if "example_path" in metafunc.fixturenames:
        ids = [_module_name_for(p) for p in _EXAMPLE_FILES]
        metafunc.parametrize("example_path", _EXAMPLE_FILES, ids=ids)
