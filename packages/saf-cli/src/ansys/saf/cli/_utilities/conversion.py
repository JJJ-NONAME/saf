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


def to_display_name(name: str) -> str:
    # input: "my-name" or "my_name" or "my name" or "My name"
    # output: "My Name"
    return name.replace("-", " ").replace("_", " ").title()


def to_module_name(name: str, module_type: str = "") -> str:
    # input: "my-name" or "my_name" or "my name" or "My name"
    # output: "my_name{_module-type}" (module_type: _step or _page)
    module_name = name.lower().replace("-", "_").replace(" ", "_")
    if module_type and not module_name.endswith(module_type):
        module_name += f"_{module_type}"
    return module_name


def to_class_name(name: str, class_type: str) -> str:
    # input: "my-name" or "my_name" or "my name" or "My name"
    # output: "MyName{ClassType}" (class_type: Solution or Step)
    class_name = name.title().replace("-", "").replace("_", "").replace(" ", "")
    if not class_name.endswith(class_type):
        class_name += class_type
    return class_name


def to_package_name(name: str) -> str:
    # input: "my-name" or "my_name" or "my name" or "My name"
    # output: "my-name"
    return name.lower().replace("_", "-").replace(" ", "-")


def namespace_to_pkg_name(namespace: str) -> str:
    # input:  "my_org.my_project"
    # output: "my-org-my-project"
    namespace_parts = [to_package_name(part) for part in namespace.split(".")]
    return "-".join(namespace_parts)


def to_docker_name(name: str, version: str) -> str:
    # input: "my-name" or "my_name" or "my name" or "My name" and version = "0.1.dev0"
    # output: "my-name-0-1-dev0"
    return f"{to_package_name(name)}_{version.replace('.', '-')}"


def namespace_to_path(namespace: str) -> str:
    # input:  "my_org.my_project"
    # output: "my_org/my_project"
    return namespace.replace(".", "/")
