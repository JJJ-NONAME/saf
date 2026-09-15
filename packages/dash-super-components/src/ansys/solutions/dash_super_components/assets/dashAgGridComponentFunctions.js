// Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
// SPDX-License-Identifier: Apache-2.0
//
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

const commonColors = {
    MANTINE_BLUE: "var(--mantine-color-blue-6)",
    MANTINE_ORANGE: "var(--mantine-color-orange-6)",
    MANTINE_RED: "var(--mantine-color-red-6)",
    MANTINE_PINK: "var(--mantine-color-pink-6)",
    MANTINE_GRAPE: "var(--mantine-color-grape-6)",
};

dagcomponentfuncs.DMC_Badge_Level_Name = function (props) {
    const {setData, data} = props;

    function onClick() {
        setData();
    }
    let leftSection, color;

    if (props.value == "INFO") {
        leftSection = React.createElement(window.dash_iconify.DashIconify, {
            icon: "material-symbols:info",
        });
        color = commonColors.MANTINE_BLUE;
    }
    else if (props.value == "WARNING") {
        leftSection = React.createElement(window.dash_iconify.DashIconify, {
            icon: "material-symbols:warning",
        });
        color = commonColors.MANTINE_ORANGE;
    }
    else if (props.value == "ERROR") {
        leftSection = React.createElement(window.dash_iconify.DashIconify, {
            icon: "icon-park-solid:error",
        });
        color = commonColors.MANTINE_RED;
    }
    else if (props.value == "CRITICAL") {
        leftSection = React.createElement(window.dash_iconify.DashIconify, {
            icon: "eos-icons:critical-bug-outlined",
        });
        color = commonColors.MANTINE_PINK;
    }
    else if (props.value == "DEBUG") {
        leftSection = React.createElement(window.dash_iconify.DashIconify, {
            icon: "eos-icons:critical-bug",
        });
        color = commonColors.MANTINE_GRAPE;
    }

    return React.createElement(
        window.dash_mantine_components.Badge,
        {
            onClick,
            variant: props.variant,
            color: color,
            leftSection: leftSection,
            radius: props.radius,
            size: props.size,
            style: props.style,
        },
        props.value
    );
};

dagcomponentfuncs.DMC_NoRows_Overlay = function (props) {
    return React.createElement(
        "div",
        {className: "ag-overlay-no-rows-center", role: "status"},
        props.message || "No rows to show."
    );
};
