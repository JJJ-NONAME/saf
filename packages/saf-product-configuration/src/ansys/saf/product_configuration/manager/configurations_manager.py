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

import inspect
import logging
from pathlib import Path

from ansys.saf.product_configuration._utils.code import load_python_file
from ansys.saf.product_configuration.aedt import AedtInstanceConfiguration
from ansys.saf.product_configuration.fluent import (
    Fluent2DDPSolverInstanceConfiguration,
    Fluent3DDPMeshingInstanceConfiguration,
    Fluent3DDPSolverInstanceConfiguration,
)
from ansys.saf.product_configuration.geometry import GeometryInstanceConfiguration
from ansys.saf.product_configuration.interfaces import (
    IProductInstanceConfiguration,
    IProductInstanceVersionConfiguration,
)
from ansys.saf.product_configuration.mapdl import MapdlInstanceConfiguration
from ansys.saf.product_configuration.mechanical import MechanicalInstanceConfiguration
from ansys.saf.product_configuration.optislang_wrapper import (
    OptislangWrapperInstanceConfiguration,
)
from ansys.saf.product_configuration.visor import VisorInstanceConfiguration

logger = logging.getLogger(__name__)


class ProductInstanceConfigurationsManager:
    """Manage the default and custom product instance configurations."""

    def __init__(self) -> None:
        # TODO: reuse _list_built_in_product_configs to avoid hardcoding the built-in configs here.
        self._configurations: list[IProductInstanceConfiguration] = [
            AedtInstanceConfiguration(),
            MechanicalInstanceConfiguration(),
            Fluent3DDPSolverInstanceConfiguration(),
            Fluent2DDPSolverInstanceConfiguration(),
            Fluent3DDPMeshingInstanceConfiguration(),
            MapdlInstanceConfiguration(),
            GeometryInstanceConfiguration(),
            OptislangWrapperInstanceConfiguration(),
            VisorInstanceConfiguration(),
        ]
        self._configurations_loaded = False

    def load_configurations(self, product_instance_configs_dir: Path | None):
        """Load the product instance configurations found in the specified directory."""
        if not product_instance_configs_dir or self._configurations_loaded:
            return
        for file_path in product_instance_configs_dir.iterdir():
            if file_path.suffix not in [".py", ".pyc"]:
                continue
            logger.info(f"Found python file that may contain product instance configurations: {file_path}.")
            # NOTE: would be safer to check subclasses without loading the file and do it later
            # only if it contains what we are looking for.
            module = load_python_file(file_path)
            for identifier, value in inspect.getmembers(
                module,
                lambda x: inspect.isclass(x) and self._inherits_from_protocol(x, IProductInstanceConfiguration),
            ):
                # Check if we already have a configuration with the same product_name
                # Create a temporary instance to check the product name
                config = value()
                if any(loaded_config.product_name == config.product_name for loaded_config in self._configurations):
                    logger.info(f"Instance configuration {identifier} already loaded, skipping.")
                    continue
                self._configurations.append(config)
                logger.info(f"Added instance configuration: {identifier}.")

        # cheap way of not adding things twice
        self._configurations_loaded = True

    def _inherits_from_protocol(self, cls: type, protocol: type) -> bool:
        if cls == protocol:
            return False
        # Can't use issubclass for Protocol-based classes, so check inheritance hierarchy manually using method
        # resolution order.
        # Can't use __bases__ neither. It only covers direct parents, leaving out classes that inherit and modify an
        # existing configuration.
        return protocol in getattr(cls, "__mro__", [])

    def list_versions(self, product_name: str) -> list[str]:
        """List all versions configured for the given product name.

        Parameters
        ----------
        product_name : str
            The name of the product.
        """
        return [
            version
            for definition in self._configurations
            for version in definition.versions
            if definition.product_name == product_name
        ]

    def list_configurations(self) -> list[IProductInstanceConfiguration]:
        """List all available product instance configurations."""
        return self._configurations

    def get_version_configuration(
        self,
        product_name: str,
        product_version: str | None = None,
    ) -> tuple[str, IProductInstanceVersionConfiguration]:
        """Get the product instance configuration for the specified product and version.

        Note: if product_version is None, returns the latest version configuration.
        """
        matching_configs = [product for product in self._configurations if product.product_name == product_name]

        if not matching_configs:
            raise RuntimeError(f"No configuration matches product {product_name}")
        if len(matching_configs) != 1:
            raise RuntimeError(f"More than one configuration matches product {product_name}")

        config = matching_configs[0]
        product_version = sorted(config.versions)[-1] if product_version is None else product_version
        return (product_version, config.get_version_configuration(product_version))

    def get_products(self) -> list[str]:
        """List all available products."""
        return [product.product_name for product in self._configurations]
