################################################################
Solution Application Framework - Guided Low-Code Workflow Engine
################################################################

|python| |pypi| |GH-CI| |codecov| |Apache| |ruff|

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-saf-glow-engine?logo=python&logoColor=white&label=Python
   :target: https://pypi.org/project/ansys-saf-glow-engine/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-saf-glow-engine.svg?logo=pypi&logoColor=white&label=PyPI
   :target: https://pypi.org/project/ansys-saf-glow-engine/
   :alt: PyPI

.. |GH-CI| image:: https://github.com/ansys/glow-engine/actions/workflows/ci_cd_release.yml/badge.svg?label=CI
   :target: https://github.com/ansys/glow-engine/actions/workflows/ci_cd_release.yml
   :alt: GH-CI

.. |codecov| image:: https://img.shields.io/codecov/c/github/ansys/glow-engine
   :target: https://app.codecov.io/gh/ansys/glow-engine
   :alt: Codecov

.. |Apache| image:: https://img.shields.io/badge/License-Apache2.0-white.svg?labelColor=black
   :target: https://www.apache.org/licenses/
   :alt: Apache

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff


Overview
========

**GLOW Engine** stands for **Guided Low-Code Workflow Engine**. It is the backend
component of the Solution Application Framework (SAF), a modular and extensible
Python framework designed to accelerate the development of simulation-driven
web applications and digital engineering workflows.

GLOW abstracts complex backend operations, orchestrates integrations with Ansys
products, and provides a unified API for building, running, and managing
solution applications. It enables solution developers to focus on business
logic and user experience rather than low-level infrastructure, while taking
advantage of Ansys technologies and best practices for production-ready
engineering applications.

Key capabilities include:

- High-level APIs for defining engineering workflows, transactions, and
  data models without extensive boilerplate code.
- Seamless connectivity with Ansys solvers and tools such as Mechanical,
  Fluent, and MAPDL through PyAnsys SDKs.
- Support for custom steps, plugins, and asset encryption to protect
  intellectual property.
- Designed for both small- and large-scale deployments,
  supporting multi-user, multi-project, and multi-instance scenarios.
- Handles long-running and synchronous transactions with built-in state management,
  error handling, and logging.
- Compatible with Windows 10/11 and Ubuntu 22.04/24.04, and deployable in
  desktop and on-premises environments.

By serving as the backbone of the SAF ecosystem, GLOW Engine allows teams to
deliver powerful, maintainable solution applications more quickly and with
greater consistency.


Installation
============

Ensure you have all the necessary `prerequisites`_. Then, refer to the
`installation guidelines`_ for detailed instructions on how to install the
project in your system.


Documentation
=============

The `official documentation`_ of SAF GLOW Engine contains the following chapters:


- `Getting started`_. This section provides a brief overview and instructions on
  how to get started with the project. It typically includes information on how
  to install the project, set up any necessary dependencies, and run a basic
  example or test to ensure everything is functioning correctly.

- `User guide`_. The user guide section offers detailed documentation and
  instructions on how to use the project. It provides comprehensive explanations
  of the project's features, functionalities, and configuration options. The
  user guide aims to help users understand the project's concepts, best
  practices, and recommended workflows.

- `API reference`_. The API reference section provides detailed documentation
  for the project's application programming interface (API). It includes
  information about classes, functions, methods, and their parameters, return
  values, and usage examples. This reference helps developers understand the
  available API endpoints, their functionalities, and how to interact with them
  programmatically.

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

This repository includes a `Copilot instructions file <https://github.com/ansys/glow-engine/blob/main/.github/copilot-instructions.md>`_ that provides AI-assisted development guidance. When working on GLOW Engine enhancements or bug fixes:

#. GitHub Copilot will automatically reference the project structure, architecture, and development guidelines from the instructions file.
#. The instructions cover core concepts like workflow APIs, transaction handling, Ansys product integrations, and code style expectations.
#. Use Copilot to generate code that follows the established patterns for FastAPI endpoints, data models, and backend services.
#. The instructions emphasize type hints, numpydoc-style docstrings, and the modular structure of the codebase.

This helps ensure consistency across contributions and speeds up development workflows.

**Suggested Copilot Prompt:**

When starting a new feature or fix, you can use a prompt like this to guide Copilot:

    "I'm working on the GLOW Engine project. [Describe your task]. Please follow the project's Copilot instructions,
    including using FastAPI for APIs, type hints, numpydoc-style docstrings, and the existing modular structure
    in src/ansys/saf/glow/. Ensure the code integrates with the existing modules and includes appropriate error handling."

This prompt helps ensure Copilot generates code that aligns with GLOW Engine's architecture and standards.


License
=======

This project is licensed under the Apache 2.0 License - see the `LICENSE`_ file for details.


Changelog
=========

The changelog section provides a summary of notable changes for each version of SAF GLOW Engine.
It helps you keep track of updates, bug fixes, new features, and improvements made to the project over time.

To view the complete changelog, please visit the project repository and navigate
to the `CHANGELOG`_ file. It provides a comprehensive list of changes
categorized by version, along with brief descriptions of each change.


.. _official documentation: https://glow-engine.docs.solutions.ansys.com
.. _Getting started: https://glow-engine.docs.solutions.ansys.com/version/stable/getting_started/index.html
.. _User guide: https://glow-engine.docs.solutions.ansys.com/version/stable/user_guide/index.html
.. _API reference: https://glow-engine.docs.solutions.ansys.com/version/stable/api/index.html
.. _Contribute: https://glow-engine.docs.solutions.ansys.com/version/stable/contribute/index.html
.. _prerequisites: https://glow-engine.docs.solutions.ansys.com/version/stable/getting_started/index.html#prerequisites
.. _installation guidelines: https://glow-engine.docs.solutions.ansys.com/version/stable/getting_started/index.html#installation
.. _LICENSE: https://github.com/ansys/glow-engine/blob/main/LICENSE
.. _CHANGELOG: https://github.com/ansys/glow-engine/blob/main/CHANGELOG.md
