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

"""Unit tests for API requests module."""

import json
from unittest.mock import Mock, patch

import pytest
import requests

from ansys.solutions.dash_super_components.utils.api_requests import GlowAPIRequest


def test_get_transaction_method_status_success():
    """Test successful retrieval of transaction method status."""
    # Setup
    mock_response = Mock()
    mock_response.ok = True
    mock_response.content = json.dumps({"status": "completed"}).encode()

    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")

        # Execute
        status = api_request.get_transaction_method_status("step1", "method1")

    # Assert
    assert status == "completed"
    mock_get.assert_called_once_with(
        "https://api.example.com/steps/step1:method1",
        headers={"accept": "application/json"},
        timeout=10,
    )


@pytest.mark.parametrize("status", ["pending", "running", "completed", "failed", "cancelled"])
def test_get_transaction_method_status_different_statuses(status: str):
    """Test retrieval of different status values."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.content = json.dumps({"status": status}).encode()

    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")
        retrieved_status = api_request.get_transaction_method_status("step1", "method1")

    assert retrieved_status == status


def test_get_transaction_method_status_response_not_ok():
    """Test that exception is raised when response is not ok."""
    mock_response = Mock()
    mock_response.ok = False
    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")

        with pytest.raises(Exception, match="Failed to get the response"):
            api_request.get_transaction_method_status("step1", "method1")


def test_get_transaction_method_status_json_parsing():
    """Test that response content is correctly parsed as JSON."""
    response_data = {"status": "running", "progress": 50, "message": "Processing"}
    mock_response = Mock()
    mock_response.ok = True
    mock_response.content = json.dumps(response_data).encode()
    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")
        status = api_request.get_transaction_method_status("step1", "method1")

    # Should only return the status field
    assert status == "running"


def test_get_transaction_method_status_empty_status():
    """Test handling of empty status in response."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.content = json.dumps({"status": ""}).encode()
    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")
        status = api_request.get_transaction_method_status("step1", "method1")

    assert status == ""


def test_get_transaction_method_status_underscore_to_hyphen_conversion():
    """Test that underscores in step and method names are converted to hyphens."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.content = json.dumps({"status": "completed"}).encode()

    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")
        api_request.get_transaction_method_status("my_step", "my_method")

    mock_get.assert_called_once_with(
        "https://api.example.com/steps/my-step:my-method",
        headers={"accept": "application/json"},
        timeout=10,
    )


def test_get_transaction_method_status_hyphens_work_as_expected():
    """Test that hyphens in step and method names are preserved."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.content = json.dumps({"status": "completed"}).encode()

    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")
        api_request.get_transaction_method_status("my-step", "my-method")

    mock_get.assert_called_once_with(
        "https://api.example.com/steps/my-step:my-method",
        headers={"accept": "application/json"},
        timeout=10,
    )


def test_get_transaction_method_status_different_steps_and_methods():
    """Test calling with different step and method names (plain Python names with underscores)."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.content = json.dumps({"status": "completed"}).encode()
    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")

        api_request.get_transaction_method_status("step_a", "method_x")
        api_request.get_transaction_method_status("step_b", "method_y")

        assert mock_get.call_count == 2

        # Check first call — underscores are converted to hyphens
        first_call = mock_get.call_args_list[0]
        assert first_call[0][0] == "https://api.example.com/steps/step-a:method-x"

        # Check second call
        second_call = mock_get.call_args_list[1]
        assert second_call[0][0] == "https://api.example.com/steps/step-b:method-y"


def test_get_transaction_method_status_connection_error():
    """Test handling of connection errors."""
    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        api_request = GlowAPIRequest("https://api.example.com")

        with pytest.raises(requests.ConnectionError):
            api_request.get_transaction_method_status("step1", "method1")


def test_get_transaction_method_status_invalid_json():
    """Test handling of invalid JSON in response."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.content = b"Not valid JSON"
    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")

        with pytest.raises(json.JSONDecodeError):
            api_request.get_transaction_method_status("step1", "method1")


def test_get_transaction_method_status_missing_status_key():
    """Test handling when 'status' key is missing from response."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.content = json.dumps({"message": "Success", "data": {}}).encode()
    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")

        with pytest.raises(KeyError):
            api_request.get_transaction_method_status("step1", "method1")


def test_get_transaction_method_status_numeric_status():
    """Test handling of numeric status value."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.content = json.dumps({"status": 200}).encode()
    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")
        status = api_request.get_transaction_method_status("step1", "method1")

    assert status == 200


def test_get_transaction_method_status_null_status():
    """Test handling of null status value."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.content = json.dumps({"status": None}).encode()
    with patch("ansys.solutions.dash_super_components.utils.api_requests.requests.get") as mock_get:
        mock_get.return_value = mock_response

        api_request = GlowAPIRequest("https://api.example.com")
        status = api_request.get_transaction_method_status("step1", "method1")

    assert status is None
