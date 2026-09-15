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

import httpx2


class SolutionClientError(Exception):
    """Base class for all solution exceptions."""


class BadRequestException(SolutionClientError):  # noqa: N818
    """Exception raised when the GLOW client API is used incorrectly."""


class NotFoundException(SolutionClientError):  # noqa: N818
    """Exception raised when the GLOW client API is invoked to access an
    object that does not exist."""


class ConflictException(SolutionClientError):  # noqa: N818
    """Exception raised when the GLOW client API is invoked making a request
    inconsistent with a given project state."""


class PermissionException(SolutionClientError):  # noqa: N818
    """Exception raised when the GLOW client API is invoked to trigger an
    operation that the user does not have permission to perform."""


class UnauthorizedException(SolutionClientError):  # noqa: N818
    """Exception raised when the GLOW client API is invoked to trigger an
    operation that the user does not have authorization to perform."""


class InternalSolutionException(SolutionClientError):  # noqa: N818
    """Exception raised when the solution experienced a problem server-side."""


CLIENT_EXCEPTIONS_BY_CODE: dict[int, type[Exception]] = {
    400: BadRequestException,
    401: UnauthorizedException,
    403: PermissionException,
    404: NotFoundException,
    405: BadRequestException,
    409: ConflictException,
    422: BadRequestException,
    500: InternalSolutionException,
}

CLIENT_EXCEPTIONS_BY_GRAPHQL_STATUS: dict[str, type[Exception]] = {
    "BAD_REQUEST": BadRequestException,
    "NOT_FOUND": NotFoundException,
    "CONFLICT": ConflictException,
    "PERMISSION_DENIED": PermissionException,
    "UNAUTHORIZED": UnauthorizedException,
    "INTERNAL_SERVER_ERROR": InternalSolutionException,
}


def _get_message(r: httpx2.Response, raw: str) -> str:
    try:
        return r.json()["detail"]
    except Exception:
        raise RuntimeError(raw) from None


def raise_for_status(status_code: int, message: str):
    if status_code // 100 == 2:
        return
    exception = CLIENT_EXCEPTIONS_BY_CODE.get(status_code)
    if exception is None:
        raise RuntimeError(message)
    raise exception(message)


def raise_for_graphql_status(result: dict[str, str]):
    status = result["status"]
    if status == "SUCCESS":
        return

    exception = CLIENT_EXCEPTIONS_BY_GRAPHQL_STATUS.get(status)
    message = result.get("error")
    if exception is None:
        raise RuntimeError(message)
    raise exception(message)


def check(r: httpx2.Response) -> None:
    if r.status_code // 100 == 2:
        return
    message = _get_message(r, r.text)
    raise_for_status(r.status_code, message)
