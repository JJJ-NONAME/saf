.. _beam_bending_tutorial_setup:

Setup
#####

.. topic:: Objective

  Create the backbone of your solution using ``saf-cli``, install the solution's Python virtual environment, and run the solution.

Create the solution
===================

To start working on your solution, generate a minimal solution from which you can build your own logic.

1. Start VS Code.

2. Click :menuselection:`File > Open Folder` and navigate to your preferred working directory.

3. Open a new terminal by clicking :menuselection:`Terminal > New Terminal`.

4. Create the solution with ``saf-cli`` using the following command:

   .. code:: bash

      saf new

- The command prompts you for a solution name. Enter ``simple-beam-bending`` and press :kbd:`Enter` to validate.
- The command prompts you for a solution display name. Enter ``Simple Beam Bending`` and press :kbd:`Enter` to validate.
- The command prompts you to select the UI framework. Select the default Plotly Dash option by pressing :kbd:`Enter`.

5. Verify that the current working directory contains a new folder named ``simple-beam-bending``.


Install the solution
====================

A solution app lives in its own virtual environment where the necessary packages are installed because:

- It allows the solution developer and the end user to run locally multiple solutions concurrently with different sets of requirements without getting dependency conflicts.
- It keeps the system Python interpreter clean.

Install the solution's development environment:

.. code-block:: bash

  saf install simple-beam-bending


Run the solution
================

At this stage, you can already run the solution derived from the template. To do so, run the following command:

.. code-block:: bash

  saf run simple-beam-bending

The solution UI opens in a desktop window:

.. image:: /_static/images/getting_started_minimal_solution_intro_page.png
    :align: center
    :width: 100%

