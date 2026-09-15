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

import http.server
import json
import logging
import socketserver
import webbrowser

import httpx2
from joserfc import jws, jwt
from joserfc.errors import ExpiredTokenError
from pydantic import BaseModel
from requests_oauthlib import OAuth2Session  # pyright: ignore[reportUnknownVariableType]

from ansys.saf.glow._utilities.ip_utilities import get_random_free_port

logger = logging.getLogger(__name__)


class HpsConfig(BaseModel):
    base_auth_url: str
    client_id: str
    scope: str
    discovery_endpoint: str
    authorization_endpoint: str
    token_endpoint: str
    issuer: str


class HpsInteractiveAuthenticator:
    @classmethod
    def _interactive_authentication(
        cls,
        client_id: str,
        authorization_url: str,
        token_url: str,
        scopes: list[str],
    ) -> tuple[str, str]:
        class AuthorizationCodeHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                query = self.path.split("?", 1)[-1]
                params = dict(qc.split("=") for qc in query.split("&"))
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Authorization successful! You can close this tab.")

                if "code" in params:
                    auth_code = params["code"]
                    token = oauth.fetch_token(  # pyright: ignore[reportUnknownMemberType]
                        token_url,
                        verify=False,
                        code=auth_code,
                    )
                    self.server.access_token = token.get("access_token")  # pyright: ignore[reportAttributeAccessIssue]
                    self.server.refresh_token = token.get(  # pyright: ignore[reportAttributeAccessIssue]
                        "refresh_token",
                    )
                else:
                    self.server.access_token = None  # pyright: ignore[reportAttributeAccessIssue]
                    self.server.refresh_token = None  # pyright: ignore[reportAttributeAccessIssue]

        # In order for the redirect URI to be accepted, we need to add it under
        # https://localhost:8443/hps/auth/ (Keycloak).
        # Select the "rep" realm -> Clients -> rep-jms-web client -> Settings -> Valid Redirect URIs
        # and add http://localhost:*
        port = get_random_free_port()
        redirect_uri = f"http://localhost:{port}/callback"
        oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=scopes)
        authorization_url, _ = oauth.authorization_url(  # pyright: ignore[reportUnknownMemberType]
            url=authorization_url,
        )

        # Start the HTTP server to listen for the redirect
        # We need to use localhost instead of 127.0.0.1, seems like the web browser blocks cookies that come
        # from an insecure context, such as 127.0.0.1 (even if allowing cookies from that address), but with localhost
        # works fine
        access_token = ""
        refresh_token = ""
        with socketserver.TCPServer(("localhost", port), AuthorizationCodeHandler) as httpd:
            logger.info(f"Opening the browser for authorization...{authorization_url}")
            webbrowser.open(authorization_url)
            logger.info("Waiting for the authorization response...")
            httpd.timeout = 180
            httpd.handle_request()
            if not getattr(httpd, "access_token", None):
                raise RuntimeError("Authorization failed or cancelled by the user.")
            access_token = str(httpd.access_token)  # type: ignore
            refresh_token = str(httpd.refresh_token)  # type: ignore

        return access_token, refresh_token

    @classmethod
    def _get_hps_auth_urls(cls, hps_server_url: str) -> tuple[str, str]:
        # Setting it to 127.0.0.1 doesn't play well with browser cookies
        # when switching from 127.0.0.1 to localhost cookies are not recognized
        # (probably blocked by the browser)
        hps_config = cls.get_config(hps_server_url)
        authorization_endpoint = hps_config.authorization_endpoint.replace("127.0.0.1", "localhost").rstrip("/")
        token_endpoint = hps_config.token_endpoint.replace("127.0.0.1", "localhost").rstrip("/")
        return authorization_endpoint, token_endpoint

    @classmethod
    def acquire_token(
        cls,
        hps_server_url: str,
        client_id: str,
    ) -> tuple[str, str]:
        authorization_url, token_url = cls._get_hps_auth_urls(hps_server_url)
        scopes = ["openid", "profile", "email"]
        return cls._interactive_authentication(client_id, authorization_url, token_url, scopes)

    @classmethod
    def refresh_token(
        cls,
        hps_server_url: str,
        client_id: str,
        refresh_token: str,
    ) -> tuple[str, str]:
        _, token_url = cls._get_hps_auth_urls(hps_server_url)
        oauth = OAuth2Session(client_id)
        # for some reason, we must pass the client_id as body param even if it's already set in the OAuth2Session
        new_tokens = oauth.refresh_token(  # pyright: ignore[reportUnknownMemberType]
            token_url,
            refresh_token=refresh_token,
            verify=False,
            body=f"client_id={client_id}",
        )
        return new_tokens["access_token"], new_tokens["refresh_token"]

    @classmethod
    def check_token_validity(cls, access_token: str) -> bool:
        if not access_token:
            return False
        try:
            token_content = jws.extract_compact(access_token.encode())
            claims = json.loads(token_content.payload)
            claims_requests = jwt.JWTClaimsRegistry()
            claims_requests.validate(claims)
            return True
        except ExpiredTokenError:
            logger.info("HPS access token has expired.")
            return False

    @classmethod
    def get_config(cls, hps_url: str, verify: bool = False) -> HpsConfig:
        jms_url = hps_url.rstrip("/") + "/jms/api/v1"
        with httpx2.Client(timeout=30.0, verify=verify) as client:
            response = client.get(url=jms_url)
            response.raise_for_status()
            raw_config = response.json()
            config = {}
            config["base_auth_url"] = raw_config["services"]["external_auth_url"]
            config["client_id"] = raw_config["settings"]["spa_client_id"]
            config["scope"] = f"openid offline_access {raw_config['settings']['oidc_required_scope']}"
            config["discovery_endpoint"] = config["base_auth_url"].rstrip("/") + "/.well-known/openid-configuration"

            response = client.get(url=config["discovery_endpoint"])
            response.raise_for_status()
            raw_discovery = response.json()
            # Fill specific endpoints from discovery
            config["authorization_endpoint"] = raw_discovery["authorization_endpoint"]
            config["token_endpoint"] = raw_discovery["token_endpoint"]
            config["issuer"] = raw_discovery["issuer"]
            return HpsConfig.model_validate(config)
