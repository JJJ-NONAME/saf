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

"""Check that installation creates and launches the desktop shortcut."""

import platform

import pytest

from tests.e2e.conftest import EXAMPLES_ROOT, InstalledDesktopExamples, LaunchedExamples

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CUSTOM_SPLASH_IMAGE = (
    EXAMPLES_ROOT / "src" / "saf" / "solutions" / "examples" / "ui" / "assets" / "orchestrator" / "splash.png"
)
CUSTOM_SPLASH_IMAGE_SUFFIX = "saf/solutions/examples/ui/assets/orchestrator/splash.png"
DEFAULT_SPLASH_IMAGE = (
    EXAMPLES_ROOT.parent
    / "packages"
    / "saf-desktop-orchestrator"
    / "src"
    / "ansys"
    / "saf"
    / "desktop"
    / "orchestrator"
    / "_assets"
    / "splash.png"
)
DEFAULT_SPLASH_IMAGE_SUFFIX = "ansys/saf/desktop/orchestrator/_assets/splash.png"


def test_desktop_shortcut_is_created(
    installed_desktop_examples: InstalledDesktopExamples,
) -> None:
    """Verify installation creates the expected platform-specific shortcut.

    The shortcut is created on the isolated desktop and is the entry point used
    to launch the installed solution.
    """
    assert (
        installed_desktop_examples.shortcut.is_file()
    ), f"Expected desktop shortcut was not created: {installed_desktop_examples.shortcut}"


@pytest.mark.skipif(
    platform.system() == "Linux",
    reason="The SAF desktop orchestrator does not display a splash screen on Linux.",
)
def test_shortcut_launches_solution_and_validates_splash_image(
    launched_examples: LaunchedExamples,
) -> None:
    """Verify the shortcut launches the solution and selects its splash image.

    The fixture has already launched the shortcut and waited for the
    orchestrator's splash image signal. The selected image must be the expected
    PNG.
    """
    assert launched_examples.process.process is not None, "The desktop shortcut did not start a process."

    splash_image_path = launched_examples.splash_image_path
    assert splash_image_path is not None, "The orchestrator did not report a splash image."
    assert splash_image_path.is_file(), f"The selected splash image does not exist: {splash_image_path}"

    image_bytes = splash_image_path.read_bytes()
    assert image_bytes.startswith(PNG_SIGNATURE), f"The selected splash image is not a PNG file: {splash_image_path}"

    normalized_path = splash_image_path.as_posix().lower()
    if CUSTOM_SPLASH_IMAGE.is_file():
        assert normalized_path.endswith(CUSTOM_SPLASH_IMAGE_SUFFIX), (
            "The orchestrator did not select the solution's custom splash image: " f"{splash_image_path}"
        )
        assert image_bytes == CUSTOM_SPLASH_IMAGE.read_bytes(), (
            "The splash image packaged with the installed solution differs from " f"{CUSTOM_SPLASH_IMAGE}."
        )
    else:
        assert normalized_path.endswith(DEFAULT_SPLASH_IMAGE_SUFFIX), (
            "The orchestrator did not select its expected default splash image: " f"{splash_image_path}"
        )
        if DEFAULT_SPLASH_IMAGE.is_file():
            assert image_bytes == DEFAULT_SPLASH_IMAGE.read_bytes(), (
                "The packaged default splash image differs from the repository's "
                f"expected image: {DEFAULT_SPLASH_IMAGE}."
            )
