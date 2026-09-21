# Copyright (C) 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
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

"""
Create certificates for gRPC mutual TLS testing.
This module can generate a complete set of certificates including:
- Certificate Authority (CA) key and certificate
- Server key and certificate(s) (signed by CA)
- Client key and certificate (signed by CA)
"""

from datetime import UTC, datetime, timedelta
import ipaddress
import logging
from pathlib import Path
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

_logger = logging.getLogger(__name__)


def generate_private_key(key_size: int = 4096) -> rsa.RSAPrivateKey:
    """
    Generate an RSA private key.
    Parameters
    ----------
    key_size : int, optional
        Size of the RSA key in bits, by default 4096
    Returns
    -------
    rsa.RSAPrivateKey
        Generated RSA private key
    """
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )


def save_private_key(key: rsa.RSAPrivateKey, filename: Path) -> None:
    """
    Save a private key to a PEM file.
    Parameters
    ----------
    key : rsa.RSAPrivateKey
        The private key to save
    filename : str
        Path to the output file
    """
    filename.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )


def save_certificate(cert: x509.Certificate, filename: Path) -> None:
    """
    Save a certificate to a PEM file.
    Parameters
    ----------
    cert : x509.Certificate
        The certificate to save
    filename : str
        Path to the output file
    """
    filename.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def create_ca_certificate(ca_key: rsa.RSAPrivateKey, validity_days: int) -> x509.Certificate:
    """
    Create a self-signed CA certificate.
    Parameters
    ----------
    ca_key : rsa.RSAPrivateKey
        The private key for the CA certificate
    validity_days : int
        Number of days the certificate should be valid
    Returns
    -------
    x509.Certificate
        Self-signed CA certificate with appropriate extensions for certificate signing
    """
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "Test CA"),
        ],
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=validity_days))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=True,
                crl_sign=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )

    return cert


def create_server_certificate(
    server_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    ca_key: rsa.RSAPrivateKey,
    server_common_name: str,
    validity_days: int,
    san_names: list[str] | None = None,
) -> x509.Certificate:
    """
    Create a server certificate signed by the CA with optional Subject Alternative Names.
    Parameters
    ----------
    server_key : rsa.RSAPrivateKey
        The private key for the server certificate
    ca_cert : x509.Certificate
        The CA certificate to use as issuer
    ca_key : rsa.RSAPrivateKey
        The CA private key to sign the certificate
    server_common_name : str
        The common name for the server certificate (will be used as CN and primary SAN)
    validity_days : int
        Number of days the certificate should be valid
    san_names : list, optional
        Additional Subject Alternative Names to include, by default None
    Returns
    -------
    x509.Certificate
        Server certificate signed by the CA with SERVER_AUTH extended key usage
    """
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, server_common_name),
        ],
    )

    # Build SAN list - always include the CN, plus any additional names
    san_list = [x509.DNSName(server_common_name)]
    if san_names:
        for name in san_names:
            # Skip if it's the same as CN to avoid duplicates
            if name != server_common_name:
                try:
                    # Try to parse as IP address
                    ip_addr = ipaddress.ip_address(name)
                    san_list.append(x509.IPAddress(ip_addr))  # type: ignore
                    _logger.info("  Added IP SAN: %s", name)
                except ValueError:
                    # Not an IP, treat as DNS name
                    san_list.append(x509.DNSName(name))
                    _logger.info("  Added DNS SAN: %s", name)

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=validity_days))
        .add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_cert_sign=False,
                crl_sign=False,
                data_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage(
                [
                    ExtendedKeyUsageOID.SERVER_AUTH,
                ],
            ),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    return cert


def create_client_certificate(
    client_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    ca_key: rsa.RSAPrivateKey,
    client_common_name: str,
    validity_days: int,
) -> x509.Certificate:
    """
    Create a client certificate signed by the CA.
    Parameters
    ----------
    client_key : rsa.RSAPrivateKey
        The private key for the client certificate
    ca_cert : x509.Certificate
        The CA certificate to use as issuer
    ca_key : rsa.RSAPrivateKey
        The CA private key to sign the certificate
    client_common_name : str
        The common name for the client certificate
    validity_days : int
        Number of days the certificate should be valid
    Returns
    -------
    x509.Certificate
        Client certificate signed by the CA with CLIENT_AUTH extended key usage
    """
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, client_common_name),
        ],
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(client_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=validity_days))
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName(client_common_name),
                ],
            ),
            critical=False,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_cert_sign=False,
                crl_sign=False,
                data_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage(
                [
                    ExtendedKeyUsageOID.CLIENT_AUTH,
                ],
            ),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    return cert


def parse_server_spec(server_spec: str) -> tuple[str, list[Any]]:
    """
    Parse a server specification string into primary hostname and SAN list.
    Parameters
    ----------
    server_spec : str
        A comma-separated string like "node01,192.0.2.1" or just "node01"
    Returns
    -------
    tuple[str, list]
        Tuple containing (primary_hostname, [additional_san_names])
    Raises
    ------
    ValueError
        If the server specification is empty or invalid
    """
    names = [name.strip() for name in server_spec.split(",") if name.strip()]
    if not names:
        raise ValueError("Server specification cannot be empty")

    primary_hostname = names[0]
    additional_sans = names[1:] if len(names) > 1 else []

    return primary_hostname, additional_sans


def generate_server_certificates(
    ca_cert: x509.Certificate,
    ca_key: rsa.RSAPrivateKey,
    server_specs: list[Any],
    validity_days: int,
    directory: str = ".",
) -> list[str]:
    """
    Generate multiple server certificates based on server specifications.
    Parameters
    ----------
    ca_cert : x509.Certificate
        The CA certificate to sign with
    ca_key : rsa.RSAPrivateKey
        The CA private key to sign with
    server_specs : list
        List of server specification strings in format "hostname[,san1,san2,...]"
    validity_days : int
        Number of days the certificates should be valid
    directory : str, optional
        Directory to save the generated certificates and keys, by default "."
    Returns
    -------
    list
        List of generated certificate filenames
    """
    generated_files: list[str] = []

    for spec in server_specs:
        primary_hostname, additional_sans = parse_server_spec(spec)

        # If only one server is specified, use 'server' as generic name
        filename = "server" if len(server_specs) == 1 else primary_hostname

        _logger.info("Generating server certificate for %s", primary_hostname)
        if additional_sans:
            _logger.info("  Additional SAN names: %s", ", ".join(additional_sans))

        # Generate server key and certificate
        server_key = generate_private_key()
        server_cert = create_server_certificate(
            server_key,
            ca_cert,
            ca_key,
            primary_hostname,
            validity_days,
            additional_sans,
        )

        # Save with primary hostname as filename
        key_filename = Path(directory) / f"{filename}.key"
        cert_filename = Path(directory) / f"{filename}.crt"

        save_private_key(server_key, key_filename)
        save_certificate(server_cert, cert_filename)

        generated_files.extend([key_filename.as_posix(), cert_filename.as_posix()])

    return generated_files
