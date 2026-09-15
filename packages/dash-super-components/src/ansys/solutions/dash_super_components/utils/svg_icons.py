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

"""
Provide offline SVG icons with customizable color parameters.

This module provides utilities for working with SVG icons bundled with the
library. You can look up available icon names using the ``IconNames`` enum
and encode SVG icons as Base64 data URIs for use in Dash components.
"""

import base64
from enum import Enum

from dash_extensions.enrich import html


# Icon name constants
class IconNames(Enum):
    """Constants for SVG icon names."""

    AKAR_CIRCLE_CHECK = "akar-icons--circle-check"
    CARBON_IBM_WORKFLOW = "carbon--ibm-engineering-workflow-mgmt"
    CARBON_RETURN = "carbon--return"
    EOS_CRITICAL_BUG = "eos-icons--critical-bug-outlined"
    EOS_LOADING = "eos-icons--loading"
    EOS_MONITORING = "eos-icons--monitoring"
    FLUENT_DATA_SUNBURST = "fluent--data-sunburst-24-filled"
    GAME_CROSSED_AIR_FLOWS = "game-icons--crossed-air-flows"
    GAME_RADAR_SWEEP = "game-icons--radar-sweep"
    HEALTH_NO = "healthicons--no"
    HEALTH_YES = "healthicons--yes"
    HERO_ADJUSTMENTS = "hero-outline--adjustments"
    HERO_DATABASE = "hero-outline--database"
    HUGE_FILE_SEARCH = "hugeicons--file-search"
    HUGE_ROCKET = "hugeicons--rocket"
    ICON_PARK_ERROR = "icon-park-solid--error"
    ICON_PARK_OUTLINE_SUCCESS = "icon-park-outline--success"
    ICON_PARK_PERMISSIONS = "icon-park-outline--permissions"
    IC_EMAIL = "ic--baseline-email"
    IC_ROUND_CELEBRATION = "ic--round-celebration"
    MATERIAL_ADD = "material-symbols--add"
    MATERIAL_DATABASE = "material-symbols--database"
    MATERIAL_DELETE = "material-symbols--delete"
    MATERIAL_DOWNLOAD = "material-symbols--download"
    MATERIAL_ERROR = "material-symbols--error"
    MATERIAL_FOLDER = "material-symbols--folder"
    MATERIAL_HELP = "material-symbols--help"
    MATERIAL_HOME = "material-symbols--home"
    MATERIAL_INFO = "material-symbols--info"
    MATERIAL_LIST = "material-symbols--list"
    MATERIAL_REMOVE = "material-symbols--remove"
    MATERIAL_TREE = "material-symbols--tree"
    MATERIAL_UI_TABLE_ROWS = "materialui--table-rows"
    MATERIAL_WARNING = "material-symbols--warning"
    MDI_FILE_TREE = "mdi--file-tree"
    MDI_FOLDER_SEARCH = "mdi--folder-search"
    MDI_FORM_OUTLINE = "mdi--form-outline"
    MDI_HIDE = "mdi--hide"
    MDI_ROCKET = "mdi--rocket"
    MDI_SECURE = "mdi--secure"
    MDI_SHOW = "mdi--show"
    MDI_SLIDER = "mdi--slider"
    MDI_TABLE_EYE = "mdi--table-eye"
    MDI_USER = "mdi--user"
    OCTICONS_THREE_BARS = "octicons--three-bars-bold"
    PEPICONS_INTERNET = "pepicons-pencil--internet"
    PH_CODE_FILL = "ph--code-fill"
    RADIX_MOON = "radix-icons--moon"
    RADIX_SUN = "radix-icons--sun"
    SIMPLE_OPSLEVEL = "simple-icons--opslevel"
    SI_ERROR_DUOTONE = "si--error-duotone"
    STREAMLINE_SHARP_STARTUP = "streamline-sharp--startup-solid"
    STREAMLINE_STARTUP = "streamline--startup-solid"
    TEENYICONS_DOC_SOLID = "teenyicons--doc-solid"


