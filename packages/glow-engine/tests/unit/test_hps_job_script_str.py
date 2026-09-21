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

"""Tests for the host-detection helpers embedded in ``HPS_JOB_SCRIPT_CONTENT``.

``HPS_JOB_SCRIPT_CONTENT`` is a script template that gets uploaded to HPS and executed by the
HPS evaluator on the remote worker. It imports ``ansys.hps.client.jms`` and ``ansys.rep.*``
modules that are only available in that remote runtime, so the template as a whole cannot be
imported or executed in this test environment. The ``_is_advertisable``/``detect_host_ip``
helper functions only depend on the standard library though, so we extract just those function
definitions from the template source via `ast` and execute them in an isolated namespace, letting
us unit test the actual production source instead of a copy/paste duplicate of the logic.
"""

import ast
import ipaddress
import os
import socket
from typing import Any

import pytest

from ansys.saf.glow._core.instance.hps_job_script_str import HPS_JOB_SCRIPT_CONTENT

_FUNCTION_NAMES = ("_is_ip_literal", "_is_advertisable", "_probe_route_to", "detect_host_ip")


def _extract_job_script_functions() -> dict[str, Any]:
    tree = ast.parse(HPS_JOB_SCRIPT_CONTENT)
    nodes: list[ast.stmt] = [
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in _FUNCTION_NAMES
    ]
    assert len(nodes) == len(_FUNCTION_NAMES), (
        f"Expected to find {_FUNCTION_NAMES} as top-level functions in HPS_JOB_SCRIPT_CONTENT"
    )
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace: dict[str, Any] = {"ipaddress": ipaddress, "os": os, "socket": socket}
    exec(compile(module, filename="<HPS_JOB_SCRIPT_CONTENT>", mode="exec"), namespace)
    return namespace


@pytest.fixture
def job_script_functions() -> dict[str, Any]:
    return _extract_job_script_functions()


class _FakeSocket:
    def __init__(self, sockname: str, raise_on_connect: bool = False) -> None:
        self._sockname = sockname
        self._raise_on_connect = raise_on_connect
        self.closed = False

    def connect(self, address: tuple[str, int]) -> None:
        if self._raise_on_connect:
            raise OSError("network is unreachable")

    def getsockname(self) -> tuple[str, int]:
        return (self._sockname, 0)

    def close(self) -> None:
        self.closed = True


@pytest.mark.parametrize(
    ("ip", "expected"),
    [
        ("127.0.0.1", False),
        ("127.5.6.7", False),
        ("::1", False),
        ("169.254.1.1", False),
        ("fe80::1", False),
        ("0.0.0.0", False),
        ("192.168.1.10", True),
        ("8.8.8.8", True),
        ("2001:4860:4860::8888", True),
        ("not-an-ip-address", False),
        ("", False),
    ],
)
def test_is_advertisable(job_script_functions: dict[str, Any], ip: str, expected: bool) -> None:
    assert job_script_functions["_is_advertisable"](ip) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("127.0.0.1", True),
        ("192.168.1.10", True),
        ("::1", True),
        ("hps.example.com", False),
        ("my-custom-host", False),
        ("", False),
    ],
)
def test_is_ip_literal(job_script_functions: dict[str, Any], value: str, expected: bool) -> None:
    assert job_script_functions["_is_ip_literal"](value) is expected


def test_detect_host_ip_uses_glow_product_host_env_override(
    monkeypatch: pytest.MonkeyPatch,
    job_script_functions: dict[str, Any],
) -> None:
    def _fail_if_called(*args: object, **kwargs: object) -> _FakeSocket:
        pytest.fail("socket.socket should not be called when GLOW_PRODUCT_HOST is set")

    monkeypatch.setenv("GLOW_PRODUCT_HOST", "my-custom-host")
    monkeypatch.setattr(socket, "socket", _fail_if_called)

    assert job_script_functions["detect_host_ip"]("hps.example.com") == "my-custom-host"


def test_detect_host_ip_uses_route_probe_toward_target_host(
    monkeypatch: pytest.MonkeyPatch,
    job_script_functions: dict[str, Any],
) -> None:
    def _socket_factory(*args: object, **kwargs: object) -> _FakeSocket:
        return _FakeSocket("10.0.0.5")

    monkeypatch.delenv("GLOW_PRODUCT_HOST", raising=False)
    monkeypatch.setattr(socket, "socket", _socket_factory)

    assert job_script_functions["detect_host_ip"]("hps.example.com") == "10.0.0.5"


def test_detect_host_ip_falls_back_to_public_probe_when_target_unreachable(
    monkeypatch: pytest.MonkeyPatch,
    job_script_functions: dict[str, Any],
) -> None:
    monkeypatch.delenv("GLOW_PRODUCT_HOST", raising=False)
    attempts: list[str] = []

    def fake_socket_factory(*args: object, **kwargs: object) -> _FakeSocket:
        # The first probe (toward target_host) is unreachable; the fallback probe (8.8.8.8) succeeds.
        attempts.append("probe")
        return _FakeSocket("203.0.113.9", raise_on_connect=len(attempts) == 1)

    monkeypatch.setattr(socket, "socket", fake_socket_factory)

    assert job_script_functions["detect_host_ip"]("unreachable-host") == "203.0.113.9"
    assert len(attempts) == 2


def test_detect_host_ip_falls_back_to_getaddrinfo_when_probes_non_advertisable(
    monkeypatch: pytest.MonkeyPatch,
    job_script_functions: dict[str, Any],
) -> None:
    def _socket_factory(*args: object, **kwargs: object) -> _FakeSocket:
        return _FakeSocket("127.0.0.1")

    def _getaddrinfo(
        *args: object,
        **kwargs: object,
    ) -> list[tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int]]]:
        return [(socket.AF_INET, socket.SOCK_DGRAM, 0, "", ("192.168.50.2", 0))]

    monkeypatch.delenv("GLOW_PRODUCT_HOST", raising=False)
    monkeypatch.setattr(socket, "socket", _socket_factory)
    monkeypatch.setattr(socket, "getaddrinfo", _getaddrinfo)

    assert job_script_functions["detect_host_ip"](None) == "192.168.50.2"


def test_detect_host_ip_final_fallback_to_gethostbyname(
    monkeypatch: pytest.MonkeyPatch,
    job_script_functions: dict[str, Any],
) -> None:
    def _socket_factory(*args: object, **kwargs: object) -> _FakeSocket:
        return _FakeSocket("", raise_on_connect=True)

    def _raise_os_error(
        *args: object,
        **kwargs: object,
    ) -> list[tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int]]]:
        raise OSError("no dns resolution available")

    def _gethostname() -> str:
        return "myhost"

    def _gethostbyname(name: str) -> str:
        return "10.10.10.10"

    monkeypatch.delenv("GLOW_PRODUCT_HOST", raising=False)
    monkeypatch.setattr(socket, "socket", _socket_factory)
    monkeypatch.setattr(socket, "getaddrinfo", _raise_os_error)
    monkeypatch.setattr(socket, "gethostname", _gethostname)
    monkeypatch.setattr(socket, "gethostbyname", _gethostbyname)

    assert job_script_functions["detect_host_ip"]("target-host") == "10.10.10.10"
