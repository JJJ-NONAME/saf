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


"""Unit tests for the utils.config module."""

import pytest

from ansys.solutions.dash_super_components.utils import config as dsc_config

_DEFAULT_ID = "notification-container"
_DEFAULT_ENABLE_BETA_FEATURES = False


@pytest.fixture(autouse=True)
def reset_config():
    """Reset notification_container_id to the default before and after each test."""
    dsc_config._config.notification_container_id = _DEFAULT_ID
    dsc_config._config.enable_beta_features = _DEFAULT_ENABLE_BETA_FEATURES
    yield
    dsc_config._config.notification_container_id = _DEFAULT_ID
    dsc_config._config.enable_beta_features = _DEFAULT_ENABLE_BETA_FEATURES


def test_default_notification_container_id():
    """_config.notification_container_id defaults to 'notification-container'."""
    assert dsc_config._config.notification_container_id == _DEFAULT_ID


def test_notification_container_id_is_string():
    """_config.notification_container_id is a str."""
    assert isinstance(dsc_config._config.notification_container_id, str)


def test_default_folder_selector_bootstrap_beta_flag_disabled():
    """FolderSelector bootstrap beta flag defaults to False."""
    assert dsc_config._config.enable_beta_features is False


def test_configure_sets_notification_container_id():
    """configure() updates _config.notification_container_id."""
    import ansys.solutions.dash_super_components as dsc

    dsc.configure(notification_container_id="my-notifications")
    assert dsc_config._config.notification_container_id == "my-notifications"


def test_configure_sets_folder_selector_bootstrap_beta_flag():
    """configure() updates _config.enable_beta_features."""
    import ansys.solutions.dash_super_components as dsc

    dsc.configure(enable_beta_features=True)
    assert dsc_config._config.enable_beta_features is True

    dsc.configure(enable_beta_features=False)
    assert dsc_config._config.enable_beta_features is False


def test_configure_updates_individual_values_without_clobbering_others():
    """configure() updates only explicitly provided values."""
    import ansys.solutions.dash_super_components as dsc

    dsc.configure(notification_container_id="my-notifications")
    assert dsc_config._config.notification_container_id == "my-notifications"
    assert dsc_config._config.enable_beta_features is False

    dsc.configure(enable_beta_features=True)
    assert dsc_config._config.notification_container_id == "my-notifications"
    assert dsc_config._config.enable_beta_features is True


def test_configure_requires_keyword_argument():
    """configure() only accepts notification_container_id as a keyword argument."""
    import ansys.solutions.dash_super_components as dsc

    with pytest.raises(TypeError):
        dsc.configure("my-notifications")  # type: ignore[call-arg]


def test_configure_exported_from_package():
    """Configure is accessible from the top-level package."""
    import ansys.solutions.dash_super_components as dsc

    assert hasattr(dsc, "configure")
    assert callable(dsc.configure)
