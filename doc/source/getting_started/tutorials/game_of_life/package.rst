.. _game_of_life_package:

Phase 5 — Package
#################

.. topic:: Objective

    Turn your working ``game-of-life`` solution into a **standalone desktop installer** that a
    colleague can double-click to install and run — no Python interpreter, no ``saf-cli``, no
    ``poetry install`` required on the target machine.

Why package the solution?
=========================

Up to this point you have been running the solution from source with ``saf run``. That is
perfect for development but it assumes the target machine has:

- a compatible Python interpreter,
- the SAF CLI installed,
- network access to every dependency,
- and a copy of your source tree.

Real end users have none of that. SAF ships ``saf build``, a one-shot command that packages the
solution — code, Python interpreter and every dependency — into a single Windows executable
installer. The end user runs the ``.exe``, clicks through a Next / Next / Finish wizard, and
lands on a working desktop app.

.. tip::

    The command is Dash-specific. It builds a desktop installer for solutions scaffolded with
    ``--ui-framework dash`` (which is what you did in :ref:`phase 1 <game_of_life_initialization>`).
    Streamlit and headless solutions have their own packaging paths.

Prerequisites
=============

The build command needs an installed solution to package. If you skipped ``saf install`` earlier,
run it now:

.. code-block:: bash

    saf install game-of-life -f

The ``-f`` flag forces a clean re-install of the virtual environment — recommended before a
release build to make sure the dependency graph is fresh.

Build the installer
===================

You have two knobs to think about before you build: **online vs offline installer**, and
**development vs release build**.

Online vs offline installer
---------------------------

- **Online installer (default)**: small ``.exe`` that downloads dependencies from the internet
  at install time. Perfect for internal distribution to machines that have network access.
- **Offline installer** (``--offline-package``): larger ``.exe`` that embeds every wheel it
  needs and installs without any network call. Choose this when your users sit behind an
  air-gapped firewall or you need a truly self-contained artifact.

Development vs release build
----------------------------

- **Development build** (``--display-console-window``): keeps a console window open next to
  the app so you can see logs and tracebacks. Use it while you are still ironing out bugs.
- **Release build** (default, no flag): hides the console window. Use it for anything you send
  to end users.

.. practice::

    From the root of the ``game-of-life`` folder, build a **development installer** first — the
    console window makes any post-install issue trivial to diagnose:

    .. code-block:: bash

        saf build game-of-life --display-console-window

    The build takes a few minutes. When it succeeds, ``saf-cli`` prints the absolute path to the
    generated installer. It sits under the ``dist/`` (or equivalent) directory of your
    solution.

    Then, once you are happy with the result, build the **release installer** you will ship:

    .. code-block:: bash

        saf build game-of-life

    Or, for a fully self-contained artifact:

    .. code-block:: bash

        saf build game-of-life --offline-package

Test the installer
==================

Never ship an installer you have not smoke-tested yourself.

.. practice::

    #. Locate the generated ``.exe`` printed at the end of the ``saf build`` command.

    #. Copy it to a **clean** location — ideally a virtual machine or a second workstation that
       does not have your development environment. This is the only way to catch missing
       dependencies that happen to be pre-installed on your dev machine.

    #. Double-click the installer and follow the wizard. Default install location is:

       .. code-block:: text

           C:\Program Files\ANSYS Inc\SAF Solutions\Game of Life Solution\1\

    #. Launch the newly-installed solution from the Start menu (or from its desktop shortcut,
       depending on your wizard choices).

    #. Reproduce the full end-to-end flow from :ref:`phase 4 <game_of_life_frontend>`:

       - Pick a couple of patterns and verify the heatmap redraws.
       - Move the grid-size slider and verify the heatmap redraws.
       - Click **Start simulation**, wait for the run to complete, and verify the completion
         notification.

    If any of that fails, the ``--display-console-window`` build you produced first will show
    the traceback. Fix the issue, rebuild, retest.

Where to go from here
=====================

Congratulations — you now have a fully functional, distributable SAF solution. Here are three
natural next steps to keep expanding your SAF fluency:

- :ref:`installer` — the full reference for ``saf build``, including options for encrypting or
  obfuscating your source code, excluding the Python interpreter, or bundling as a directory
  when the installer exceeds the 4 GB single-file limit.
- :ref:`user_guide` — dive deeper into the SAF concepts you touched in this tutorial (product
  instances, BDM storage, HPS job submission, testing, deployment).
- The examples gallery in ``examples/src/saf/solutions/examples/`` on the
  `SAF examples repository <https://github.com/ansys/saf>`_ — a growing library of small,
  focused solutions that showcase one SAF feature at a time.

Key takeaways
=============

.. important::

    - ``saf build <solution-name>`` produces a **standalone Windows installer** that bundles
      the solution, its dependencies, and a Python interpreter.
    - The command only works for **Dash-based** solutions.
    - Use ``--offline-package`` when the target machine is offline or air-gapped.
    - Use ``--display-console-window`` during development to see logs and tracebacks; drop the
      flag for release builds so end users don't see a stray console window.
    - Always test the generated installer on a **clean machine** before distributing it — that
      is the only reliable way to catch missing dependencies that happen to be installed
      globally on your development workstation.
    - See :ref:`installer` for advanced options (encryption, obfuscation, custom entry points,
      excluding Python, and more).