def get_svg_icon(icon_name: IconNames, color: str = "#000") -> str:
    """
    Return inline SVG content for icons with specified color.

    Parameters
    ----------
    icon_name : IconNames
        The name of the icon
    color : str, optional
        The color to apply to the SVG (default: "#000")

    Returns
    -------
    str
        SVG content as HTML string
    """
    svg_icons: dict[IconNames, str] = {
        IconNames.CARBON_RETURN: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
                <path fill="{color}" d="M22 8v2c2.206 0 4 1.794 4 4s-1.794 4-4 4H10v-5l-6 6l6 6v-5h12c3.309 0 6-2.691 6-6s-2.691-6-6-6"/>
            </svg>
        """,
        IconNames.CARBON_IBM_WORKFLOW: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
                <path fill="{color}" d="M31.324 11.261A14.27 14.27 0 0 0 22.25 8H22v2h.25c2.608 0 5.155.837 7.246 2.372a12.18 12.18 0 0 1-7.548 7.036q.052-.605.052-1.22C22 10.366 15.635 4 7.812 4c-.929 0-1.856.09-2.757.268l-.657.13l-.13.657A14.3 14.3 0 0 0 4 7.812c0 4.124 1.78 7.831 4.598 10.426A14.2 14.2 0 0 0 8 22.254l.001.001a14.27 14.27 0 0 0 3.261 9.07l.439.53l.652-.22a14.18 14.18 0 0 0 9.237-10.046a14.18 14.18 0 0 0 10.045-9.237l.22-.652zM12.372 29.496A12.27 12.27 0 0 1 10 22.251c0-.912.113-1.796.303-2.652a14.1 14.1 0 0 0 9.105 2.349a12.18 12.18 0 0 1-7.036 7.548m7.51-9.613q-.833.116-1.694.117c-2.715 0-5.218-.904-7.247-2.412a12.4 12.4 0 0 1 4.048-5.204l-1.28-1.53A14.3 14.3 0 0 0 9.37 16.2A12.14 12.14 0 0 1 6.117 6.117A12 12 0 0 1 7.812 6C14.532 6 20 11.468 20 18.188q0 .862-.117 1.695Z"/>
                <circle cx="20" cy="2" r="2" fill="{color}"/>
                <circle cx="27" cy="26" r="2" fill="{color}"/>
                <circle cx="2" cy="20" r="2" fill="{color}"/>
            </svg>
        """,
        IconNames.EOS_MONITORING: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M11 18h2v3h-2zm5 3v2H8v-2zm4-3H4a3.003 3.003 0 0 1-3-3V4a3.003 3.003 0 0 1 3-3h16a3.003 3.003 0 0 1 3 3v11a3.003 3.003 0 0 1-3 3M4 3a1 1 0 0 0-1 1v11a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1V4a1 1 0 0 0-1-1Z"/>
                <path fill="{color}" d="m16 15l-1.914-6.38L13 13l-1.309-3h-.331L10 14L8.843 9.933L8.309 11H5v-1h2.691L9 7l1.068 3.713L10.64 9h1.669l.487.973L14 4l2 8l.64-2H19v1h-1.64z"/>
            </svg>
        """,
        IconNames.FLUENT_DATA_SUNBURST: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M15 3.51c0 .322.2.607.493.74a8.53 8.53 0 0 1 4.258 4.257a.82.82 0 0 0 .739.494c.521 0 .892-.508.684-.986a10.04 10.04 0 0 0-5.188-5.189c-.479-.208-.986.163-.986.685m-6.986-.684c.479-.208.986.163.986.685a.82.82 0 0 1-.494.738A8.53 8.53 0 0 0 4.25 8.507a.82.82 0 0 1-.739.494c-.522 0-.892-.508-.684-.986a10.04 10.04 0 0 1 5.188-5.189M15 20.49c0-.321.2-.606.493-.738a8.53 8.53 0 0 0 4.258-4.258a.82.82 0 0 1 .739-.493c.521 0 .892.507.684.985a10.04 10.04 0 0 1-5.188 5.189c-.479.208-.986-.163-.986-.685M4.249 15.494a.82.82 0 0 0-.739-.493c-.522 0-.892.507-.684.985a10.04 10.04 0 0 0 5.188 5.189c.479.208.986-.163.986-.685a.82.82 0 0 0-.494-.738a8.53 8.53 0 0 1-4.257-4.258m7.75-8.993q-.29 0-.571.029a.75.75 0 1 1-.154-1.492Q11.633 5 12 5a7 7 0 0 1 6.826 5.443a.75.75 0 0 1-1.463.332A5.5 5.5 0 0 0 12 6.501m-2.878-.1a.75.75 0 0 1-.2 1.042A5.5 5.5 0 0 0 6.5 12a5.47 5.47 0 0 0 .942 3.08a.75.75 0 0 1-1.242.84A6.97 6.97 0 0 1 5 12a7 7 0 0 1 3.08-5.8a.75.75 0 0 1 1.041.2m9.11 6.505a.75.75 0 0 1 .529.919a7.003 7.003 0 0 1-10.01 4.377a.75.75 0 0 1 .697-1.328a5.503 5.503 0 0 0 7.864-3.44a.75.75 0 0 1 .92-.528M12 8a4 4 0 1 0 0 8a4 4 0 0 0 0-8"/>
            </svg>
        """,
        IconNames.GAME_CROSSED_AIR_FLOWS: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
                <path fill="{color}" d="M21 18.035v5.088c109.998 50.032 220.054 122.967 293.453 201.82a839 839 0 0 1-6.23 10.54C218.595 169.884 117.723 122.586 21 92.822v77.1c75.186 16.99 155.106 46.088 231.27 89.356c-54.09-19.95-113.754-32.143-175.204-33.876c59.19 20.343 123.45 46.638 184.955 78.492c-65.03 85.433-145.31 149.098-239.266 174.39C141.178 511.62 307.632 481.4 414 401.755c30.91 25.406 58.157 52.78 79.965 82.025v-5.17c-10.706-36.043-26.167-71.84-45.272-106.794c12.84-12.864 24.225-26.682 33.852-41.416c-56.283 49.778-128.067 78.627-216.725 105.834c78.377-44.805 146.055-100.623 199.133-159.6a817 817 0 0 0 29.012-36.52v-38.41c-75.202 99.392-188.794 188.773-302.738 236.14c122.326-68.48 252.93-199.788 297.607-323.684c-38.43 54.704-84.59 103.334-133.86 144.86c57.522-73.943 108.355-152.33 138.99-216.06V18.036h-90.03c-20.39 65.42-46.51 128.732-78.065 186.61c-72.37-77.783-156.326-143.35-233.247-186.61H21zM186.703 439.5h.492c-.32.13-.64.265-.96.395c.156-.13.313-.265.468-.395"/>
            </svg>
        """,
        IconNames.GAME_RADAR_SWEEP: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
                <path fill="{color}" d="M252.78 20.875c-1.302.012-2.6.03-3.905.063c-37.928.974-76.148 11.153-111.28 31.437C25.164 117.285-13.41 261.322 51.5 373.75s208.946 151.036 321.375 86.125c77.7-44.86 120.1-127.513 117.47-211.406c-3.563 65.847-35.898 128.573-91 169.374a218 218 0 0 1-35.814 25.844c-103.68 59.86-235.983 24.4-295.842-79.282c-59.86-103.68-24.43-235.984 79.25-295.844c35.64-20.576 74.67-29.88 112.968-29.03c63.304 1.4 124.623 30.57 165.438 82.53l-32.594 23.032c-33.27-42.835-84.01-66.6-136.063-67c-.96-.008-1.91-.012-2.875 0c-.964.01-1.943.038-2.906.062c-28.006.717-56.222 8.215-82.156 23.188c-82.99 47.914-111.508 154.322-63.594 237.312s154.32 111.51 237.313 63.594c51.37-29.66 81.862-81.724 86.28-136.78c-12.53 45.37-42.32 86.745-85.438 114.186c-.02.013-.043.018-.062.03l-.344.22a158 158 0 0 1-9.78 6.156c-74.245 42.865-168.918 17.494-211.782-56.75c-42.864-74.243-17.493-168.917 56.75-211.78c23.2-13.396 48.39-20.122 73.375-20.782c47.953-1.266 95.138 19.858 125.968 59.156l-39.844 28.156c-20.232-24.32-50.055-37.79-80.594-38.03c-1.17-.01-2.33 0-3.5.03c-17.035.432-34.176 4.995-49.938 14.094c-50.435 29.12-67.806 93.877-38.687 144.313c29.12 50.434 93.908 67.806 144.344 38.686c21.245-12.267 36.623-30.85 45.124-52.03c-18.815 21.064-44.364 36.888-73.938 44.155c-.04.013-.084.02-.125.033c-37.507 10.787-78.796-4.816-99.217-40.188c-24.07-41.688-9.845-94.712 31.843-118.78c13.028-7.523 27.143-11.314 41.156-11.69c25.66-.685 50.898 10.098 68.188 30.25l-41 28.97c-5.497-4.796-12.664-7.72-20.53-7.72c-17.277 0-31.283 14.007-31.283 31.282c0 17.276 14.004 31.282 31.282 31.282s31.28-14.007 31.28-31.283c0-1.187-.06-2.347-.188-3.5l120.094-57.312l4.03-1.75l-.06-.156l62.25-29.72l9.25-4.438l-5.282-8.812l-19.97-33.375l-5.155-8.625l-8.25 5.813l-8.095 5.718c-45.9-58.864-116.14-91.053-187.844-90.405z"/>
            </svg>
        """,
        IconNames.HERO_ADJUSTMENTS: f"""
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="{color}">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>
            </svg>
        """,
        IconNames.HERO_DATABASE: f"""
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="{color}">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"/>
            </svg>
        """,
        IconNames.HUGE_ROCKET: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24">
                <g fill="none" stroke="{color}" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="m8 10.167l4.123-4.124c1.125-1.124 1.688-1.687 2.308-2.14A9.9 9.9 0 0 1 18.74 2.12C19.499 2 20.293 2 21.885 2c.083 0 .115.038.115.115c0 1.59 0 2.386-.119 3.145a9.9 9.9 0 0 1-1.784 4.309c-.453.62-1.016 1.183-2.14 2.308L13.833 16"/>
                    <path stroke-linejoin="round" d="M10.341 8.098c-1.703 0-3.843-.36-5.437.3C3.737 8.88 2.878 10 2 10.878l3.306 1.418c.876.375.34 1.48.195 2.206c-.161.808-.152.838.43 1.42l2.147 2.146c.582.583.612.592 1.42.43c.725-.145 1.831-.68 2.206.196L13.121 22c.878-.878 1.998-1.737 2.481-2.904c.66-1.594.3-3.734.3-5.437"/>
                    <path stroke-linecap="round" stroke-linejoin="round" d="m12 20l-1 1m-7-9l-1 1"/>
                    <path stroke-linecap="square" d="M15 4.08c1.2.18 2.46.66 3.161 1.38c.897.792 1.519 1.86 1.759 3.54"/>
                    <path stroke-linecap="round" d="M17.94 6.06L16.5 7.5"/>
                </g>
            </svg>
        """,
        IconNames.IC_EMAIL: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2m0 4l-8 5l-8-5V6l8 5l8-5z"/>
            </svg>
        """,
        IconNames.ICON_PARK_PERMISSIONS: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
                <g fill="none" stroke="{color}" stroke-linecap="round" stroke-width="4">
                    <path stroke-linejoin="round" d="M20 10H6a2 2 0 0 0-2 2v26a2 2 0 0 0 2 2h36a2 2 0 0 0 2-2v-2.5"/>
                    <path d="M10 23h8m-8 8h24"/>
                    <circle cx="34" cy="16" r="6" stroke-linejoin="round"/>
                    <path stroke-linejoin="round" d="M44 28.419C42.047 24.602 38 22 34 22s-5.993 1.133-8.05 3"/>
                </g>
            </svg>
        """,
        IconNames.MATERIAL_DATABASE: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M12 11q3.75 0 6.375-1.175T21 7t-2.625-2.825T12 3T5.625 4.175T3 7t2.625 2.825T12 11m0 2.5q1.025 0 2.563-.213t2.962-.687t2.45-1.237T21 9.5V12q0 1.1-1.025 1.863t-2.45 1.237t-2.962.688T12 16t-2.562-.213t-2.963-.687t-2.45-1.237T3 12V9.5q0 1.1 1.025 1.863t2.45 1.237t2.963.688T12 13.5m0 5q1.025 0 2.563-.213t2.962-.687t2.45-1.237T21 14.5V17q0 1.1-1.025 1.863t-2.45 1.237t-2.962.688T12 21t-2.562-.213t-2.963-.687t-2.45-1.237T3 17v-2.5q0 1.1 1.025 1.863t2.45 1.237t2.963.688T12 18.5"/>
            </svg>
        """,
        IconNames.MATERIAL_DOWNLOAD: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="m12 16l-5-5l1.4-1.45l2.6 2.6V4h2v8.15l2.6-2.6L17 11zm-6 4q-.825 0-1.412-.587T4 18v-3h2v3h12v-3h2v3q0 .825-.587 1.413T18 20z"/>
            </svg>
        """,
        IconNames.MATERIAL_ERROR: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M12 17q.425 0 .713-.288T13 16t-.288-.712T12 15t-.712.288T11 16t.288.713T12 17m-1-4h2V7h-2zm1 9q-2.075 0-3.9-.788t-3.175-2.137T2.788 15.9T2 12t.788-3.9t2.137-3.175T8.1 2.788T12 2t3.9.788t3.175 2.137T21.213 8.1T22 12t-.788 3.9t-2.137 3.175t-3.175 2.138T12 22"/>
            </svg>
        """,
        IconNames.MATERIAL_FOLDER: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M4 20q-.825 0-1.412-.587T2 18V6q0-.825.588-1.412T4 4h6l2 2h8q.825 0 1.413.588T22 8v10q0 .825-.587 1.413T20 20z" />
            </svg>
        """,
        IconNames.MATERIAL_HOME: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M4 21V9l8-6l8 6v12h-6v-7h-4v7z"/>
            </svg>
        """,
        IconNames.MATERIAL_INFO: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24">
                <path fill="{color}" d="M11 17h2v-6h-2zm1-8q.425 0 .713-.288T13 8t-.288-.712T12 7t-.712.288T11 8t.288.713T12 9m0 13q-2.075 0-3.9-.788t-3.175-2.137T2.788 15.9T2 12t.788-3.9t2.137-3.175T8.1 2.788T12 2t3.9.788t3.175 2.137T21.213 8.1T22 12t-.788 3.9t-2.137 3.175t-3.175 2.138T12 22"/>
            </svg>
        """,
        IconNames.MATERIAL_LIST: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M7 9V7h14v2zm0 4v-2h14v2zm0 4v-2h14v2zM4 9q-.425 0-.712-.288T3 8t.288-.712T4 7t.713.288T5 8t-.288.713T4 9m0 4q-.425 0-.712-.288T3 12t.288-.712T4 11t.713.288T5 12t-.288.713T4 13m0 4q-.425 0-.712-.288T3 16t.288-.712T4 15t.713.288T5 16t-.288.713T4 17"/>
            </svg>
        """,
        IconNames.MATERIAL_UI_TABLE_ROWS: f"""
            <svg xmlns="http://www.w3.org/2000/svg" height="24" width="24" viewBox="0 0 24 24" fill="{color}">
                <path fill="none" d="M0 0h24v24H0z"/>
                <path d="M22 7H2V2h20v5zm0 2.5H2v5h20v-5zm0 7.5H2v5h20v-5z"/>
            </svg>
        """,
        IconNames.MDI_FILE_TREE: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M3 3h6v4H3zm12 7h6v4h-6zm0 7h6v4h-6zm-2-4H7v5h6v2H5V9h2v2h6z"/>
            </svg>
        """,
        IconNames.MDI_FOLDER_SEARCH: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24">
                <path fill="{color}" d="M16.5 12c2.5 0 4.5 2 4.5 4.5c0 .88-.25 1.71-.69 2.4l3.08 3.1L22 23.39l-3.12-3.07c-.69.43-1.51.68-2.38.68c-2.5 0-4.5-2-4.5-4.5s2-4.5 4.5-4.5m0 2a2.5 2.5 0 0 0-2.5 2.5a2.5 2.5 0 0 0 2.5 2.5a2.5 2.5 0 0 0 2.5-2.5a2.5 2.5 0 0 0-2.5-2.5M9 4l2 2h8a2 2 0 0 1 2 2v3.81A6.48 6.48 0 0 0 16.5 10a6.5 6.5 0 0 0-6.5 6.5c0 1.29.37 2.5 1 3.5H3a2 2 0 0 1-2-2V6c0-1.11.89-2 2-2z"/>
            </svg>
        """,
        IconNames.MDI_FORM_OUTLINE: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M11 15h6v2h-6zM9 7H7v2h2zm2 6h6v-2h-6zm0-4h6V7h-6zm-2 2H7v2h2zm12-6v14c0 1.1-.9 2-2 2H5c-1.1 0-2-.9-2-2V5c0-1.1.9-2 2-2h14c1.1 0 2 .9 2 2m-2 0H5v14h14zM9 15H7v2h2z"/>
            </svg>
        """,
        IconNames.MDI_ROCKET: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="m20 22l-3.86-1.55c.7-1.53 1.2-3.11 1.51-4.72zM7.86 20.45L4 22l2.35-6.27c.31 1.61.81 3.19 1.51 4.72M12 2s5 2 5 10c0 3.1-.75 5.75-1.67 7.83A2 2 0 0 1 13.5 21h-3a2 2 0 0 1-1.83-1.17C7.76 17.75 7 15.1 7 12c0-8 5-10 5-10m0 10c1.1 0 2-.9 2-2s-.9-2-2-2s-2 .9-2 2s.9 2 2 2"/>
            </svg>
        """,
        IconNames.MDI_SECURE: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                <path fill="{color}" d="M12 17a2 2 0 0 0 2-2a2 2 0 0 0-2-2a2 2 0 0 0-2 2a2 2 0 0 0 2 2m6-9a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2h1V6a5 5 0 0 1 5-5a5 5 0 0 1 5 5v2zm-6-5a3 3 0 0 0-3 3v2h6V6a3 3 0 0 0-3-3"/>
            </svg>
        """,
        IconNames.MDI_SLIDER: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M8 13c-1.86 0-3.41 1.28-3.86 3H2v2h2.14c.45 1.72 2 3 3.86 3s3.41-1.28 3.86-3H22v-2H11.86c-.45-1.72-2-3-3.86-3m0 6c-1.1 0-2-.9-2-2s.9-2 2-2s2 .9 2 2s-.9 2-2 2M19.86 6c-.45-1.72-2-3-3.86-3s-3.41 1.28-3.86 3H2v2h10.14c.45 1.72 2 3 3.86 3s3.41-1.28 3.86-3H22V6zM16 9c-1.1 0-2-.9-2-2s.9-2 2-2s2 .9 2 2s-.9 2-2 2"/>
            </svg>
        """,
        IconNames.MDI_TABLE_EYE: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M17 16.88c.56 0 1 .44 1 1s-.44 1-1 1s-1-.45-1-1s.44-1 1-1m0-3c2.73 0 5.06 1.66 6 4c-.94 2.34-3.27 4-6 4s-5.06-1.66-6-4c.94-2.34 3.27-4 6-4m0 1.5a2.5 2.5 0 0 0 0 5a2.5 2.5 0 0 0 0-5M18 3H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h5.42c-.16-.32-.3-.66-.42-1c.12-.34.26-.68.42-1H4v-4h6v2.97c.55-.86 1.23-1.6 2-2.21V13h1.15c1.16-.64 2.47-1 3.85-1c1.06 0 2.07.21 3 .59V5c0-1.1-.9-2-2-2m-8 8H4V7h6zm8 0h-6V7h6z"/>
            </svg>
        """,
        IconNames.MDI_USER: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                <path fill="{color}" d="M12 4a4 4 0 0 1 4 4a4 4 0 0 1-4 4a4 4 0 0 1-4-4a4 4 0 0 1 4-4m0 10c4.42 0 8 1.79 8 4v2H4v-2c0-2.21 3.58-4 8-4"/>
            </svg>
        """,
        IconNames.OCTICONS_THREE_BARS: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="{color}">
                <path fill-rule="evenodd" d="M1 2.75A.75.75 0 011.75 2h12.5a.75.75 0 110 1.5H1.75A.75.75 0 011 2.75zm0 5A.75.75 0 011.75 7h12.5a.75.75 0 110 1.5H1.75A.75.75 0 011 7.75zM1.75 12a.75.75 0 100 1.5h12.5a.75.75 0 100-1.5H1.75z"/>
            </svg>
        """,
        IconNames.PEPICONS_INTERNET: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
                <g fill="{color}">
                    <path fill-rule="evenodd" d="M1.5 10a8.5 8.5 0 1 0 17 0a8.5 8.5 0 0 0-17 0m16 0a7.5 7.5 0 1 1-15 0a7.5 7.5 0 0 1 15 0" clip-rule="evenodd"/>
                    <path fill-rule="evenodd" d="M6.5 10c0 4.396 1.442 8 3.5 8s3.5-3.604 3.5-8s-1.442-8-3.5-8s-3.5 3.604-3.5 8m6 0c0 3.889-1.245 7-2.5 7s-2.5-3.111-2.5-7S8.745 3 10 3s2.5 3.111 2.5 7" clip-rule="evenodd"/>
                    <path d="m3.735 5.312l.67-.742q.16.144.343.281c1.318.988 3.398 1.59 5.665 1.59c1.933 0 3.737-.437 5.055-1.19a5.6 5.6 0 0 0 .857-.597l.65.76q-.448.383-1.01.704c-1.477.845-3.452 1.323-5.552 1.323c-2.47 0-4.762-.663-6.265-1.79a6 6 0 0 1-.413-.34m0 9.389l.67.74q.16-.145.343-.28c1.318-.988 3.398-1.59 5.665-1.59c1.933 0 3.737.436 5.055 1.19q.482.277.857.596l.65-.76a6.6 6.6 0 0 0-1.01-.704c-1.477-.844-3.452-1.322-5.552-1.322c-2.47 0-4.762.663-6.265 1.789q-.22.165-.413.34M2 10.5v-1h16v1z"/>
                </g>
            </svg>
        """,
        IconNames.PH_CODE_FILL: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
                <path fill="{color}" d="M216 40H40a16 16 0 0 0-16 16v144a16 16 0 0 0 16 16h176a16 16 0 0 0 16-16V56a16 16 0 0 0-16-16M92.8 145.6a8 8 0 1 1-9.6 12.8l-32-24a8 8 0 0 1 0-12.8l32-24a8 8 0 0 1 9.6 12.8L69.33 128Zm58.89-71.4l-32 112a8 8 0 1 1-15.38-4.4l32-112a8 8 0 0 1 15.38 4.4m53.11 60.2l-32 24a8 8 0 0 1-9.6-12.8l23.47-17.6l-23.47-17.6a8 8 0 1 1 9.6-12.8l32 24a8 8 0 0 1 0 12.8"/>
            </svg>
        """,
        IconNames.SIMPLE_OPSLEVEL: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="M21.246 4.86L13.527.411a3.07 3.07 0 0 0-3.071 0l-2.34 1.344v6.209l3.104-1.793a1.52 1.52 0 0 1 1.544 0l3.884 2.241c.482.282.764.78.764 1.328v4.482a1.54 1.54 0 0 1-.764 1.328l-3.884 2.241V24l8.482-4.897a3.08 3.08 0 0 0 1.544-2.656V7.532a3.05 3.05 0 0 0-1.544-2.672M6.588 14.222V2.652L2.754 4.876A3.08 3.08 0 0 0 1.21 7.532v8.915c0 1.095.581 2.108 1.544 2.656L11.236 24v-6.209L7.352 15.55a1.53 1.53 0 0 1-.764-1.328"/>
            </svg>
        """,
        IconNames.STREAMLINE_STARTUP: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 14 14">
                <path fill="{color}" fill-rule="evenodd" d="m6.547 10.263l-2.81-2.81c.309-.517.617-1.052.922-1.584c1.016-1.766 2.008-3.49 2.938-4.387c2.524-2.524 5.981-1.06 5.981-1.06s1.464 3.457-1.06 5.981c-.89.922-2.587 1.9-4.34 2.908c-.546.315-1.097.632-1.631.952m2.14-6.532a1.582 1.582 0 1 1 3.164 0a1.582 1.582 0 0 1-3.163 0m-4.09-.232C3.18 3.122 1.849 3.82.668 4.903a.48.48 0 0 0 .089.765l1.905 1.148l.002-.004c.275-.46.582-.993.894-1.533c.355-.617.716-1.243 1.04-1.78m2.587 7.84l1.148 1.905a.48.48 0 0 0 .765.088c1.083-1.18 1.782-2.512 1.404-3.93c-.522.314-1.07.63-1.613.943l-.083.048c-.548.316-1.091.628-1.616.943zM2.622 9.343a2 2 0 0 1 1.402 3.46c-.222.212-.569.379-.89.506a11 11 0 0 1-1.1.358c-.367.1-.717.18-.982.233a6 6 0 0 1-.336.059q-.066.009-.133.013a.5.5 0 0 1-.198-.022a.5.5 0 0 1-.241-.156a.5.5 0 0 1-.11-.22a.6.6 0 0 1-.012-.176c.003-.04.009-.086.015-.128c.013-.088.033-.203.06-.334c.053-.264.135-.612.235-.977c.1-.364.222-.754.359-1.095c.128-.321.294-.667.506-.888a2 2 0 0 1 1.425-.633" clip-rule="evenodd"/>
            </svg>
        """,
        IconNames.STREAMLINE_SHARP_STARTUP: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" fill-rule="evenodd" d="M4.5 12.5L16 1h7v7L11.5 19.5zM17.414 8l-.707.707l-1 1l-.707.707L13.586 9l.707-.707l1-1L16 6.586zm1.336 6.371l-6.22 6.22L15 23.06l3.75-3.75zm-8.104 6.397l-1.414-1.414l-1.94 1.939l1.415 1.414zm-3-3l-1.414-1.414l-4.94 4.939l1.415 1.414zm-3-3l-1.414-1.414l-1.94 1.939l1.415 1.414zM3.41 11.47l6.22-6.22H4.69L.94 9z" clip-rule="evenodd"/>
            </svg>
        """,
        IconNames.ICON_PARK_OUTLINE_SUCCESS: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
                <g fill="none" stroke="{color}" stroke-linecap="round" stroke-linejoin="round" stroke-width="4"><path d="m24 4l5.253 3.832l6.503-.012l1.997 6.188l5.268 3.812L41 24l2.021 6.18l-5.268 3.812l-1.997 6.188l-6.503-.012L24 44l-5.253-3.832l-6.503.012l-1.997-6.188l-5.268-3.812L7 24l-2.021-6.18l5.268-3.812l1.997-6.188l6.503.012z"/><path d="m17 24l5 5l10-10"/></g>
            </svg>
        """,
        IconNames.SI_ERROR_DUOTONE: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <g fill="none"><path fill="{color}" fill-opacity="0.16" d="M3.23 7.913L7.91 3.23c.15-.15.35-.23.57-.23h7.05c.21 0 .42.08.57.23l4.67 4.673c.15.15.23.35.23.57v7.054c0 .21-.08.42-.23.57L16.1 20.77c-.15.15-.35.23-.57.23H8.47a.8.8 0 0 1-.57-.23l-4.67-4.673a.8.8 0 0 1-.23-.57V8.473c0-.21.08-.42.23-.57z"/><path stroke="{color}" stroke-linecap="round" stroke-linejoin="round" stroke-miterlimit="10" stroke-width="1.5" d="M12 16h.008M12 8v5M3.23 7.913L7.91 3.23c.15-.15.35-.23.57-.23h7.05c.21 0 .42.08.57.23l4.67 4.673c.15.15.23.35.23.57v7.054c0 .21-.08.42-.23.57L16.1 20.77c-.15.15-.35.23-.57.23H8.47a.8.8 0 0 1-.57-.23l-4.67-4.673a.8.8 0 0 1-.23-.57V8.473c0-.21.08-.42.23-.57z"/></g>
            </svg>
        """,
        IconNames.IC_ROUND_CELEBRATION: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="{color}" d="m3.99 21.29l9.04-3.23c1.38-.49 1.78-2.26.74-3.3l-4.53-4.53c-1.04-1.04-2.8-.64-3.3.74l-3.23 9.04c-.28.8.48 1.56 1.28 1.28M15.06 12l5.06-5.06a1.25 1.25 0 0 1 1.77 0l.06.06c.29.29.77.29 1.06 0s.29-.77 0-1.06l-.06-.06a2.76 2.76 0 0 0-3.89 0L14 10.94c-.29.29-.29.77 0 1.06s.77.29 1.06 0m-5-5.12l-.06.06c-.29.29-.29.77 0 1.06s.77.29 1.06 0l.06-.06a2.76 2.76 0 0 0 0-3.89L11.07 4c-.3-.3-.78-.3-1.07 0c-.29.29-.29.77 0 1.06l.06.06c.48.48.48 1.28 0 1.76m7 5L16 12.94c-.29.29-.29.77 0 1.06s.77.29 1.06 0l1.06-1.06a1.25 1.25 0 0 1 1.77 0l1.08 1.08c.29.29.77.29 1.06 0s.29-.77 0-1.06l-1.08-1.08a2.76 2.76 0 0 0-3.89 0m-2-6L12 8.94c-.29.29-.29.77 0 1.06s.77.29 1.06 0l3.06-3.06a2.76 2.76 0 0 0 0-3.89l-1.06-1.06a.754.754 0 0 0-1.06 0c-.29.29-.29.77 0 1.06l1.06 1.06c.48.49.48 1.29 0 1.77"/>
            </svg>
        """,
        IconNames.MATERIAL_HELP: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                <path fill="{color}" d="M11.95 18q.525 0 .888-.363t.362-.887t-.362-.888t-.888-.362t-.887.363t-.363.887t.363.888t.887.362m-.9-3.85h1.85q0-.825.188-1.3t1.062-1.3q.65-.65 1.025-1.238T15.55 8.9q0-1.4-1.025-2.15T12.1 6q-1.425 0-2.312.75T8.55 8.55l1.65.65q.125-.45.563-.975T12.1 7.7q.8 0 1.2.438t.4.962q0 .5-.3.938t-.75.812q-1.1.975-1.35 1.475t-.25 1.825M12 22q-2.075 0-3.9-.787t-3.175-2.138T2.788 15.9T2 12t.788-3.9t2.137-3.175T8.1 2.788T12 2t3.9.788t3.175 2.137T21.213 8.1T22 12t-.788 3.9t-2.137 3.175t-3.175 2.138T12 22"/>
            </svg>
        """,
        IconNames.AKAR_CIRCLE_CHECK: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="m8 12.5l3 3l5-6"/><circle cx="12" cy="12" r="10"/></g>
            </svg>
        """,
        IconNames.MATERIAL_DELETE: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="{color}" d="M7 21q-.825 0-1.412-.587T5 19V6H4V4h5V3h6v1h5v2h-1v13q0 .825-.587 1.413T17 21zm2-4h2V8H9zm4 0h2V8h-2z"/>
            </svg>
        """,
        IconNames.ICON_PARK_ERROR: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 48 48"><path fill="{color}" fill-rule="evenodd" stroke="{color}" stroke-linecap="round" stroke-linejoin="round" stroke-width="4" d="m6 11l5-5l13 13L37 6l5 5l-13 13l13 13l-5 5l-13-13l-13 13l-5-5l13-13z" clip-rule="evenodd"/></svg>
        """,
        IconNames.MATERIAL_WARNING: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"><path fill="{color}" d="M1 21L12 2l11 19zm11-3q.425 0 .713-.288T13 17t-.288-.712T12 16t-.712.288T11 17t.288.713T12 18m-1-3h2v-5h-2z"/>
            </svg>
        """,
        IconNames.EOS_CRITICAL_BUG: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"><path fill="{color}" d="M11 15h2v2h-2zm0-6h2v5h-2z"/><path fill="{color}" d="M20 8h-2.81a6 6 0 0 0-1.82-1.96L17 4.41L15.59 3l-2.17 2.17A6 6 0 0 0 12 5a6 6 0 0 0-1.41.17L8.41 3L7 4.41l1.62 1.63A6.1 6.1 0 0 0 6.81 8H4v2h2.09A6.6 6.6 0 0 0 6 11v1H4v2h2v1a6.6 6.6 0 0 0 .09 1H4v2h2.81a5.99 5.99 0 0 0 10.38 0H20v-2h-2.09a6.6 6.6 0 0 0 .09-1v-1h2v-2h-2v-1a6.6 6.6 0 0 0-.09-1H20Zm-4 4v3a4 4 0 0 1-.07.7l-.1.65l-.37.65a3.993 3.993 0 0 1-6.92 0l-.37-.64l-.1-.65A4.3 4.3 0 0 1 8 15v-4a4 4 0 0 1 .07-.7l.1-.65l.37-.65a4.1 4.1 0 0 1 1.21-1.31l.57-.39l.74-.18A3.8 3.8 0 0 1 12 7a4 4 0 0 1 .95.12l.68.16l.61.42a3.9 3.9 0 0 1 1.21 1.31l.38.65l.1.65A4 4 0 0 1 16 11Z"/>
            </svg>
        """,
        IconNames.HEALTH_NO: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><path fill="{color}" fill-rule="evenodd" d="M44 24c0 11.046-8.954 20-20 20S4 35.046 4 24S12.954 4 24 4s20 8.954 20 20m-27.778 7.778a1 1 0 0 1 0-1.414L22.586 24l-6.364-6.364a1 1 0 0 1 1.414-1.414L24 22.586l6.364-6.364a1 1 0 0 1 1.414 1.414L25.414 24l6.364 6.364a1 1 0 0 1-1.414 1.414L24 25.414l-6.364 6.364a1 1 0 0 1-1.414 0" clip-rule="evenodd"/></svg>
        """,
        IconNames.HEALTH_YES: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><path fill="{color}" fill-rule="evenodd" d="M24 44c11.046 0 20-8.954 20-20S35.046 4 24 4S4 12.954 4 24s8.954 20 20 20m10.742-26.33a1 1 0 1 0-1.483-1.34L21.28 29.567l-6.59-6.291a1 1 0 0 0-1.382 1.446l7.334 7l.743.71l.689-.762z" clip-rule="evenodd"/></svg>
        """,
        IconNames.EOS_LOADING: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="{color}" d="M12 2A10 10 0 1 0 22 12A10 10 0 0 0 12 2Zm0 18a8 8 0 1 1 8-8A8 8 0 0 1 12 20Z" opacity="0.5"/><path fill="#fff" d="M20 12h2A10 10 0 0 0 12 2V4A8 8 0 0 1 20 12Z"><animateTransform attributeName="transform" dur="1s" from="0 12 12" repeatCount="indefinite" to="360 12 12" type="rotate"/></path>
            </svg>
        """,
        IconNames.HUGE_FILE_SEARCH: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"><path d="M20 13v-2.343c0-.818 0-1.226-.152-1.594c-.152-.367-.441-.657-1.02-1.235l-4.736-4.736c-.499-.499-.748-.748-1.058-.896a2 2 0 0 0-.197-.082C12.514 2 12.161 2 11.456 2c-3.245 0-4.868 0-5.967.886a4 4 0 0 0-.603.603C4 4.59 4 6.211 4 9.456V14c0 3.771 0 5.657 1.172 6.828C6.235 21.892 7.886 21.99 11 22m2-19.5V3c0 2.828 0 4.243.879 5.121C14.757 9 16.172 9 19 9h.5"/><path d="m20 22l-2.147-2.147m0 0a3.43 3.43 0 0 0 1.004-2.424a3.429 3.429 0 1 0-1.004 2.424"/></g>
            </svg>
        """,
        IconNames.MATERIAL_ADD: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"><path fill="{color}" d="M11 13H5v-2h6V5h2v6h6v2h-6v6h-2z"/>
            </svg>
        """,
        IconNames.MATERIAL_REMOVE: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="20px" height="20px" viewBox="0 0 24 24"><path fill="{color}" d="M5 13v-2h14v2z"/>
            </svg>
        """,
        IconNames.MDI_SHOW: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="15px" height="15px" viewBox="0 0 24 24"><path fill="{color}" d="M12 9a3 3 0 0 0-3 3a3 3 0 0 0 3 3a3 3 0 0 0 3-3a3 3 0 0 0-3-3m0 8a5 5 0 0 1-5-5a5 5 0 0 1 5-5a5 5 0 0 1 5 5a5 5 0 0 1-5 5m0-12.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5"/>
            </svg>
        """,
        IconNames.MDI_HIDE: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="15px" height="15px" viewBox="0 0 24 24"><path fill="{color}" d="M11.83 9L15 12.16V12a3 3 0 0 0-3-3zm-4.3.8l1.55 1.55c-.05.21-.08.42-.08.65a3 3 0 0 0 3 3c.22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53a5 5 0 0 1-5-5c0-.79.2-1.53.53-2.2M2 4.27l2.28 2.28l.45.45C3.08 8.3 1.78 10 1 12c1.73 4.39 6 7.5 11 7.5c1.55 0 3.03-.3 4.38-.84l.43.42L19.73 22L21 20.73L3.27 3M12 7a5 5 0 0 1 5 5c0 .64-.13 1.26-.36 1.82l2.93 2.93c1.5-1.25 2.7-2.89 3.43-4.75c-1.73-4.39-6-7.5-11-7.5c-1.4 0-2.74.25-4 .7l2.17 2.15C10.74 7.13 11.35 7 12 7"/></svg>
        """,
        IconNames.MATERIAL_TREE: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="15px" height="15px" viewBox="0 0 24 24"><path fill="{color}" d="M15 21v-3h-4V8H9v3H2V3h7v3h6V3h7v8h-7V8h-2v8h2v-3h7v8z"/></svg>
        """,
        IconNames.RADIX_MOON: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 15 15">
                <path fill="{color}" d="m8.544.982l.292.053l.265.06l.324.09l.253.082l.276.104l.24.101l.113.052l.327.165l.322.185l.292.19l.245.178l.32.26l.223.2l.16.158l.12.124l.163.18l.2.24l.152.2q.307.419.545.883l.075.148l.077.166l.113.268a6.5 6.5 0 0 1 .385 1.415l.036.277q.04.365.04.74a6.6 6.6 0 0 1-6.982 6.588l-.268-.02l-.316-.04a6.6 6.6 0 0 1-1.104-.26l-.243-.086l-.304-.122l-.26-.12l-.263-.135a7 7 0 0 1-.371-.217l-.176-.115l-.187-.13l-.12-.09l-.19-.15l-.259-.225l-.072-.066a7 7 0 0 1-.21-.206c-.15-.154-.03-.405.183-.416q.376-.021.739-.081a6.603 6.603 0 0 0 4.33-10.268c-.122-.176.004-.424.217-.4zm1.288 1.424A7.6 7.6 0 0 1 10.35 6.2l.128.006a1.25 1.25 0 1 1-.786 2.305q-.085.181-.179.358a.75.75 0 1 1-.77 1.17a7.6 7.6 0 0 1-3.66 2.513A5.6 5.6 0 1 0 9.832 2.405M1.5 6.1a.4.4 0 0 1 .4.4v.6h.6l.081.009a.4.4 0 0 1 0 .783l-.08.009h-.6v.6a.401.401 0 0 1-.801 0v-.6H.5a.401.401 0 0 1 0-.801h.6v-.6c0-.22.18-.4.4-.4m4-3a.4.4 0 0 1 .4.4v.6h.6l.081.009a.4.4 0 0 1 0 .783l-.08.009h-.6v.6a.401.401 0 0 1-.801 0v-.6h-.6a.401.401 0 0 1 0-.801h.6v-.6c0-.22.18-.4.4-.4m-3-3a.4.4 0 0 1 .4.4v.6h.6l.081.009a.4.4 0 0 1 0 .783l-.08.009h-.6v.6a.401.401 0 0 1-.801 0v-.6h-.6a.401.401 0 0 1 0-.801h.6V.5c0-.22.18-.4.4-.4"/>
            </svg>
        """,
        IconNames.RADIX_SUN: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 15 15">
                <path fill="{color}" d="M7.5 12a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2a.5.5 0 0 1 .5-.5m-3.889-1.318a.5.5 0 0 1 .707.707l-1.415 1.415a.5.5 0 0 1-.707-.707zm7.07 0a.5.5 0 0 1 .708 0l1.415 1.415a.5.5 0 0 1-.707.707l-1.415-1.415a.5.5 0 0 1 0-.707M7.5 4.5a3 3 0 1 1 0 6a3 3 0 0 1 0-6m0 1a2 2 0 1 0 0 4a2 2 0 0 0 0-4M2.5 7a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1zm12 0a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1zM2.196 2.196a.5.5 0 0 1 .707 0l1.415 1.415a.5.5 0 0 1-.707.707L2.196 2.903a.5.5 0 0 1 0-.707m9.9 0a.5.5 0 0 1 .708.707l-1.415 1.415a.5.5 0 0 1-.707-.707zM7.5 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2a.5.5 0 0 1 .5-.5"/>
            </svg>
        """,
        IconNames.TEENYICONS_DOC_SOLID: f"""
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 15 15">
                <path fill="{color}" d="M3 10V7h.5a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.5.5zm4-2.5a.5.5 0 0 1 1 0v2a.5.5 0 0 1-1 0z"/>
                <path fill="{color}" fill-rule="evenodd" d="M1 1.5A1.5 1.5 0 0 1 2.5 0h8.207L14 3.293V13.5a1.5 1.5 0 0 1-1.5 1.5h-10A1.5 1.5 0 0 1 1 13.5zM3.5 6H2v5h1.5A1.5 1.5 0 0 0 5 9.5v-2A1.5 1.5 0 0 0 3.5 6m4 0A1.5 1.5 0 0 0 6 7.5v2a1.5 1.5 0 0 0 3 0v-2A1.5 1.5 0 0 0 7.5 6m2.5 5V6h3v2h-1V7h-1v3h1V9h1v2z" clip-rule="evenodd"/>
            </svg>
        """,
    }

    return svg_icons[icon_name]


