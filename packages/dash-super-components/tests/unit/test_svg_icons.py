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

"""Unit tests for SVG icons module."""

import base64

from dash_extensions.enrich import html
import pytest

from ansys.solutions.dash_super_components.utils.svg_icons import (
    IconNames,
    create_base64_svg_src,
    create_icon_span,
    create_image_icon_span,
    get_svg_icon,
)


@pytest.mark.parametrize("icon_name", list(IconNames))
def test_get_svg_icon_returns_string(icon_name: IconNames):
    """Test that get_svg_icon returns a string."""
    result = get_svg_icon(icon_name)
    assert isinstance(result, str)


@pytest.mark.parametrize("icon_name", list(IconNames))
def test_get_svg_icon_default_color(icon_name: IconNames):
    """Test that get_svg_icon uses default black color."""
    result = get_svg_icon(icon_name)
    assert "#000" in result or 'fill="#000"' in result or 'stroke="#000"' in result


@pytest.mark.parametrize("icon_name", list(IconNames))
def test_get_svg_icon_custom_color(icon_name: IconNames):
    """Test that get_svg_icon applies custom color."""
    custom_color = "#FF5733"
    result = get_svg_icon(icon_name, color=custom_color)
    assert custom_color in result


@pytest.mark.parametrize("icon_name", list(IconNames))
def test_get_svg_icon_contains_svg_tag(icon_name: IconNames):
    """Test that returned string contains SVG tag."""
    result = get_svg_icon(icon_name)
    assert "<svg" in result
    assert "</svg>" in result


@pytest.mark.parametrize("icon_name", list(IconNames))
def test_get_svg_icon_contains_xmlns(icon_name: IconNames):
    """Test that SVG contains xmlns attribute."""
    result = get_svg_icon(icon_name)
    assert 'xmlns="http://www.w3.org/2000/svg"' in result


@pytest.mark.parametrize("icon_name", list(IconNames))
def test_get_svg_icon_contains_viewbox(icon_name: IconNames):
    """Test that SVG contains viewBox attribute."""
    result = get_svg_icon(icon_name)
    assert "viewBox=" in result


def test_get_svg_icon_color_hex_format():
    """Test various color formats are applied correctly."""
    test_colors = ["#FF0000", "#00FF00", "#0000FF", "#ABC", "#123456"]
    for color in test_colors:
        result = get_svg_icon(IconNames.MATERIAL_INFO, color=color)
        assert color in result


def test_get_svg_icon_multiple_colors():
    """Test that different colors produce different outputs."""
    red_svg = get_svg_icon(IconNames.MATERIAL_ERROR, color="#FF0000")
    blue_svg = get_svg_icon(IconNames.MATERIAL_ERROR, color="#0000FF")
    assert red_svg != blue_svg
    assert "#FF0000" in red_svg
    assert "#0000FF" in blue_svg


def test_get_svg_icon_rgb_color():
    """Test that RGB color format is applied."""
    rgb_color = "rgb(255, 0, 0)"
    result = get_svg_icon(IconNames.MATERIAL_LIST, color=rgb_color)
    assert rgb_color in result


def test_get_svg_icon_named_color():
    """Test that named colors are applied."""
    result = get_svg_icon(IconNames.MATERIAL_HELP, color="red")
    assert "red" in result


def test_get_svg_icon_consistent_output():
    """Test that calling with same parameters produces same output."""
    result1 = get_svg_icon(IconNames.MDI_ROCKET, color="#123456")
    result2 = get_svg_icon(IconNames.MDI_ROCKET, color="#123456")
    assert result1 == result2


@pytest.mark.parametrize("icon_name", list(IconNames))
def test_get_svg_icon_path_element(icon_name: IconNames):
    """Test that SVG contains path or other shape elements."""
    result = get_svg_icon(icon_name)
    # Should contain at least one shape element
    assert any(tag in result for tag in ["<path", "<circle", "<rect", "<polygon", "<g"])


def test_get_svg_icon_empty_color_string():
    """Test behavior with empty color string."""
    result = get_svg_icon(IconNames.MDI_USER, color="")
    assert isinstance(result, str)
    assert "fill=" in result or "stroke=" in result


@pytest.mark.parametrize("icon_name", list(IconNames))
def test_create_base64_svg_src_returns_string(icon_name: IconNames):
    """Test that create_base64_svg_src returns a string."""
    result = create_base64_svg_src(icon_name)
    assert isinstance(result, str)


