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

from ansys.saf.glow.solution import Solution, SolutionConfiguration, StepsModel
from tests.mocks.solution_end_to_end.solution.custom_grpc_instance_step import (
    CustomGrpcSharedInstanceStep,
)
from tests.mocks.solution_end_to_end.solution.custom_http_instance_step import (
    CustomHttpSharedInstanceStep,
)
from tests.mocks.solution_end_to_end.solution.custom_tcp_instance_step import CustomTcpSharedInstanceStep
from tests.mocks.solution_end_to_end.solution.custom_unshared_instance_step import (
    CustomUnsharedInstanceStep,
)
from tests.mocks.solution_end_to_end.solution.hps_simple_project_step import HpsSimpleProjectStep
from tests.mocks.solution_end_to_end.solution.parametric_studies_step import ParametricStudiesStep
from tests.mocks.solution_end_to_end.solution.simple_job_step import SimpleJobStep
from tests.mocks.solution_end_to_end.solution.transaction_verification_step import (
    TransactionVerificationStep,
)
from tests.mocks.solution_end_to_end.solution.user_info_step import UserInfoStep


class Steps(StepsModel):
    transaction_verification_step: TransactionVerificationStep
    custom_grpc_shared_instance_step: CustomGrpcSharedInstanceStep
    custom_unshared_instance_step: CustomUnsharedInstanceStep
    custom_http_shared_instance_step: CustomHttpSharedInstanceStep
    custom_tcp_shared_instance_step: CustomTcpSharedInstanceStep
    parametric_studies_step: ParametricStudiesStep
    hps_simple_project_step: HpsSimpleProjectStep
    simple_job_step: SimpleJobStep
    user_info_step: UserInfoStep


class EndToEndSolution(Solution):
    display_name: str = "End-to-end solution"
    steps: Steps
    solution_configuration: SolutionConfiguration = SolutionConfiguration()