def create_base64_svg_src(icon_name: IconNames, color: str = "#000"):
    """
    Create a base64-encoded SVG data URI for the given icon and color.

    Parameters
    ----------
    icon_name : IconNames
        The name of the icon to encode.
    color : str, optional
        The color to apply to the SVG icon (default is "#000").

    Returns
    -------
    str
        A data URI containing the base64-encoded SVG image.
    """
    svg = get_svg_icon(icon_name, color)
    encoded_svg = base64.b64encode(svg.encode())
    return f"data:image/svg+xml;base64,{encoded_svg.decode()}"


def create_icon_span(icon_name: IconNames, size_px: int, color: str | None = None) -> html.Span:
    """Return a span element rendering a built-in library icon.

    Looks up the icon by name from the bundled ``IconNames`` catalog and renders
    it as a CSS mask over a base64-encoded SVG. This keeps the component
    offline-compatible while allowing the icon color to either inherit
    ``currentColor`` from surrounding text or use an explicit override.

    Parameters
    ----------
    icon_name : IconNames
        The name of the icon to render.
    size_px : int
        The size of the icon in pixels.
    color : str | None, optional
        Explicit icon color. If None, the icon inherits ``currentColor`` from
        surrounding text (default is None).

    Returns
    -------
    html.Span
        A Dash HTML span element containing the icon.
    """
    icon_src = create_base64_svg_src(icon_name, color="#000")
    return create_image_icon_span(
        mask_image=icon_src,
        size_px=size_px,
        color=color,
    )


