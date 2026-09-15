.. _beam_bending_tutorial_logic:

Logic
#####

.. topic:: Objective

    Understand what business logic is and how to implement it in your solution.

The business logic refers to the methods that contain the knowledge to solve the engineering problem. This is the core
part of the solution. No business logic, no solution. In real world use cases leveraging Ansys products, the business
logic is often implemented using PyAnsys SDKs, such as PyMAPDL, PyAEDT, and so on.

In the case of the simple beam bending example, the business logic is very simple and does not require any Ansys SDKs.
It is implemented in a single Python function that calculates the beam deflection given the geometrical, material, and
loading parameters.

Implementation
==============

In this tutorial, you won't need to implement the business logic from scratch. It is provided to you.
What you need to pay attention to is where the business logic should be implemented in the solution.

We recommend that you implement any business logic in the ``logic`` directory of your solution.
a clean separation of concerns between the business logic and the rest of the solution.

.. note::

    The ``solution/scripts`` directory is reserved for scripts that contain the logic to be executed in HPS jobs.
    Check the `HPS job submission <https://saf.glow.docs.solutions.ansys.com/version/stable/user_guide/using_ansys_products/job_execution/index.html>`_ documentation for more information about HPS job submission.

.. practice::

    Download the ``beam_deflection`` module from the simple beam bending example repository:

    #. Go to the `beam_deflection.py <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/solution/logic/beam_deflection.py>`__ file in the simple beam bending example repository.

    #. Download the file by clicking the :bdg-primary:`Download raw file` button in the top right corner of the code block.

       .. image:: /_static/images/beam_bending_beam_deflection_download_raw_file_button.png
          :align: center
          :width: 100%
          :alt: Download raw file button

    #. Copy the downloaded file into the ``logic`` directory of your solution.

    Let's take a look at the code. Our business logic is implemented in the ``compute_beam_deflection`` function. The function takes
    the geometrical parameters (`a`, `b`, `d`), material parameters (`E`), and loading (`p`) as input arguments. The argument `n` is
    the number of points along the beam axis on which the deflection is computed.

    The function returns two lists containing the x and y coordinates of the beam centerline.

Testing
=======

It is crucial to test the business logic independently from the rest of the solution before going further. This is an important best
practice for solution developers. If you look at the bottom of the ``beam_deflection`` module, there is a simple test provided inside
the construct ``if __name__ == "__main__":``. This test is executed only when the module is run as a script.

This code will be executed when you run the module as a script. Let's test it.

.. practice::

    Using ``saf-cli``, run the following command to test the business logic:

    .. code:: bash

        saf execute simple-beam-bending "python src/ansys/solutions/simple_beam_bending/solution/logic/beam_deflection.py"

    If the test passes, you should see the following output:

    .. code:: bash

        Point 0: x = 0.00 mm, y = -0.0000 mm
        Point 1: x = 33.33 mm, y = -1.8444 mm
        Point 2: x = 66.67 mm, y = -3.4372 mm
        Point 3: x = 100.00 mm, y = -4.5271 mm
        Point 4: x = 133.33 mm, y = -4.9253 mm
        Point 5: x = 166.67 mm, y = -4.6947 mm
        Point 6: x = 200.00 mm, y = -3.9612 mm
        Point 7: x = 233.33 mm, y = -2.8504 mm
        Point 8: x = 266.67 mm, y = -1.4881 mm
        Point 9: x = 300.00 mm, y = -0.0000 mm

    The deformed state of the beam is defined for each point along the beam axis. The first point is the left support, the last point is the
    right support, and the points in between are the points along the beam axis where the deflection is computed. We can see that the deflection
    is null at the left and right supports, and it reaches a maximum value in the middle of the beam.

.. note::

    Check the guidelines for implementing business logic in your solution in the :ref:`best_practices_logic` section.

Key takeaways
=============

.. important::

    - The business logic is implemented in the ``logic`` directory of your solution.
    - The business logic must be modular and organized into dedicated Python modules based on functionality or domain responsibility.
    - The business logic must not contain any top-level code. This includes any logic that performs computations, file I/O, network calls, or data processing.
    - The business logic is tested independently from the rest of the solution before going any step further.
