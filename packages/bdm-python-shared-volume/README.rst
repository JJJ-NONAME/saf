#########################
BDM Python Shared Volume
#########################

|python| |pypi| |GH-CI| |codecov| |APACHE| |ruff|

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-bdm-shared-volume?logo=python&logoColor=white&label=Python
   :target: https://pypi.org/project/ansys-bdm-shared-volume/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-bdm-shared-volume.svg?logo=pypi&logoColor=white&label=PyPI
   :target: https://pypi.org/project/ansys-bdm-shared-volume/
   :alt: PyPI

.. |codecov| image:: https://img.shields.io/codecov/c/github/ansys/bdm-python-shared-volume
   :target: https://app.codecov.io/gh/ansys/bdm-python-shared-volume
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/bdm-python-shared-volume/actions/workflows/certification.yml/badge.svg?label=CI
   :target: https://github.com/ansys/bdm-python-shared-volume/actions/workflows/certification.yml
   :alt: GH-CI

.. |APACHE| image:: https://img.shields.io/badge/License-APACHE-white.svg?labelColor=black
   :target: https://opensource.org/licenses/Apache-2.0
   :alt: APACHE

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff


Overview
========

The ``ansys-bdm-shared-volume`` package provides a concrete implementation of
the Blob Data Management (BDM) interface defined by
`ansys-bdm-api <https://github.com/ansys/bdm-python-api>`_. It uses a networked
shared file-system volume as the underlying storage backend.

Within the SAF ecosystem, this package enables GLOW-based solutions to manage
files and directories through the standard BDM abstractions while storing data
on a shared volume that is accessible across processes and machines. This makes
it well suited for desktop deployments and on-premises environments where a
common network drive or local shared folder is available.

Key capabilities include:

- Implementation of ``StorageScope`` and ``AsyncStorageScope`` for synchronous
  and asynchronous file operations.
- Automatic tracking and cleanup of cached entities when a storage scope exits.
- Factory utilities for creating storage scopes from configuration.

By plugging into the BDM layer, the shared-volume backend allows solution code
to remain storage-agnostic: the same workflow logic can run against this
backend during local development and against other BDM backends in cloud or
distributed deployments.


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
BDM Python Shared Volume. It helps you keep track of updates, bug
fixes, new features, and improvements made to the project over time.

To view the complete changelog, visit the project repository and navigate
to the `CHANGELOG`_ file. It provides a comprehensive list of changes
categorized by version, along with brief descriptions of each change.


.. _prerequisites: https://bdm-python-shared-volume.docs.solutions.ansys.com/version/stable/getting-started#prerequisites
.. _installation guidelines: https://bdm-python-shared-volume.docs.solutions.ansys.com/version/stable/getting-started#installation

.. _official documentation: https://bdm-python-shared-volume.docs.solutions.ansys.com
.. _Getting started: https://bdm-python-shared-volume.docs.solutions.ansys.com/version/stable/getting-started.html
.. _User guide: https://bdm-python-shared-volume.docs.solutions.ansys.com/version/stable/user-guide.html
.. _API reference: https://bdm-python-shared-volume.docs.solutions.ansys.com/version/stable/api/index.html
.. _Examples: https://bdm-python-shared-volume.docs.solutions.ansys.com/version/dev/examples.html
.. _Contribute: https://bdm-python-shared-volume.docs.solutions.ansys.com/version/stable/contribute.html

.. _LICENSE: https://github.com/ansys/bdm-python-shared-volume/blob/main/LICENSE
.. _CHANGELOG: https://github.com/ansys/bdm-python-shared-volume/blob/main/CHANGELOG.md