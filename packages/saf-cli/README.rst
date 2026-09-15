#####################################################
Solution Application Framework - CLI
#####################################################

|python| |pypi| |GH-CI| |codecov| |Apache| |ruff|

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-saf-cli?logo=python&logoColor=white&label=Python
   :target: https://pypi.org/project/ansys-saf-cli/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-saf-cli.svg?logo=pypi&logoColor=white&label=PyPI
   :target: https://pypi.org/project/ansys-saf-cli/
   :alt: PyPI

.. |GH-CI| image:: https://github.com/ansys/saf-cli/actions/workflows/ci_cd_release.yml/badge.svg?label=CI
   :target: https://github.com/ansys/saf-cli/actions/workflows/ci_cd_release.yml
   :alt: GH-CI

.. |codecov| image:: https://img.shields.io/codecov/c/github/ansys/saf-cli
   :target: https://app.codecov.io/gh/ansys/saf-cli
   :alt: Codecov

.. |Apache| image:: https://img.shields.io/badge/License-Apache2.0-white.svg?labelColor=black
   :target: https://www.apache.org/licenses/
   :alt: Apache

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff


Overview
========

SAF CLI is a command-line tool that streamlines the development, management, and packaging of SAF-based solutions.
It provides a unified developer workflow for common SAF tasks such as scaffolding new solutions, installing and
managing solution environments, running solutions locally, executing commands in the correct Python environment,
building distributable installers, archiving solution source code, and listing registered solutions. Under the hood,
it helps coordinate the tools and services involved in the SAF ecosystem so that developers can work with solutions
through a consistent command set instead of stitching together manual steps.

+------------+------------------------------------------------------------------+
| Command    | Description                                                      |
+============+==================================================================+
| new        | Scaffold a new SAF solution from a template.                     |
+------------+------------------------------------------------------------------+
| install    | Set up the solution development environment and dependencies.    |
+------------+------------------------------------------------------------------+
| run        | Run a solution locally for development and testing.              |
+------------+------------------------------------------------------------------+
| execute    | Run arbitrary commands in the solution Python environment.       |
+------------+------------------------------------------------------------------+
| build      | Build a distributable package or installer for a solution.       |
+------------+------------------------------------------------------------------+
| add-step   | Add a new step to an existing SAF solution.                      |
+------------+------------------------------------------------------------------+
| archive    | Archive a solution source tree into a distributable bundle.      |
+------------+------------------------------------------------------------------+
| solutions  | List the solutions registered in the SAF solution database.      |
+------------+------------------------------------------------------------------+
| doc        | Open the SAF CLI documentation.                                  |
+------------+------------------------------------------------------------------+

The CLI is designed to improve developer productivity and solution consistency across the full solution lifecycle.
It reduces setup friction for new projects, lowers the amount of custom scripting teams need to maintain, and makes
local development, packaging, and delivery more repeatable.


Installation
============

Ensure you have all the necessary `prerequisites`_. Then, refer to the
`installation guidelines`_ for detailed instructions on how to install the
project on your system.


Documentation
=============

The `official documentation`_ of SAF CLI contains
the following chapters:

- `Getting started`_. This section provides a brief overview and instructions on
  how to get started with the project. It typically includes information on how
  to install the project, set up any necessary dependencies, and run a basic
  example or test to ensure everything is functioning correctly.

- `User guide`_. The user guide section offers detailed documentation and
  instructions on how to use the project. It provides comprehensive explanations
  of the project's features, functionalities, and configuration options. The
  user guide aims to help users understand the project's concepts, best
  practices, and recommended workflows.

- `Contribute`_. This section provides guidelines and instructions on how to
  contribute to the project. It includes information on how to set up the
  development environment, run tests, submit pull requests, and follow
  contribution guidelines.


Troubleshooting
===============

For troubleshooting or reporting issues, please open an issue in the project
repository.

Please follow these steps to report an issue:

- Go to the project repository.
- Click on the ``Issues`` tab.
- Click on the ``New Issue`` button.
- Provide a clear and detailed description of the issue you are facing.
- Include any relevant error messages, code snippets, or screenshots.

Additionally, you can refer to the `official documentation`_ for additional
resources and troubleshooting guides.


Using GitHub Copilot for Development
=====================================

This repository includes a `Copilot instructions file <https://github.com/ansys/saf-cli/blob/main/.github/copilot-instructions.md>`_ that provides AI-assisted development guidance. When working on SAF CLI enhancements or bug fixes:

#. GitHub Copilot will automatically reference the project structure, architecture, and development guidelines from the instructions file.
#. The instructions cover core concepts like solution resolution, dependency groups, environment management, and code style expectations.
#. Use Copilot to generate code that follows the established patterns for CLI commands, configuration management, and integrations.
#. The instructions emphasize type hints, Google-style docstrings, and the modular structure of the codebase.

This helps ensure consistency across contributions and speeds up development workflows.

**Suggested Copilot Prompt:**

When starting a new feature or fix, you can use a prompt like this to guide Copilot:

    "I'm working on the SAF CLI project. [Describe your task]. Please follow the project's Copilot instructions,
    including using Click for CLI commands, type hints, Google-style docstrings, and the existing modular structure
    in src/ansys/saf/cli/. Ensure the code integrates with the existing modules and includes appropriate error handling."

This prompt helps ensure Copilot generates code that aligns with SAF CLI's architecture and standards.


License
=======

This project is licensed under the Apache 2.0 License - see the `LICENSE`_ file for details.


Changelog
=========

The changelog section provides a summary of notable changes for each version of
SAF CLI for Python. It helps you keep track of updates, bug
fixes, new features, and improvements made to the project over time.

To view the complete changelog, visit the project repository and navigate
to the `CHANGELOG`_ file. It provides a comprehensive list of changes
categorized by version, along with brief descriptions of each change.


.. _official documentation: https://saf-cli.docs.solutions.ansys.com
.. _prerequisites: https://saf-cli.docs.solutions.ansys.com
.. _installation guidelines: https://saf-cli.docs.solutions.ansys.com/version/stable/getting_started
.. _Getting started: https://saf-cli.docs.solutions.ansys.com/version/stable/getting_started/index.html
.. _User guide: https://saf-cli.docs.solutions.ansys.com/version/stable/user_guide/index.html
.. _Contribute: https://saf-cli.docs.solutions.ansys.com/version/stable/contribute/index.html
.. _LICENSE: https://github.com/ansys/saf-cli/blob/main/LICENSE
.. _CHANGELOG: https://github.com/ansys/saf-cli/blob/main/CHANGELOG.md
