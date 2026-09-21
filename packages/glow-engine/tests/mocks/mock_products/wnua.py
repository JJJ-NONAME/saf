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

# type: ignore
"""
Windows Named User Authentication (WNUA) for Python gRPC servers.
This module provides a server interceptor that authenticates clients
by verifying they run under the same Windows user account.
"""

from concurrent import futures
import ctypes
from ctypes import wintypes
import logging
from pathlib import Path
import re
import sys

import grpc

# Only available on Windows
if sys.platform != "win32":
    raise ImportError("WNUA (Windows Named User Authentication) is only supported on Windows")

logger = logging.getLogger(__name__)


class WNUAAuthenticator:
    """Windows Named User Authentication using FPN library.

    This class provides authentication functionality by interfacing with the
    FPN (Find Port Number) library to verify that gRPC clients are running
    under the same Windows user account as the server.
    """

    def __init__(self):
        """Initialize the WNUA authenticator with FPN library.

        Loads the FPN DLL and sets up function signatures for authentication.
        The DLL is searched in the following order:
        1. Bundled DLL in the package (libs/x64/fpn.dll or libs/x86/fpn.dll based on Python architecture)
        2. Build directory (for development)
        3. System PATH

        Raises
        ------
        RuntimeError
            If the FPN library cannot be loaded or accessed.
        """
        # Detect Python architecture
        package_dir = Path(__file__).parent
        bundled_dll_path = package_dir / "fpn.dll"

        try:
            # Try architecture-specific bundled DLL first (for packaged installations)
            if bundled_dll_path.exists():
                self.fpn_lib = ctypes.CDLL(str(bundled_dll_path))
            # Try fallback architecture if available
            else:
                # Fall back to searching in PATH
                self.fpn_lib = ctypes.CDLL("fpn.dll")
        except OSError as e:
            raise RuntimeError("Failed to load FPN library") from e

        # Define function signatures
        self.fpn_lib.fpn_remote_is_me.argtypes = [
            ctypes.c_ushort,  # port
            ctypes.POINTER(wintypes.DWORD),  # err_loc
            ctypes.POINTER(wintypes.DWORD),  # err_code
        ]
        self.fpn_lib.fpn_remote_is_me.restype = wintypes.BOOL

        self.fpn_lib.fpn_reduce_err_codes.argtypes = [
            ctypes.POINTER(wintypes.DWORD),  # err_loc
            ctypes.POINTER(wintypes.DWORD),  # err_code
        ]
        self.fpn_lib.fpn_reduce_err_codes.restype = wintypes.DWORD

        # Error constants (matching the C header)
        self.FPN_ERROR_PROCESS_PERMISSION = 1
        self.FPN_ERROR_NOT_ME = 2
        self.FPN_ERROR_NO_MATCH = 3

    def authenticate_client(self, context):
        """Authenticate a client by checking if they run under the same Windows user.

        Extracts the client's port number from the gRPC context and uses the FPN
        library to verify that the process using that port belongs to the same
        Windows user as the server process.

        Parameters
        ----------
        context : grpc.ServicerContext
            The gRPC service context containing client connection information.

        Returns
        -------
        tuple[bool, str]
            A tuple of (success, error_message). If success is True, error_message is empty.
            If success is False, error_message contains the reason for failure.
        """
        peer = context.peer()
        logger.info(f"WNUA: Client peer: {peer}")

        # Extract host and port from peer string (format like "ipv4:127.0.0.1:12345" or "ipv6:[::1]:12345")
        # First verify that the connection is coming from localhost (IPv4 or IPv6)
        if not (
            peer.startswith("ipv4:127.0.0.1:") or peer.startswith("ipv4:localhost:") or peer.startswith("ipv6:[::1]:")
        ):
            logger.error(f"WNUA: Connection rejected - not from localhost. Peer: {peer}")
            return False, "WNUA authentication only allowed from localhost (127.0.0.1 or ::1)"

        # Extract port from peer string
        match = re.search(r":(\d+)$", peer)
        if not match:
            logger.error("WNUA: Could not extract port from peer info")
            return False, "Authentication system error"

        try:
            client_port = int(match.group(1))
            logger.info(f"WNUA: Client port: {client_port}")

            # Call FPN library to check if the client port belongs to the same user
            err_loc = wintypes.DWORD()
            err_code = wintypes.DWORD()

            is_same_user = self.fpn_lib.fpn_remote_is_me(
                ctypes.c_ushort(client_port),
                ctypes.byref(err_loc),
                ctypes.byref(err_code),
            )

            if is_same_user:
                logger.info("WNUA: Client is same Windows user - ACCESS GRANTED")
                # Add authentication metadata
                context.set_trailing_metadata(
                    [
                        ("wnua-authenticated", "true"),
                        ("wnua-user-verified", "same-user"),
                    ],
                )
                return True, ""
            else:
                logger.error("WNUA: Client is NOT same Windows user - ACCESS DENIED")
                reduced_error = self.fpn_lib.fpn_reduce_err_codes(
                    ctypes.byref(err_loc),
                    ctypes.byref(err_code),
                )

                error_msg = "Authentication failed"
                if reduced_error == self.FPN_ERROR_PROCESS_PERMISSION:
                    error_msg = "Permission denied to check process"
                elif reduced_error == self.FPN_ERROR_NOT_ME:
                    error_msg = "Client is not the same Windows user"
                elif reduced_error == self.FPN_ERROR_NO_MATCH:
                    error_msg = "No process found using client port"
                else:
                    error_msg = f"Authentication error (loc: {err_loc.value}, code: {err_code.value})"

                return False, error_msg

        except Exception as e:
            # This is a real error during authentication
            logger.error(f"WNUA: Error during authentication: {e}")
            return False, "Authentication system error"


