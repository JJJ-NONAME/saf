##############################
Blob Management API for Python
##############################

|python| |pypi| |GH-CI| |codecov| |Apache| |ruff|

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-bdm-api?logo=python&logoColor=white&label=Python
   :target: https://pypi.org/project/ansys-bdm-api/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-bdm-api.svg?logo=pypi&logoColor=white&label=PyPI
   :target: https://pypi.org/project/ansys-bdm-api/
   :alt: PyPI

.. |GH-CI| image:: https://github.com/ansys/bdm-python-api/actions/workflows/ci_cd_release.yml/badge.svg?label=CI
   :target: https://github.com/ansys/bdm-python-api/actions/workflows/ci_cd_release.yml
   :alt: GH-CI

.. |codecov| image:: https://img.shields.io/codecov/c/github/ansys/bdm-python-api
   :target: https://app.codecov.io/gh/ansys/bdm-python-api
   :alt: Codecov

.. |Apache| image:: https://img.shields.io/badge/License-Apache2.0-white.svg?labelColor=black
   :target: https://www.apache.org/licenses/
   :alt: Apache

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff


Overview
========

Blob Data Management (BDM) Python API is a way to manage files and directories through
abstract references instead of direct file-system paths. In SAF GLOW, BDM is a
shared technology component that helps applications work with engineering data
in a scalable and cloud-ready way across different runtime environments.

The ``ansys-bdm-api`` package provides the Python interfaces and models for
working with BDM services. It is built around concepts such as
``EntityHandle``, which references a file or directory through metadata, and
``Storage Scopes``, which define where data lives and how it is transferred or
realized when needed.

This approach helps reduce unnecessary file copying, improves performance
through caching, and makes workflows more portable across Windows, Linux,
cloud, and on-premises environments. It also supports safer and more
consistent handling of large engineering datasets and directory structures.


Installation
============

Ensure you have all the necessary `prerequisites`_. Then, refer to the
`installation guidelines`_ for detailed instructions on how to install the
project in your system.


Documentation
=============

The `official documentation`_ of the Blob Management API for Python contains the following chapters:

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


License
=======

You can find the full text of the license in the `LICENSE`_ file.


Changelog
=========

The changelog section provides a summary of notable changes for each version of
Blob Management API for Python. It helps you keep track of updates, bug
fixes, new features, and improvements made to the project over time.

To view the complete changelog, visit the project repository and navigate
to the `CHANGELOG`_ file. It provides a comprehensive list of changes
categorized by version, along with brief descriptions of each change.


.. _prerequisites: https://bdm-python-api.docs.solutions.ansys.com/version/stable/getting-started.html#prerequisites
.. _installation guidelines: https://bdm-python-api.docs.solutions.ansys.com/version/stable/getting-started.html#installation
.. _official documentation: https://bdm-python-api.docs.solutions.ansys.com
.. _Getting started: https://bdm-python-api.docs.solutions.ansys.com/version/stable/getting-started.html
.. _User guide: https://bdm-python-api.docs.solutions.ansys.com/version/stable/user-guide.html
.. _API reference: https://bdm-python-api.docs.solutions.ansys.com/version/stable/api/index.html
.. _Examples: https://bdm-python-api.docs.solutions.ansys.com/version/stable/examples.html
.. _Contribute: https://bdm-python-api.docs.solutions.ansys.com/version/stable/contribute.html
.. _LICENSE: https://github.com/ansys/bdm-python-api/blob/main/LICENSE
.. _CHANGELOG: https://github.com/ansys/bdm-python-api/blob/main/CHANGELOG.md