def create_image_icon_span(
    mask_image: str,
    size_px: int,
    *,
    color: str | None = None,
    class_name: str | None = None,
) -> html.Span:
    """Return a span element rendering an arbitrary image source as an icon.

    Accepts any asset path or base64-encoded data URI and renders it using a
    CSS mask, making the icon color controllable via ``color`` or inherited from
    ``currentColor``.

    Parameters
    ----------
    mask_image : str
        Image source for the icon. Can be an asset path or a base64-encoded SVG
        data URI.
    size_px : int
        Icon size in pixels.
    color : str | None, optional
        Explicit icon color. If None or empty, ``currentColor`` is used.
    class_name : str | None, optional
        Optional CSS class name applied to the span.

    Returns
    -------
    html.Span
        A Dash HTML span element containing the icon.
    """
    css_url = _to_css_url(mask_image)
    color = color or "currentColor"
    style = {
        "backgroundColor": color,
        "display": "inline-block",
        "width": f"{size_px}px",
        "height": f"{size_px}px",
        "maskImage": css_url,
        "maskRepeat": "no-repeat",
        "maskPosition": "center",
        "maskSize": "contain",
        "WebkitMaskImage": css_url,
        "WebkitMaskRepeat": "no-repeat",
        "WebkitMaskPosition": "center",
        "WebkitMaskSize": "contain",
    }

    return html.Span(className=class_name, style=style)


def _to_css_url(raw_value: str) -> str:
    """Build a safely quoted CSS ``url(...)`` token from an arbitrary string value.

    Parameters
    ----------
    raw_value : str
        The raw string value to be converted into a CSS ``url(...)`` token.

    Returns
    -------
    str
        A safely quoted CSS ``url(...)`` token.
    """
    escaped_value = raw_value.replace("\\", "\\\\").replace('"', '\\"')
    return f'url("{escaped_value}")'
