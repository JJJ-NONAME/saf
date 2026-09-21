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

import json
import sys

import click

from ansys.saf.cli._solutions.environment import (
    set_user_level_environment_variable,
    validate_credentials,
)


@click.group()
def main():
    """Solutions Manager Integration CLI"""


@main.command("validate-credentials")
@click.option("--source", required=True, help="Source configuration as JSON")
@click.option("--username", required=True, help="The username for authentication")
@click.option("--password", required=True, help="The password for authentication")
def validate_credentials_cmd(source: str, username: str, password: str):
    """Validate credentials by testing PyPI access"""
    try:
        source_data = json.loads(source)
        is_valid = validate_credentials(source_data, username, password)
        click.echo("Credentials are valid!" if is_valid else "Invalid credentials.")
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@main.command("set-env-var")
@click.option("--key", required=True, help="The name of the environment variable")
@click.option("--value", required=True, help="The value to set for the environment variable")
def set_env_var_cmd(key: str, value: str):
    """Set a user-level environment variable"""
    try:
        set_user_level_environment_variable(key, value)
        click.echo(f"Environment variable '{key}' set successfully!")
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
