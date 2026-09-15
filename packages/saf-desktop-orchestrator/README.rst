#####################################################
Solution Application Framework - Desktop Orchestrator
#####################################################

|python| |pypi| |GH-CI| |codecov| |Apache| |ruff|

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-saf-desktop-orchestrator?logo=python&logoColor=white&label=Python
   :target: https://pypi.org/project/ansys-saf-desktop-orchestrator/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-saf-desktop-orchestrator.svg?logo=pypi&logoColor=white&label=PyPI
   :target: https://pypi.org/project/ansys-saf-desktop-orchestrator/
   :alt: PyPI

.. |GH-CI| image:: https://github.com/ansys/saf-desktop-orchestrator/actions/workflows/ci_cd_release.yml/badge.svg?label=CI
   :target: https://github.com/ansys/saf-desktop-orchestrator/actions/workflows/ci_cd_release.yml
   :alt: GH-CI

.. |codecov| image:: https://img.shields.io/codecov/c/github/ansys/saf-desktop-orchestrator
   :target: https://app.codecov.io/gh/ansys/saf-desktop-orchestrator
   :alt: Codecov

.. |Apache| image:: https://img.shields.io/badge/License-Apache2.0-white.svg?labelColor=black
   :target: https://www.apache.org/licenses/
   :alt: Apache

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff


Overview
========

The **SAF Desktop Orchestrator** is the central controller for running
SAF-based solutions in standalone desktop environments. It is responsible for
starting, health-checking, and shutting down all the services that a solution
needs to run on a user's local machine.

When a solution is launched, the orchestrator coordinates the startup of the
following components in a controlled sequence:

- **Solution API**: The backend service derived from the solution that exposes
  project data and transaction methods.
- **Solution UI**: The front-end displayed in a native window (via pywebview)
  or in an external browser.
- **Portal**: A UI for creating and managing projects within a solution.
- **OTEL Dashboard**: A web dashboard for viewing logs and traces from the
  various services.
- **PIM Light Server**: A lightweight server that creates product instances in
  isolated environments, separate from the method execution environment.
- **Additional services**: Other stateless or custom services defined by the
  solution.

The orchestrator also manages health checks to ensure each service is ready
before the solution UI is displayed, and it handles graceful shutdown when the
user closes the application.

.. note::

   The **Portal**, **OTEL Dashboard**, and **PIM Light Server** are not
   open-source components. For more information about these capabilities,
   contact the PyAnsys core team at pyansys-core@synopsys.com.


Documentation
=============

The `official documentation`_ of SAF Desktop Orchestrator for Python contains
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

- Go to the project repository.
- Click on the ``Issues`` tab.
- Click on the ``New Issue`` button.
- Provide a clear and detailed description of the issue you are facing.
- Include any relevant error messages, code snippets, or screenshots.

Additionally, you can refer to the `official documentation`_ for additional
resources and troubleshooting guides.


Using GitHub Copilot for Development
=====================================

This repository includes a `Copilot instructions file <https://github.com/ansys/saf-desktop-orchestrator/blob/main/.github/copilot-instructions.md>`_ that provides AI-assisted development guidance.
When working on SAF Desktop Orchestrator enhancements or bug fixes:

#. GitHub Copilot will automatically reference the project structure, architecture, and development guidelines from the instructions file.
#. The instructions cover core concepts like solution resolution, dependency groups, environment management, and code style expectations.
#. Use Copilot to generate code that follows the established patterns, configuration management, and integrations.
#. The instructions emphasize type hints, numpydoc docstrings, and the modular structure of the codebase.

This helps ensure consistency across contributions and speeds up development workflows.

**Suggested Copilot Prompt:**

When starting a new feature or fix, you can use a prompt like this to guide Copilot:

    "I'm working on the SAF Desktop Orchestrator project. [Describe your task]. Please follow the project's Copilot instructions,
    type hints, numpydoc docstrings, and the existing modular structure in src/ansys/saf/desktop/orchestrator/. Ensure the
    code integrates with the existing modules and includes appropriate error handling."

This prompt helps ensure Copilot generates code that aligns with SAF Desktop Orchestrator's architecture and standards.


License
=======

This project is licensed under the Apache 2.0 License - see the `LICENSE`_ file for details.


Changelog
=========

The changelog section provides a summary of notable changes for each version of
SAF Desktop Orchestrator for Python. It helps you keep track of updates, bug
fixes, new features, and improvements made to the project over time.

To view the complete changelog, visit the project repository and navigate
to the `CHANGELOG`_ file. It provides a comprehensive list of changes
categorized by version, along with brief descriptions of each change.


.. _official documentation: https://saf-desktop-orchestrator.docs.solutions.ansys.com
.. _Getting started: https://saf-desktop-orchestrator.docs.solutions.ansys.com/version/stable/getting_started/index.html
.. _User guide: https://saf-desktop-orchestrator.docs.solutions.ansys.com/version/stable/user_guide/index.html
.. _Contribute: https://saf-desktop-orchestrator.docs.solutions.ansys.com/version/stable/contribute/index.html
.. _LICENSE: https://github.com/ansys/saf-desktop-orchestrator/blob/main/LICENSE
.. _CHANGELOG: https://github.com/ansys/saf-desktop-orchestrator/blob/main/CHANGELOG.md
