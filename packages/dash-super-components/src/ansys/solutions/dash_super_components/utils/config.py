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


"""Package-wide configuration for Super Components for Dash.

Call :func:`configure` in your ``app.py`` before building the layout to
change settings from their defaults.
"""

_DEFAULT_NOTIFICATION_CONTAINER_ID = "notification-container"
_DEFAULT_ENABLE_BETA_FEATURES = False


class _Config:
    """Holds package-wide configuration settings for Super Components for Dash."""

    def __init__(self) -> None:
        self.notification_container_id: str = _DEFAULT_NOTIFICATION_CONTAINER_ID
        """The ``id`` of the ``dmc.NotificationContainer`` that this library
        targets when dispatching notifications.

        Default value: ``"notification-container"``
        """

        self.enable_beta_features: bool = _DEFAULT_ENABLE_BETA_FEATURES
        """Whether beta features are enabled.

        Bootstrap mode is a beta feature and is disabled by default. Applications
        that want to use ``FolderSelectorMode.BOOTSTRAP`` must opt in by calling
        :func:`configure` with ``enable_beta_features=True``.

        Default value: ``False``
        """


_config = _Config()


def configure(
    *,
    notification_container_id: str | None = None,
    enable_beta_features: bool | None = None,
) -> None:
    """Configure Super Components for Dash settings at runtime.

    Call this function in your ``app.py`` *before* building the layout so
    that components use the updated settings when their callbacks fire.

    Parameters
    ----------
    notification_container_id : str, optional
        The ``id`` of the ``dmc.NotificationContainer`` in your application
        layout.  Components that show notifications (such as
        :class:`~ansys.solutions.dash_super_components.FolderSelector`) will
        forward their messages to the container with this ID.
    enable_beta_features : bool, optional
        Whether to enable beta features.
        When ``False`` (default), beta features are disabled.

    Examples
    --------
    .. code-block:: python

        # app.py
        import ansys.solutions.dash_super_components as dsc

        dsc.configure(
            notification_container_id="my-notifications",
            enable_beta_features=True,
        )

        import dash_mantine_components as dmc

        app.layout = dmc.MantineProvider(
            children=[
                dmc.NotificationContainer(
                    id="my-notifications",
                    position="bottom-center",
                ),
                # ... rest of the layout
            ]
        )
    """
    if notification_container_id is not None:
        _config.notification_container_id = notification_container_id

    if enable_beta_features is not None:
        _config.enable_beta_features = enable_beta_features