@pytest.mark.parametrize("icon_name", list(IconNames))
def test_create_base64_svg_src_format(icon_name: IconNames):
    """Test that result has correct data URI format."""
    result = create_base64_svg_src(icon_name)
    assert result.startswith("data:image/svg+xml;base64,")


@pytest.mark.parametrize("icon_name", list(IconNames))
def test_create_base64_svg_src_is_base64(icon_name: IconNames):
    """Test that the encoded part is valid base64."""
    result = create_base64_svg_src(icon_name)
    # Extract the base64 part after the prefix
    base64_part = result.split(",", 1)[1]

    # Should be able to decode without error
    try:
        decoded = base64.b64decode(base64_part)
        assert isinstance(decoded, bytes)
        assert b"<svg" in decoded
    except Exception as e:
        pytest.fail(f"Failed to decode base64: {e}")


@pytest.mark.parametrize("icon_name", list(IconNames))
def test_create_base64_svg_src_decodes_to_svg(icon_name: IconNames):
    """Test that decoded base64 produces valid SVG."""
    result = create_base64_svg_src(icon_name)
    base64_part = result.split(",", 1)[1]
    decoded = base64.b64decode(base64_part).decode("utf-8")

    assert "<svg" in decoded
    assert "</svg>" in decoded
    assert 'xmlns="http://www.w3.org/2000/svg"' in decoded


def test_create_base64_svg_src_default_color():
    """Test that default color is applied in base64 output."""
    result = create_base64_svg_src(IconNames.MATERIAL_INFO)
    base64_part = result.split(",", 1)[1]
    decoded = base64.b64decode(base64_part).decode("utf-8")

    # Default color should be #000
    assert "#000" in decoded


def test_create_base64_svg_src_custom_color():
    """Test that custom color is applied in base64 output."""
    custom_color = "#FF5733"
    result = create_base64_svg_src(IconNames.MATERIAL_ERROR, color=custom_color)
    base64_part = result.split(",", 1)[1]
    decoded = base64.b64decode(base64_part).decode("utf-8")

    assert custom_color in decoded


def test_create_base64_svg_src_different_colors():
    """Test that different colors produce different base64 outputs."""
    red_result = create_base64_svg_src(IconNames.MATERIAL_ADD, color="#FF0000")
    blue_result = create_base64_svg_src(IconNames.MATERIAL_ADD, color="#0000FF")

    assert red_result != blue_result


def test_create_base64_svg_src_rgb_color():
    """Test that RGB color format works in base64."""
    rgb_color = "rgb(255, 0, 0)"
    result = create_base64_svg_src(IconNames.MATERIAL_REMOVE, color=rgb_color)
    base64_part = result.split(",", 1)[1]
    decoded = base64.b64decode(base64_part).decode("utf-8")

    assert rgb_color in decoded


def test_create_base64_svg_src_named_color():
    """Test that named colors work in base64."""
    result = create_base64_svg_src(IconNames.MATERIAL_HELP, color="red")
    base64_part = result.split(",", 1)[1]
    decoded = base64.b64decode(base64_part).decode("utf-8")

    assert "red" in decoded


def test_create_base64_svg_src_consistent_output():
    """Test that same inputs produce same base64 output."""
    result1 = create_base64_svg_src(IconNames.MDI_ROCKET, color="#123456")
    result2 = create_base64_svg_src(IconNames.MDI_ROCKET, color="#123456")
    assert result1 == result2


def test_create_base64_svg_src_empty_color():
    """Test create_base64_svg_src with empty color string."""
    result = create_base64_svg_src(IconNames.MDI_USER, color="")
    assert result.startswith("data:image/svg+xml;base64,")

    base64_part = result.split(",", 1)[1]
    decoded = base64.b64decode(base64_part).decode("utf-8")
    assert "fill=" in decoded or "stroke=" in decoded


def test_create_base64_svg_src_roundtrip():
    """Test that we can decode what we encode and get back the original SVG."""
    original_svg = get_svg_icon(IconNames.MATERIAL_DATABASE, color="#ABCDEF")
    base64_result = create_base64_svg_src(IconNames.MATERIAL_DATABASE, color="#ABCDEF")

    # Extract and decode
    base64_part = base64_result.split(",", 1)[1]
    decoded_svg = base64.b64decode(base64_part).decode("utf-8")

    # Should match the original (accounting for potential whitespace)
    assert decoded_svg.strip() == original_svg.strip() or decoded_svg == original_svg


