######################################################
Solution Application Framework - Product Manager
######################################################

|python| |pypi| |GH-CI| |codecov| |Apache| |ruff|

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-saf-product-manager?logo=python&logoColor=white&label=Python
   :target: https://pypi.org/project/ansys-saf-product-manager/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-saf-product-manager.svg?logo=pypi&logoColor=white&label=PyPI
   :target: https://pypi.org/project/ansys-saf-product-manager/
   :alt: PyPI

.. |GH-CI| image:: https://github.com/ansys/saf-product-manager/actions/workflows/ci_cd_release.yml/badge.svg?label=CI
   :target: https://github.com/ansys/saf-product-manager/actions/workflows/ci_cd_release.yml
   :alt: GH-CI

.. |codecov| image:: https://img.shields.io/codecov/c/github/ansys/saf-product-manager
   :target: https://app.codecov.io/gh/ansys/saf-product-manager
   :alt: Codecov

.. |Apache| image:: https://img.shields.io/badge/License-Apache2.0-white.svg?labelColor=black
   :target: https://www.apache.org/licenses/
   :alt: Apache

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff


Overview
========

The ``ansys-saf-product-manager`` package provides ready-to-use managers for
launching and controlling Ansys product instances within SAF-based solutions.
Each manager wraps the corresponding PyAnsys client library and exposes a
consistent API for initializing, connecting to, and interacting with the
product.

Within the SAF ecosystem, the Product Manager layer sits between solution code
and the underlying PyAnsys clients. It handles the details of product startup,
connection management, and lifecycle control so that solution developers can
work with Ansys products through a uniform interface without writing low-level
initialization logic themselves.

The package currently supports the following products:

+------------+------------------------------------------------------------------+
| Product    | Supported versions                                               |
+============+==================================================================+
| MAPDL      | ``2025 R1 SP4``, ``2025 R2 SP4``                                 |
+------------+------------------------------------------------------------------+
| Mechanical | ``2025 R1 SP4``, ``2025 R2 SP4``                                 |
+------------+------------------------------------------------------------------+
| Fluent     | ``2025 R1 SP4``, ``2025 R2 SP4``                                 |
+------------+------------------------------------------------------------------+
| AEDT       | ``2025 R1 SP4``, ``2025 R2 SP4``                                 |
+------------+------------------------------------------------------------------+
| optiSLang  | ``2024 R1``, ``2024 R2``                                         |
+------------+------------------------------------------------------------------+
| Geometry   | Windows ``2025 R1 SP4``, ``2025 R2 SP4``, Linux: ``2025 R2 SP4`` |
+------------+------------------------------------------------------------------+

Each product manager is packaged as an optional extra, so solutions only pull
in the dependencies they actually need.


Installation
============

Ensure you have all the necessary `prerequisites`_. Then, refer to the
`installation guidelines`_ for detailed instructions on how to install the
project in your system.


Documentation
=============

The `official documentation`_ of SAF Product Manager contains
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

This repository includes a `Copilot instructions file <https://github.com/ansys/saf-product-manager/blob/main/.github/copilot-instructions.md>`_ that provides AI-assisted development guidance. When working on SAF Product Manager enhancements or bug fixes:

#. GitHub Copilot will automatically reference the project structure, architecture, and development guidelines from the instructions file.
#. The instructions cover core concepts like product manager patterns, optional dependency handling, and code style expectations.
#. Use Copilot to generate code that follows the established patterns for product managers, PyAnsys client integration, and shared utilities.
#. The instructions emphasize type hints, the fully typed codebase, and the modular structure with one subdirectory per supported product.

This helps ensure consistency across contributions and speeds up development workflows.

**Suggested Copilot Prompt:**

When starting a new feature or fix, you can use a prompt like this to guide Copilot:

    "I'm working on the SAF Product Manager project. [Describe your task]. Please follow the project's Copilot instructions,
    including type hints, the existing modular structure in src/ansys/saf/product_manager/, and the pattern of one subdirectory
    per supported product. Ensure the code integrates with the existing modules and includes appropriate error handling."

This prompt helps ensure Copilot generates code that aligns with SAF Product Manager's architecture and standards.


License
=======

This project is licensed under the Apache 2.0 License - see the `LICENSE`_ file for details.


Changelog
=========

The changelog section provides a summary of notable changes for each version of
SAF Product Manager for Python. It helps you keep track of updates, bug
fixes, new features, and improvements made to the project over time.

To view the complete changelog, please visit the project repository and navigate
to the `CHANGELOG`_ file. It provides a comprehensive list of changes
categorized by version, along with brief descriptions of each change.


.. _prerequisites: https://saf-product-manager.docs.solutions.ansys.com/version/stable/getting-started.html#prerequisites
.. _installation guidelines: https://saf-product-manager.docs.solutions.ansys.com/version/stable/getting-started.html#installation

.. _official documentation: https://saf-product-manager.docs.solutions.ansys.com
.. _Getting started: https://saf-product-manager.docs.solutions.ansys.com/version/stable/getting-started.html
.. _User guide: https://saf-product-manager.docs.solutions.ansys.com/version/stable/user-guide.html
.. _Contribute: https://saf-product-manager.docs.solutions.ansys.com/version/stable/contribute.html

.. _LICENSE: https://github.com/ansys/saf-product-manager/blob/main/LICENSE
.. _CHANGELOG: https://github.com/ansys/saf-product-manager/blob/main/CHANGELOG.md