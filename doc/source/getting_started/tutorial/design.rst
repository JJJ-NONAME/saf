.. _beam_bending_tutorial_design:

Design
######

.. topic:: Objective

  Define the number of steps and the components to be used in the workflow, as well as the
  the user experience (UX) you want to deliver.

Workflow definition
===================

Prior to any coding activity, it is important to think about the design of the solution:

* How many steps?
* Are Ansys flagship products involved? If so, how does the business logic connect with them?
* Are you using the product APIs? Can you use PyAnsys APIs instead?
* Are in-house solvers involved?
* Do you need 3D visualization capabilities?

.. tip::
    Address as many of these questions as possible early in the development cycle so you can identify potential blocking points and make the best decisions in terms of components.

For the ``simple-beam-bending`` problem, there is a single **Compute** step which exposes the input parameters and displays the output in a graph.
When you sketch the workflow in terms of components, you get a very simple process:

.. image:: /_static/images/solution_workflow_2.png
  :width: 75%
  :align: center

No Ansys flagship product is involved. You want to solve the beam bending problem with a homemade :dfn:`solver`, which is a simple implementation of the analytical solution according to Euler-Bernoulli Beam Theory. Therefore, :dfn:`custom solver` refers to the component containing this implementation.

UI/UX
=====

As part of the design process, you need to start thinking about the user experience you want to deliver. There are many tools that you can use to
create the sketches. One of these is simply **PowerPoint**. It is accessible and it can deliver realistic drafts. After several discussions with
your customer, you come up with the following design:

.. image:: /_static/images/ui_mockup_step_2.png
  :width: 100%

.. only:: internal

  .. tip::
    Draw drafts of the user interface and iterate with the development team and the customer until you converge on a satisfying design.
