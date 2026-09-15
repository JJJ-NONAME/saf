#######################################################
Solution Application Framework - SAF Desktop Installer
#######################################################

|python| |pypi| |GH-CI| |codecov| |Apache| |ruff|

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-saf-desktop-installer?logo=python&logoColor=white&label=Python
   :target: https://pypi.org/project/ansys-saf-desktop-installer/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-saf-desktop-installer.svg?logo=pypi&logoColor=white&label=PyPI
   :target: https://pypi.org/project/ansys-saf-desktop-installer/
   :alt: PyPI

.. |GH-CI| image:: https://github.com/ansys/saf-desktop-installer/actions/workflows/ci_cd_release.yml/badge.svg?label=CI
   :target: https://github.com/ansys/saf-desktop-installer/actions/workflows/ci_cd_release.yml
   :alt: GH-CI

.. |codecov| image:: https://img.shields.io/codecov/c/github/ansys/saf-desktop-installer
   :target: https://app.codecov.io/gh/ansys/saf-desktop-installer
   :alt: Codecov

.. |Apache| image:: https://img.shields.io/badge/License-Apache2.0-white.svg?labelColor=black
   :target: https://www.apache.org/licenses/
   :alt: Apache

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff


Overview
========

The **SAF Desktop Installer** enables packaging SAF-based solutions into
standalone, distributable installers for desktop deployment. It is part of the
Solution Application Framework (SAF) toolchain and is typically invoked through
the ``saf build`` command provided by the SAF CLI.

The generated installer is self-contained: it bundles the solution code, all
Python dependencies, and the Python interpreter itself, so end users can run
the solution without needing a pre-configured development environment. Ansys
products and other external tools required by the solution must still be
installed separately on the target machine.

Key capabilities include:

- **Standalone packaging**: Uses PyInstaller to produce a single installer that
  includes all necessary dependencies and a Python interpreter.
- **Cross-platform support**: Generates installers compatible with the
  operating system where the build is executed (Windows ``.exe`` or Linux
  executable).
- **Online and offline modes**: By default, installers download dependencies at
  install time; the ``--offline-package`` option bundles everything for
  environments without internet access.
- **Customizable build options**: Supports encryption, code obfuscation, custom
  entry points, and configurable Python versions.
- **Documentation embedding**: Automatically builds and embeds Sphinx
  documentation so users can access it offline from within the solution.

From a workflow perspective, SAF Desktop Installer is the final step in
preparing a solution for distribution. Once a solution has been developed and
tested locally using SAF CLI and SAF Desktop Orchestrator, the installer
packages it into a form that can be delivered to end users or deployed across
an organization.


Installation
============

Ensure you have all the necessary `prerequisites`_. Then, refer to the
`installation guidelines`_ for detailed instructions on how to install the
project in your system.


Documentation
=============

The `official documentation`_ of SAF Desktop Installer contains
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
SAF Desktop Installer for Python. It helps you keep track of updates, bug
fixes, new features, and improvements made to the project over time.

To view the complete changelog, visit the project repository and navigate
to the `CHANGELOG`_ file. It provides a comprehensive list of changes
categorized by version, along with brief descriptions of each change.


.. _prerequisites: https://saf-desktop-installer.docs.solutions.ansys.com/version/stable/getting_started#prerequisites
.. _installation guidelines: https://saf-desktop-installer.docs.solutions.ansys.com/version/stable/getting_started#installation

.. _official documentation: https://saf-desktop-installer.docs.solutions.ansys.com
.. _Getting started: https://saf-desktop-installer.docs.solutions.ansys.com/version/stable/getting_started/index.html
.. _User guide: https://saf-desktop-installer.docs.solutions.ansys.com/version/stable/user_guide/index.html
.. _Contribute: https://saf-desktop-installer.docs.solutions.ansys.com/version/stable/contribute/index.html

.. _LICENSE: https://github.com/ansys/saf-desktop-installer/blob/main/LICENSE
.. _CHANGELOG: https://github.com/ansys/saf-desktop-installer/blob/main/CHANGELOG.md
