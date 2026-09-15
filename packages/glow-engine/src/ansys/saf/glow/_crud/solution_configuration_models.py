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

from typing import Any, Self, TypeVar

from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from sqlalchemy import JSON, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

GLOW_SCHEMA_VERSION = 1
SOLUTION_SCHEMA_VERSION = 1  # do not change, solution developers should do it when extending the solution config class.
SOLUTION_CONFIGURATION_INDEX = 0


class Base(AsyncAttrs, DeclarativeBase):
    pass


class SolutionConfigurationSQL(Base):
    __tablename__ = "solution_configuration"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, default=SOLUTION_CONFIGURATION_INDEX)
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON)


class SolutionConfiguration(BaseModel):
    """
    Contains the configuration of the Solution. This configuration applies to all users and projects of the Solution.

    The configuration can be retrieved and modified using the REST API with the route ``/solution-configuration``.

    To retrieve the configuration within a transaction, specify a parameter with type ``SolutionConfiguration``.

    The configuration can also be retrieved from the Client using the project property ``solution_configuration``.

    Examples
    --------

    Retrieving the Solution configuration from within a transaction:

     >>> @transaction(self=StepSpec())
     >>> def my_transaction(self, config: SolutionConfiguration) -> None:
     >>>     my_method(config.config_field)
     >>>     ...

    Retrieving the Solution configuration from the Client:

     >>> project.solution_configuration.configuration_field
    """

    model_config = ConfigDict(extra="forbid")

    glow_schema_version: int = GLOW_SCHEMA_VERSION
    solution_schema_version: int = SOLUTION_SCHEMA_VERSION

    @field_validator("glow_schema_version")
    @classmethod
    def glow_schema_version_must_be_default(cls, v: int) -> int:
        if v != GLOW_SCHEMA_VERSION:
            raise ValueError(f"GLOW schema version mismatch: {v}. Expected {GLOW_SCHEMA_VERSION}.")
        return v

    @model_validator(mode="after")
    def solution_schema_version_must_be_default(self) -> Self:
        default_solution_schema_version = self.model_fields[  # pyright: ignore[reportDeprecated]
            "solution_schema_version"
        ].default  # pyright: ignore[reportDeprecated]
        if self.solution_schema_version != default_solution_schema_version:
            raise ValueError(
                f"Solution schema version mismatch: {self.solution_schema_version}. "
                f"Expected {default_solution_schema_version}.",
            )
        return self


TSolutionConfig = TypeVar("TSolutionConfig", bound=SolutionConfiguration)


def get_default_solution_configuration(solution_configuration_type: type[TSolutionConfig]) -> TSolutionConfig:
    # placeholder until we decide on how to get the default solution configuration.
    return solution_configuration_type()
