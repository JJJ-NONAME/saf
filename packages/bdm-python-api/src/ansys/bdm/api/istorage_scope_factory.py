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

from typing import Protocol

from ansys.bdm.api.iasync_storage_scope import (
    IAsyncReadStorageScope,
    IAsyncStorageScope,
)
from ansys.bdm.api.istorage_scope import IReadStorageScope, IStorageScope


class IReadStorageScopeFactory(Protocol):
    """
    Factory pattern for creating instances of IReadStorageScope and IAsyncReadStorageScope.
    """

    def create_storage_scope(
        self,
        context: str,
        template_vars: dict[str, str],
    ) -> IReadStorageScope:
        """
        Create a new read only storage scope.

        Parameters
        ----------
        context: str
            TODO: How to word what this genericaly does.
        template_vars: Dict[str, str]
            Template variables that may be used by the configuration system \
            to return an appropriate :class:`IStorageScope`. TODO: Define whether certain fields \
            need to be passed in?

        Returns
        -------
        IReadStorageScope
            A configured and ready to use :class:`IReadStorageScope`
        """
        # deliberately not implemented
        ...

    async def create_async_storage_scope(
        self,
        context: str,
        template_vars: dict[str, str],
    ) -> IAsyncReadStorageScope:
        """
        Create a new asynchronous read only storage scope.

        Parameters
        ----------
        context: str
            TODO: How to word what this genericaly does.
        template_vars: Dict[str, str]
            Template variables that may be used by the configuration system \
            to return an appropriate :class:`IAsyncStorageScope`. TODO: Define whether certain fields \
            need to be passed in?

        Returns
        -------
        IAsyncReadStorageScope
            A configured and ready to use :class:`IAsyncReadStorageScope`
        """
        # deliberately not implemented
        ...


class IStorageScopeFactory(IReadStorageScopeFactory, Protocol):
    """
    Factory pattern for creating instances of IStorageScope and IAsyncStorageScope.
    """

    def create_storage_scope(
        self,
        context: str,
        template_vars: dict[str, str],
    ) -> IStorageScope:
        """
        Create a new storage scope.

        Parameters
        ----------
        context: str
            TODO: How to word what this genericaly does.
        template_vars: Dict[str, str]
            Template variables that may be used by the configuration system \
            to return an appropriate :class:`IStorageScope`. TODO: Define whether certain fields \
            need to be passed in?

        Returns
        -------
        IStorageScope
            A configured and ready to use :class:`IStorageScope`
        """
        # deliberately not implemented
        ...

    async def create_async_storage_scope(
        self,
        context: str,
        template_vars: dict[str, str],
    ) -> IAsyncStorageScope:
        """
        Create a new asynchronous storage scope.

        Parameters
        ----------
        context: str
            TODO: How to word what this genericaly does.
        template_vars: Dict[str, str]
            Template variables that may be used by the configuration system \
            to return an appropriate :class:`IAsyncStorageScope`. TODO: Define whether certain fields \
            need to be passed in?

        Returns
        -------
        IAsyncStorageScope
            A configured and ready to use :class:`IAsyncStorageScope`
        """
        # deliberately not implemented
        ...
