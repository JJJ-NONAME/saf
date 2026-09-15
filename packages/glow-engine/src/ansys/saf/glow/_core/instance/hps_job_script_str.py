HPS_JOB_SCRIPT_CONTENT = """# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.

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

# type: ignore

import ipaddress
import os
import platform
import socket
import string
import tempfile
from urllib.parse import urlparse

from ansys.hps.client.jms import ProjectApi  # type: ignore
from ansys.rep.common.logging import log
from ansys.rep.evaluator.task_manager import ApplicationExecution

def _is_ip_literal(value: str) -> bool:
    '''Return True if value parses as an IPv4 or IPv6 address literal (not a hostname).'''
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True


def _is_advertisable(ip: str) -> bool:
    '''Return False for addresses no external caller can reach back on.

    Rejects loopback (127/8, ::1), link-local (169.254/16, fe80::/10),
    and unspecified (0.0.0.0) addresses using the ipaddress stdlib module
    for correct IPv4 and IPv6 handling. Non-IP-literal values (such as hostnames)
    are also rejected: callers should use _is_ip_literal first to distinguish
    "not an advertisable IP" from "not an IP at all".
    '''
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return not (addr.is_loopback or addr.is_link_local or addr.is_unspecified)


def _probe_route_to(host: str) -> str | None:
    '''Return the local address the OS would use to route toward host, if advertisable.

    Uses a UDP "connect" so the OS consults its routing table without sending any data
    on the wire - works even when host is unreachable. Returns None if the route can't
    be determined or the resulting local address isn't advertisable.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((host, 80))
        ip = s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()
    return ip if _is_advertisable(ip) else None


def detect_host_ip(target_host: str | None = None) -> str:
    '''Return a best-effort IPv4 address suitable for advertising to external callers.

    If GLOW_PRODUCT_HOST is set, it is returned verbatim (it may be an IP literal or a hostname).
    Avoids socket.gethostbyname(socket.gethostname()), which can return loopback addresses
    (127.x.x.x) on systems where the hostname maps to loopback in /etc/hosts.

    Resolution order:
    1. GLOW_PRODUCT_HOST environment variable (explicit override for NAT/overlay).
    2. UDP route probe toward target_host, if provided.
    3. UDP route probe toward 8.8.8.8 as a fallback public sink.
    4. First advertisable address from socket.getaddrinfo.
    5. Legacy socket.gethostbyname(socket.gethostname()) for compatibility.
    '''
    override = os.environ.get("GLOW_PRODUCT_HOST")
    if override:
        return override

    if target_host:
        ip = _probe_route_to(target_host)
        if ip:
            return ip

    ip = _probe_route_to("8.8.8.8")
    if ip:
        return ip

    try:
        for *_, sockaddr in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = sockaddr[0]
            if _is_advertisable(ip):
                return ip
    except OSError:
        pass

    return socket.gethostbyname(socket.gethostname())


class GlowInstanceExecution(ApplicationExecution):
    LOCALHOSTS = ["localhost", "127.0.0.1"]
    DEFAULT_GLOW_PRODUCT_BINDING_HOST = "0.0.0.0"  # To avoid breaking changes
    DEFAULT_GLOW_PRODUCT_BINDING_SECURE_HOST = "localhost"
    GLOW_PRODUCT_HOST = "GLOW_PRODUCT_HOST"
    GLOW_PRODUCT_BINDING_HOST = "GLOW_PRODUCT_BINDING_HOST"

    def _get_random_free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("", 0))
                return sock.getsockname()[1]
            except OSError as err:
                raise OSError("no free ports") from err

    def _generate_uds_dir(self, value: str, env: dict[str, str], task_id: str, port: int) -> tuple[str, str, str]:
        uds_dir = tempfile.gettempdir()
        uds_id = env.get("_GLOW_LINUX_UDS_ID", "glow-${TASK_ID}")
        uds_id = string.Template(uds_id).substitute({"TASK_ID": task_id, "PORT": str(port)})
        value = string.Template(value).substitute(
            {"UDS_DIR": str(uds_dir), "UDS_ID": str(uds_id)},
        )
        return uds_dir, uds_id, value

    def execute(self):
        log.info("Starting GLOW Instance execution script")

        log.info("context dump:")
        log.info(f"{self.context.software=}")
        log.info(f"{self.context.resource_requirements=}")
        log.info(f"{self.context.execution_context=}")
        log.info(f"{self.context.environment=}")
        log.info(f"{self.context.parameter_values=}")
        log.info(f"{self.context.input_files=}")
        log.info(f"{self.context.output_files=}")
        log.info(f"{self.context.task=}")

        app = self.context.software[0]
        exe = app["executable"]
        if " " in exe and not exe.startswith('"'):
            exe = f'"{exe}"'

        # Pass env vars correctly
        env = os.environ.copy()
        env.update(self.context.environment)

        project_api = ProjectApi(self.context.client, self.context.task["project_id"])
        task = project_api.get_tasks(id=self.context.task["task_id"], fields="all")[0]
        task_definition = project_api.get_task_definitions(id=self.context.task["task_definition_id"], fields="all")[0]

        hps_hostname = urlparse(self.context.client.url).hostname
        published_host = env.get(self.GLOW_PRODUCT_HOST) or detect_host_ip(hps_hostname)
        if _is_ip_literal(published_host) and not _is_advertisable(published_host):
            log.warning(
                f"The detected address for this product instance ('{published_host}') is a loopback, "
                "link-local, or unspecified address, so other machines will not be able to reach it. "
                "The Solution API may be unable to connect to the running instance. If this machine has "
                "multiple network interfaces or runs in a container, set the GLOW_PRODUCT_HOST environment "
                "variable to an address or hostname that other machines can use to reach it."
            )
        bind_host = env.get(
            self.GLOW_PRODUCT_BINDING_HOST,
            (
                self.DEFAULT_GLOW_PRODUCT_BINDING_HOST
                if "_GLOW_WINDOWS_LOCAL_SECURE_FLAGS" not in env  # any X_SECURE_FLAGS env var would work as indicator
                else self.DEFAULT_GLOW_PRODUCT_BINDING_SECURE_HOST
            ),
        )

        # TODO - we will probably need more than one port in the long term - here we're assuming there's only one
        # service
        # Here we are deliberately minimising the delay between getting the port number and using it to set the custom
        # data and start the command. This is to reduce the probability of a race condition. It isn't perfect: the
        # race is not eliminated another process could grab the port.
        port = self._get_random_free_port()

        secure_flags = ""
        uds_dir = ""
        uds_id = ""
        is_localhost = bind_host in self.LOCALHOSTS
        is_windows = platform.system() == "Windows"
        certs_dir = env.get("ANSYS_GRPC_CERTIFICATES", None)
        message_before_secure_flags = ""
        if is_localhost:
            if is_windows:
                secure_flags = env.get("_GLOW_WINDOWS_LOCAL_SECURE_FLAGS", "")
                message_before_secure_flags = "Secure flags found for local windows:"
            else:
                secure_flags = env.get("_GLOW_LINUX_LOCAL_SECURE_FLAGS", "")
                if "UDS_DIR" in secure_flags:
                    uds_dir, uds_id, secure_flags = self._generate_uds_dir(secure_flags, env, task.id, port)
                message_before_secure_flags = "Secure flags found for local linux:"
            if not secure_flags:
                secure_flags = env.get("_GLOW_INSECURE_FLAGS", "")
                message_before_secure_flags = "No secure flags found for localhost, falling back to"

        else:
            secure_flags = env.get("_GLOW_REMOTE_SECURE_FLAGS", "")
            if secure_flags:
                message_before_secure_flags = "Secure flags found for remote:"
            else:
                secure_flags = env.get("_GLOW_INSECURE_FLAGS", "")
                message_before_secure_flags = "No secure flags found for remote, falling back to"

        if "${CERTS_DIR}" in secure_flags or "mtls" in secure_flags:
            if certs_dir is None:
                secure_flags = env.get("_GLOW_INSECURE_FLAGS", "")
                message_before_secure_flags = (
                    "No grpc certificates found for "
                    + f"{'remote' if not is_localhost else 'localhost'}, falling back to"
                )
            else:
                secure_flags = string.Template(secure_flags).substitute({"CERTS_DIR": str(certs_dir)})

        log.info(f"{message_before_secure_flags} {secure_flags=}")
        # Replace the HOST and PORT template variables if present on the task's environment
        for key, value in task_definition.environment.items():
            if "PORT" in value:
                task_definition.environment[key] = string.Template(value).substitute({"PORT": str(port)})
            if "HOST" in value:
                task_definition.environment[key] = string.Template(value).substitute({"HOST": str(bind_host)})
            if "UDS_DIR" in value:
                uds_dir, uds_id, value = self._generate_uds_dir(value, env, task.id, port)
                task_definition.environment[key] = value
        env.update(task_definition.environment)

        cmd = string.Template(task_definition.execution_command).substitute(
            {
                "HOST": str(bind_host),
                "PORT": str(port),
                "EXECUTABLE": exe,
            },
        )
        cmd += " " + secure_flags if secure_flags else ""
        task.custom_data = {
            "port": port,
            "host": published_host,
            "secure_flags": secure_flags,
            "uds_dir": uds_dir,
            "uds_id": uds_id,
        }
        project_api.update_tasks([task])

        # Execute command
        log.info(f"subprocess.run {cmd=} {env=}")

        self.run_and_capture_output(cmd, shell=True, env=env)
"""
