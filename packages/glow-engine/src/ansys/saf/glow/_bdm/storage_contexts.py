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

# the following constants are universal across different SAF contexts
# do not move these definitions

RESTAPI_CONTEXT = "uploaded"  # covers REST */blob/* route
PRODUCT_CONTEXT = "product"  # covers product instances
PRODUCT_MANAGER_CONTEXT = "productmgr"  # covers product instance managers
CLIENT_CONTEXT = "client"  # covers python Client including DashClient
GC_CONTEXT = "__gc__"  # covers garbage collection
METHOD_CONTEXT = "method"  # covers transaction methods
PROJECT_BOUNDARY = "project_boundary"
