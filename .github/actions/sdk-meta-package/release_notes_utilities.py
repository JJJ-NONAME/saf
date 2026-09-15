# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from constants import (
    INITIAL_META_PACKAGE_VERSION,
    META_PACKAGE_NAME,
    PACKAGE_LIBRARY_DIRS,
    REPO_ROOT,
)
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import requests
from packaging.version import Version

RELEASE_NOTES_FILE = REPO_ROOT / "release_notes.md"
GITHUB_RELEASE_URL = "https://api.github.com/repos/ansys/saf/releases/tags/{tag}"
MAINTENANCE_WINDOW_DAYS = 180
PACKAGES = list(PACKAGE_LIBRARY_DIRS)


def get_maintenance_window(name: str, version: str) -> str:
    """Return the maintenance-window date for a package release.

    The maintenance window starts 180 days after the ``X.Y.0`` release on
    PyPI, where ``X.Y`` is taken from ``version``.

    Parameters
    ----------
    name : str
        PyPI package name.
    version : str
        Package version whose major and minor components identify the base
        release.

    Returns
    -------
    str
        Maintenance-window date in ``YYYY-MM-DD`` format.

    Raises
    ------
    ValueError
        If the corresponding ``X.Y.0`` release is not listed on PyPI.
    requests.HTTPError
        If the PyPI request fails.
    """
    pypi_json_url = "https://pypi.org/pypi/{name}/json"
    response = requests.get(pypi_json_url.format(name=name), timeout=10)
    response.raise_for_status()
    releases = response.json()["releases"]
    parsed_version = Version(version)
    release_version = f"{parsed_version.major}.{parsed_version.minor}.0"
    if release_version not in releases or not releases[release_version]:
        raise ValueError(
            f"Release {release_version} (derived from {version}) not found for package: {name}"
        )
    upload_time = releases[release_version][0]["upload_time"]
    maintenance_window = datetime.fromisoformat(upload_time) + timedelta(
        days=MAINTENANCE_WINDOW_DAYS
    )
    return maintenance_window.strftime("%Y-%m-%d")


def get_release_notes(package: str, version: str) -> str | None:
    """Return GitHub release notes for a package version.

    The release is looked up using the tag ``v{version}-{library-dir}``. HTML
    comments are removed, and when present, only the content after the
    ``What's changed`` heading is returned.

    Parameters
    ----------
    package : str
        Package name used to determine its repository library directory.
    version : str
        Package release version.

    Returns
    -------
    str or None
        Cleaned release-note content, or ``None`` when the release is missing
        or has an empty body.

    Raises
    ------
    requests.HTTPError
        If GitHub returns an unsuccessful response other than ``404``.
    """
    tag = f"v{version}-{PACKAGE_LIBRARY_DIRS[package]}"
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        GITHUB_RELEASE_URL.format(tag=tag), headers=headers, timeout=10
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    body = response.json()["body"]
    if not body:
        return None

    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()
    match = re.search(
        r"^#{1,6}\s*what's changed\s*$", body, flags=re.IGNORECASE | re.MULTILINE
    )
    notes = body[match.end() :].lstrip("\n").strip() if match else body
    return notes or None


def generate_release_notes(
    versions: dict[str, str],
    meta_package_version: str,
    current_versions: dict[str, str],
) -> None:
    """Write dependency versions and package release notes to Markdown files.

    Parameters
    ----------
    versions : dict[str, str]
        Resolved package versions to include in the report.
    meta_package_version : str
        Version of the generated meta-package.
    current_versions : dict[str, str]
        Versions currently declared by the meta-package, used to identify
        packages without changes.

    Notes
    -----
    The report is written to ``RELEASE_NOTES_FILE`` and, when configured, to
    the GitHub Actions step summary identified by ``GITHUB_STEP_SUMMARY``.
    """
    print(f"Generating package versions summary in {RELEASE_NOTES_FILE}...")

    rows = [
        f"| `{package}` | `{versions[package]}` | `{get_maintenance_window(package, versions[package])}` |"
        for package in PACKAGES
    ]

    minimum_pip_version = os.environ["MINIMUM_PIP_VERSION"]

    content = "\n".join(
        [
            "<!-- DO NOT EDIT BELOW THIS LINE; THIS SECTION OF THE FILE IS AUTO-GENERATED -->",
            f"# {META_PACKAGE_NAME} {meta_package_version}",
            f"**Note:** Installing `{META_PACKAGE_NAME}` requires **pip {minimum_pip_version}** or higher.",
            "## Dependency Versions",
            "",
            f"The following versions were resolved when this version of the {META_PACKAGE_NAME} was generated.",
            "",
            "| Package | Version | Maintenance Window |",
            "| --- | --- | --- |",
            *rows,
            "---",
        ]
    )

    for package in PACKAGES:
        if (
            versions[package] == current_versions[package]
            and meta_package_version != INITIAL_META_PACKAGE_VERSION
        ):
            package_notes = "No changes"
        else:
            package_notes = get_release_notes(package, versions[package])

        if package_notes:
            content += "\n\n" + "\n".join(
                [
                    f"# {package} {versions[package]}",
                    "",
                    package_notes,
                    "",
                ]
            )

    RELEASE_NOTES_FILE.write_text(content, encoding="utf-8")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("w", encoding="utf-8") as summary_file:
            summary_file.write(content)

    print(f"Package versions summary written to {RELEASE_NOTES_FILE}.")
