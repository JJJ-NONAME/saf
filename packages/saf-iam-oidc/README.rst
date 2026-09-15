#########
IAM OIDC
#########

|python| |pypi| |GH-CI| |codecov| |Apache-2.0| |ruff|

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-iam-oidc?logo=python&logoColor=white&label=Python
   :target: https://pypi.org/project/ansys-iam-oidc/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-iam-oidc.svg?logo=pypi&logoColor=white&label=PyPI
   :target: https://pypi.org/project/ansys-iam-oidc/
   :alt: PyPI

.. |codecov| image:: https://img.shields.io/codecov/c/github/ansys/ansys-iam-oidc
   :target: https://app.codecov.io/gh/ansys/ansys-iam-oidc
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/saf-iam-oidc/actions/workflows/certification.yml/badge.svg?label=CI
   :target: https://github.com/ansys/saf-iam-oidc/actions/workflows/certification.yml
   :alt: GH-CI

.. |Apache-2.0| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://www.apache.org/licenses/LICENSE-2.0
   :alt: Apache-2.0

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff


Overview
========

The ``ansys-iam-oidc`` package provides Python utilities for adding OAuth 2.0
and OpenID Connect (OIDC) authentication to SAF applications. It simplifies
the integration of secure identity flows so that developers can protect APIs,
validate access tokens, and retrieve user information without implementing the
underlying protocol details themselves.

Key capabilities include:

- **Token validation**: Verify access-token signatures, expiration, and audience
  claims against an OIDC provider's public keys.
- **User information retrieval**: Obtain standard OIDC user-profile claims
  either from the token itself or by querying the provider's ``userinfo``
  endpoint.
- **FastAPI integration**: Ready-to-use dependency classes for protecting
  FastAPI routes, including support for HTTP requests and WebSocket connections.
- **Flexible client modes**: Support for synchronous and asynchronous workflows
  through ``OidcClient`` and ``AsyncOidcClient``.
- **Standard OIDC flows**: Foundation for authorization-code with PKCE, client
  credentials, device-code, token introspection, token revocation, and token
  exchange.

By handling discovery, key retrieval, and claim validation internally, the
package allows developers to focus on application logic while relying on a
consistent and tested authentication layer.


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

This library is licensed under the Apache License 2.0.
You can find the full text of the license in the `LICENSE`_ file.


Changelog
=========

The changelog section provides a summary of notable changes for each version of
SAF IAM OIDC for Python. It helps you keep track of updates, bug fixes, new
features, and improvements made to the project over time.

To view the complete changelog, visit the project repository and navigate
to the `CHANGELOG`_ file. It provides a comprehensive list of changes
categorized by version, along with brief descriptions of each change.


.. _official documentation: https://saf-iam-oidc.docs.solutions.ansys.com
.. _prerequisites: https://saf-iam-oidc.docs.solutions.ansys.com/version/dev/getting-started.html#prerequisites
.. _installation guidelines: https://saf-iam-oidc.docs.solutions.ansys.com/version/dev/getting-started.html#installation
.. _Getting started: https://saf-iam-oidc.docs.solutions.ansys.com/version/stable/getting-started.html
.. _User guide: https://saf-iam-oidc.docs.solutions.ansys.com/version/stable/user-guide.html
.. _API reference: https://saf-iam-oidc.docs.solutions.ansys.com/version/stable/api/index.html
.. _Examples: https://saf-iam-oidc.docs.solutions.ansys.com/version/dev/examples.html
.. _Contribute: https://saf-iam-oidc.docs.solutions.ansys.com/version/stable/contribute.html
.. _LICENSE: https://github.com/ansys/saf-iam-oidc/blob/main/LICENSE
.. _CHANGELOG: https://github.com/ansys/saf-iam-oidc/blob/main/CHANGELOG.md