class WNUAServerInterceptor(grpc.ServerInterceptor):
    """gRPC server interceptor that enforces Windows Named User Authentication.

    This interceptor wraps all incoming RPC calls and applies WNUA authentication
    by checking that the client process runs under the same Windows user as the
    server process. Uses the FPN library to determine port ownership.

    Attributes
    ----------
    authenticator : WNUAAuthenticator
        The authenticator instance used to verify client credentials.
    """

    def __init__(self):
        """Initialize the WNUA interceptor.

        Creates a new WNUAAuthenticator instance for handling client authentication.

        Raises
        ------
        RuntimeError
            If the FPN library cannot be loaded.
        """
        self.authenticator = WNUAAuthenticator()

    def intercept_service(self, continuation, handler_call_details):
        """Intercept service calls to apply WNUA authentication.

        This method is called for each service handler registration. It wraps
        the original service handler with authentication logic that verifies
        the client's Windows user identity before allowing RPC execution.

        Supports all gRPC call patterns:
        - Unary-Unary: Single request → Single response
        - Unary-Stream: Single request → Stream of responses
        - Stream-Unary: Stream of requests → Single response
        - Stream-Stream: Stream of requests → Stream of responses

        Parameters
        ----------
        continuation : callable
            Function to get the original service handler.
        handler_call_details : grpc.HandlerCallDetails
            Details about the service call being intercepted.

        Returns
        -------
        grpc.RpcMethodHandler or None
            Modified handler with authentication wrapper for the appropriate
            call pattern, or None if no handler exists.
        """

        # Get the original handler from the continuation
        original_handler = continuation(handler_call_details)

        if original_handler is None:
            return None

        # Generic authentication wrapper that works for all call patterns
        def create_authenticated_wrapper(original_method):
            """Create an authenticated wrapper for any handler method."""

            def wrapper(*args):
                # The context is always the last argument
                context = args[-1]
                success, error_message = self.authenticator.authenticate_client(context)
                if not success:
                    # Authentication failed, abort the RPC
                    if "system error" in error_message.lower():
                        context.abort(grpc.StatusCode.INTERNAL, error_message)
                    else:
                        context.abort(grpc.StatusCode.UNAUTHENTICATED, error_message)
                    return  # This line won't be reached due to abort exception
                return original_method(*args)

            return wrapper

        # Handler type mapping: (attribute_name, handler_constructor)
        handler_types = [
            ("unary_unary", grpc.unary_unary_rpc_method_handler),
            ("unary_stream", grpc.unary_stream_rpc_method_handler),
            ("stream_unary", grpc.stream_unary_rpc_method_handler),
            ("stream_stream", grpc.stream_stream_rpc_method_handler),
        ]

        # Find the active handler type and wrap it
        for attr_name, handler_constructor in handler_types:
            original_method = getattr(original_handler, attr_name)
            if original_method is not None:
                authenticated_method = create_authenticated_wrapper(original_method)
                return handler_constructor(
                    authenticated_method,
                    request_deserializer=original_handler.request_deserializer,
                    response_serializer=original_handler.response_serializer,
                )

        # Unknown handler type, return as-is
        return original_handler


def create_wnua_server(max_workers=10):
    """Create a gRPC server with Windows Named User Authentication enabled.

    Creates a new gRPC server instance configured with the WNUA interceptor
    that enforces same-user authentication for all incoming RPC calls. This
    function is only supported on Windows platforms.

    Parameters
    ----------
    max_workers : int, optional
        Maximum number of worker threads in the server's thread pool, by default 10.

    Returns
    -------
    grpc.Server
        Configured gRPC server instance with WNUA interceptor enabled.
    """
    # Create server with WNUA interceptor
    interceptors = [WNUAServerInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        interceptors=interceptors,
    )

    return server
