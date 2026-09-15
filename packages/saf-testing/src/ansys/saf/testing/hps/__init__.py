# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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

from ansys.saf.testing._common.common import has_modules_installed
from ansys.saf.testing._hps.hps import (
    configure_hps_deployment_keycloak,
    configure_hps_deployment_traefik_tls_setup,
    external_hps_deployment,
    external_hps_scaler,
    hps_deployment,
    hps_host,
    hps_port,
    hps_scaler,
    is_hps_enabled,
    is_hps_requested,
    restore_default_hps_deployment,
    should_hps_be_launched,
)

__all__ = [
    "external_hps_deployment",
    "external_hps_scaler",
    "is_hps_requested",
    "should_hps_be_launched",
    "is_hps_enabled",
    "hps_deployment",
    "hps_host",
    "hps_scaler",
    "hps_port",
    "configure_hps_deployment_keycloak",
    "configure_hps_deployment_traefik_tls_setup",
    "restore_default_hps_deployment",
]

if has_modules_installed(["ansys.hps.client"]):
    from ansys.saf.testing._hps.hps_client import (
        GetHpsJobIdsType,
        get_available_application_on_hps,
        get_hps_job_ids,
        get_hps_job_output,
    )

    __all__ += ["GetHpsJobIdsType", "get_hps_job_ids", "get_hps_job_output", "get_available_application_on_hps"]
