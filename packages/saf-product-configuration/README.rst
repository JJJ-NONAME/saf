######################################################
Solution Application Framework - Product Configuration
######################################################

|python| |pypi| |GH-CI| |codecov| |Apache| |ruff|

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-saf-product-configuration?logo=python&logoColor=white&label=Python
   :target: https://pypi.org/project/ansys-saf-product-configuration/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-saf-product-configuration.svg?logo=pypi&logoColor=white&label=PyPI
   :target: https://pypi.org/project/ansys-saf-product-configuration/
   :alt: PyPI

.. |GH-CI| image:: https://github.com/ansys/saf-product-configuration/actions/workflows/ci_cd_release.yml/badge.svg?label=CI
   :target: https://github.com/ansys/saf-product-configuration/actions/workflows/ci_cd_release.yml
   :alt: GH-CI

.. |codecov| image:: https://img.shields.io/codecov/c/github/ansys/saf-product-configuration
   :target: https://app.codecov.io/gh/ansys/saf-product-configuration
   :alt: Codecov

.. |Apache| image:: https://img.shields.io/badge/License-Apache2.0-white.svg?labelColor=black
   :target: https://www.apache.org/licenses/
   :alt: Apache

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff


Overview
========

SAF Product Configuration provides protocol-based interfaces and ready-to-use product definitions for launching
products in SAF-based solutions.

Out of the box, the package contains the recipes, startup commands, environment settings, and version-specific
metadata needed to launch selected Ansys products in a consistent way through SAF product instance systems such as
HPS and PIM Light. These built-in configurations cover the following products, so solution developers can use proven
launch definitions instead of reimplementing product startup behavior for each deployment.

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

From a business and solution-development perspective, SAF Product Configuration helps reduce the amount of custom
code that developers need to write and maintain to launch products reliably. It provides an out-of-the-box connector
layer for product startup and lifecycle integration, so teams can focus more on solution logic and user workflows
instead of rebuilding product-specific launch, configuration, and instance-management behavior.

The package is not limited to the built-in Ansys product definitions. It also provides protocol-based interfaces for
describing a product name, supported versions, execution command, environment variables, service type, and transport
settings. This makes it possible for developers to create and load their own custom product configurations to start
additional Ansys products or even third-party applications, while keeping the same SAF integration model and
configuration workflow.


Installation
============

Ensure you have all the necessary `prerequisites`_. Then, refer to the
`installation guidelines`_ for detailed instructions on how to install the
project in your system.


Documentation
=============

The `official documentation`_ of SAF Product Configuration contains
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

- `API reference`_. The API reference section provides detailed documentation
  for the project's application programming interface (API). It includes
  information about classes, functions, methods, and their parameters, return
  values, and usage examples. This reference helps developers understand the
  available API endpoints, their functionalities, and how to interact with them
  programmatically.

- `Examples`_. The examples section showcases practical code examples that
  demonstrate how to use the project in real-world scenarios. It provides sample
  code snippets or complete scripts that illustrate different use cases or
  demonstrate specific features of the project. Examples serve as practical
  references for developers, helping them understand how to apply the project to
  their own applications.

- `Contribute`_. This section provides guidelines and instructions on how to
  contribute to the project. It includes information on how to set up the
  development environment, run tests, submit pull requests, and follow
  contribution guidelines.


Troubleshooting
===============

For troubleshooting or reporting issues, open an issue in the project
repository.

Follow these steps to report an issue:

- Go to the project repository.
- Click on the ``Issues`` tab.
- Click on the ``New Issue`` button.
- Provide a clear and detailed description of the issue you are facing.
- Include any relevant error messages, code snippets, or screenshots.

Additionally, you can refer to the `official documentation`_ for additional
resources and troubleshooting guides.


License
=======

This project is licensed under the Apache 2.0 License - see the `LICENSE`_ file for details.


Changelog
=========

The changelog section provides a summary of notable changes for each version of
SAF Product Configuration for Python. It helps you keep track of updates, bug
fixes, new features, and improvements made to the project over time.

To view the complete changelog, visit the project repository and navigate
to the `CHANGELOG`_ file. It provides a comprehensive list of changes
categorized by version, along with brief descriptions of each change.


.. Prerequisites and installation guidelines
.. _prerequisites: https://saf-product-configuration.docs.solutions.ansys.com/version/stable/getting-started#prerequisites
.. _installation guidelines: https://saf-product-configuration.docs.solutions.ansys.com/version/stable/getting-started#installation

.. Documentation chapters
.. _official documentation: https://saf-product-configuration.docs.solutions.ansys.com
.. _Getting started: https://saf-product-configuration.docs.solutions.ansys.com/version/stable/getting-started.html
.. _User guide: https://saf-product-configuration.docs.solutions.ansys.com/version/stable/user-guide.html
.. _API reference: https://saf-product-configuration.docs.solutions.ansys.com/version/stable/api/index.html
.. _Examples: https://saf-product-configuration.docs.solutions.ansys.com/version/dev/examples.html
.. _Contribute: https://saf-product-configuration.docs.solutions.ansys.com/version/stable/contribute.html

.. _LICENSE: https://github.com/ansys/saf-product-configuration/blob/main/LICENSE
.. _CHANGELOG: https://github.com/ansys/saf-product-configuration/blob/main/CHANGELOG.md
