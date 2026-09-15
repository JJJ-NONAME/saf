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

from ansys.hps.client.rms import RmsApi  # pyright: ignore[reportMissingTypeStubs]

from ansys.saf.glow._hps_parametric_studies.base import HpsComputeResourceSet, HpsQueue, IHpsSystemInformation
from ansys.saf.glow._hps_parametric_studies.system import HpsParametricStudySystem


class HpsSystemInformationImpl(IHpsSystemInformation):
    @staticmethod
    def get_compute_resource_sets(
        hps_server_url: str | None = None,
        client_id: str | None = None,
    ) -> list[HpsComputeResourceSet]:
        # Note that this is going to create a new authenticator every time it is called and thus it will not benefit
        # of cached HPS Clients.
        with HpsParametricStudySystem.get_hps_client(
            hps_server_url=hps_server_url,
            client_id=client_id,
        ) as hps_client:
            rms_api = RmsApi(hps_client)
            num_compute_resource_sets = (
                rms_api.get_compute_resource_sets_count()  # pyright: ignore[reportUnknownMemberType]
            )
            compute_resource_sets = rms_api.get_compute_resource_sets(  # pyright: ignore[reportUnknownMemberType]
                limit=num_compute_resource_sets,
            )
            available_resource_sets: list[HpsComputeResourceSet] = []
            for compute_resource_set in compute_resource_sets:
                if not compute_resource_set.name:
                    continue
                compute_resource_info = rms_api.get_cluster_info(  # pyright: ignore[reportUnknownMemberType]
                    compute_resource_set.id,
                )
                queues_available = []
                if compute_resource_info.queues:
                    queues_available = [
                        HpsQueue(name=queue.name) for queue in compute_resource_info.queues if queue.name
                    ]
                available_resource_sets.append(
                    HpsComputeResourceSet(name=compute_resource_set.name, queues=queues_available),
                )
            return available_resource_sets