@pytest.mark.parametrize(
    ("icon_name", "size_px"),
    [
        (IconNames.MDI_HIDE, 16),
        (IconNames.MDI_SHOW, 20),
    ],
)
def test_create_icon_span_returns_span_with_expected_style(
    icon_name: IconNames,
    size_px: int,
):
    """Test that create_icon_span returns the expected masked span element."""
    result = create_icon_span(icon_name, size_px=size_px)
    expected_src = create_base64_svg_src(icon_name, color="#000")

    assert isinstance(result, html.Span)
    assert result.style is not None  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["display"] == "inline-block"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["width"] == f"{size_px}px"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["height"] == f"{size_px}px"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["backgroundColor"] == "currentColor"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["maskRepeat"] == "no-repeat"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["maskPosition"] == "center"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["maskSize"] == "contain"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["WebkitMaskRepeat"] == "no-repeat"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["WebkitMaskPosition"] == "center"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["WebkitMaskSize"] == "contain"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert _extract_css_url_value(result.style["maskImage"]) == expected_src  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert _extract_css_url_value(result.style["WebkitMaskImage"]) == expected_src  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span


def test_create_icon_span_mask_sources_match():
    """Test that standard and webkit mask image sources are kept in sync."""
    result = create_icon_span(IconNames.MATERIAL_INFO, size_px=14)

    assert result.style is not None  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["maskImage"] == result.style["WebkitMaskImage"]  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span


@pytest.mark.parametrize(
    ("color_input", "expected_background_color"),
    [
        (None, "currentColor"),
        ("", "currentColor"),
        ("#FF5733", "#FF5733"),
        ("var(--mantine-color-blue-6)", "var(--mantine-color-blue-6)"),
    ],
)
def test_create_icon_span_color_handling(
    color_input: str | None,
    expected_background_color: str,
):
    """Test color handling for default, fallback, and explicit color inputs."""
    result = create_icon_span(
        IconNames.MATERIAL_INFO,
        size_px=16,
        color=color_input,
    )

    assert result.style is not None  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["backgroundColor"] == expected_background_color  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span


def test_create_icon_span_mask_uses_black_encoded_svg_even_with_custom_color():
    """Test that the mask source is generated from a black SVG always."""
    result = create_icon_span(
        IconNames.MATERIAL_HELP,
        size_px=16,
        color="#FF0000",
    )
    expected_src = create_base64_svg_src(IconNames.MATERIAL_HELP, color="#000")

    assert result.style is not None  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert _extract_css_url_value(result.style["maskImage"]) == expected_src  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert _extract_css_url_value(result.style["WebkitMaskImage"]) == expected_src  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span


def test_create_image_icon_span_defaults_to_current_color_and_no_classname():
    """Test that create_image_icon_span defaults color/class behavior."""
    result = create_image_icon_span("/assets/icons/custom.svg", size_px=16)

    assert isinstance(result, html.Span)
    assert result.className is None  # type: ignore[reportAttributeAccessIssue] - className exists on html.Span
    assert result.style is not None  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["backgroundColor"] == "currentColor"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert _extract_css_url_value(result.style["maskImage"]) == "/assets/icons/custom.svg"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span


def test_create_image_icon_span_supports_custom_color_and_classname():
    """Test that create_image_icon_span applies explicit color and className."""
    result = create_image_icon_span(
        "material-symbols:home",
        size_px=20,
        color="#FF5733",
        class_name="tree-icon-mask",
    )

    assert isinstance(result, html.Span)
    assert result.className == "tree-icon-mask"  # type: ignore[reportAttributeAccessIssue] - className exists on html.Span
    assert result.style is not None  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["backgroundColor"] == "#FF5733"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["width"] == "20px"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["height"] == "20px"  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span


def test_create_image_icon_span_keeps_mask_image_url_as_provided():
    """Test that create_image_icon_span uses preformatted URL values without mutation."""
    raw_mask_image = r'C:\icons\my"icon".svg'
    result = create_image_icon_span(raw_mask_image, size_px=16)

    assert result.style is not None  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert result.style["maskImage"] == result.style["WebkitMaskImage"]  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span
    assert _extract_css_url_value(result.style["maskImage"]) == raw_mask_image  # type: ignore[reportAttributeAccessIssue] - style exists on html.Span


def _extract_css_url_value(css_url: str) -> str:
    """Extract inner value from a CSS ``url(...)`` token, independent of quote style."""
    assert css_url.startswith("url(")
    assert css_url.endswith(")")
    inner = css_url[4:-1]
    if inner.startswith(('"', "'")) and inner.endswith(('"', "'")):
        inner = inner[1:-1]
    return inner.replace('\\"', '"').replace("\\\\", "\\")
