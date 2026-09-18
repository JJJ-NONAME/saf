Dash Super Components
=========================
|pyansys| |pypi| |python| |apache|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-solutions-dash-super-components.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-solutions-dash-super-components/
   :alt: PyPI

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-solutions-dash-super-components?logo=pypi
   :target: https://pypi.org/project/ansys-solutions-dash-super-components/
   :alt: Python

.. |apache| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0
   :alt: Apache 2.0

Overview
--------

Dash Super Components is a collection of pre-assembled, high-level UI components
built on top of the `Dash Mantine Components (DMC) <https://www.dash-mantine-components.com/>`_
library. The components implement common patterns in simulation web app UIs, reducing
frontend development effort by packaging UI logic and layout conventions into smart
building blocks.

Dash is a trademark of Plotly Technologies Inc. This project is not affiliated with, endorsed by,
or sponsored by Plotly Technologies Inc.

Documentation and issues
------------------------

For full documentation, including the getting started guide, user guide, and API
reference, see the `Dash Super Components documentation
<https://saf.ansys.com/version/stable/user_guide/frontend/dash/dash_super_components/index.html>`_.
In the upper right corner of the documentation's title bar, there is an option for
switching from viewing the documentation for the latest stable release to viewing
the documentation for the development version or previously released versions.

On the `SAF Issues <https://github.com/ansys/saf/issues>`_ page, you can create
issues to report bugs and request new features.

Installation
------------

The ``ansys-solutions-dash-super-components`` package supports Python 3.11
through 3.14 on Windows and Linux.

Install the latest release from `PyPI
<https://pypi.org/project/ansys-solutions-dash-super-components/>`_ with:

.. code:: console

   pip install ansys-solutions-dash-super-components

Quick start
-----------

.. important::

   Dash Super Components use the ``callback`` decorator and other utilities from
   ``dash_extensions.enrich``. Your application **must** use
   ``dash_extensions.enrich.DashProxy`` instead of the standard ``dash.Dash``.
   Using ``dash.Dash`` directly causes the internal callbacks of the components
   to fail.

The following minimal example shows how to add the ``DualInputRangeSlider``
component to a Dash application:

.. code:: python

   import dash_mantine_components as dmc
   from dash import _dash_renderer
   from dash_extensions.enrich import DashProxy, html
   from ansys.solutions.dash_super_components import DualInputRangeSlider

   # Required for Dash 2.x
   _dash_renderer._set_react_version("18.2.0")

   app = DashProxy(__name__)

   app.layout = dmc.MantineProvider(
       children=[
           html.Div(
               [
                   DualInputRangeSlider(
                       aio_id="example-slider",
                       min=0,
                       max=100,
                       value=[20, 80],
                   )
               ],
               style={"padding": "40px"},
           )
       ]
   )

   if __name__ == "__main__":
       app.run(debug=True)

Run the example with ``python app.py`` and open ``http://127.0.0.1:8050`` in
your browser.

For detailed instructions on how to get started with Dash Super Components, see the
`getting started guide
<https://saf.ansys.com/version/stable/user_guide/frontend/dash/dash_super_components/dash_super_components_getting_started.html>`_
in the documentation.

For more complex examples, see the `showcase application
<https://github.com/ansys/saf/tree/main/packages/dash-super-components/examples/showcase_all>`_
in the repository.

Contributing
------------

Contributions are welcome! See the `contributing guide
<https://saf.ansys.com/version/stable/contribute/index.html>`_ for
developer installation instructions and guidelines on how to contribute code,
documentation, and examples to this project.

License
-------

This project is licensed under the Apache 2.0 License. For more information,
see the `LICENSE <LICENSE>`_ file.
