.. _beam_bending_tutorial_problem:

Problem
#######

.. topic:: Objective

    Review the problem to be solved: given a set of geometrical, material, and loading parameters, the goal of the application is to predict the deformed state of the beam subjected to a concentrated load `P`.

A solution application is designed to answer a given engineering problem. In this tutorial, we want to solve a classical problem in mechanical engineering:
the bending of a structure which can be approximated by a beam:

The parametrization of the problem is provided in the figure below:

.. figure:: /_static/images/beam_model.png

Geometrical parameters:
 * `l`: beam length.
 * `a`: distance of the load `P` with respect to the left support.
 * `b`: distance of the load `P` with respect to the right support.
 * `d`: diameter of the beam section.

Material parameters:
 * `E`: Young's modulus of elasticity.

Loading:
 * `P`: concentrated force.

Unknowns:
 * `x`: coordinate of the center of geometry of the beam center line along x axis in the deformed state.
 * `y`: coordinate of the center of geometry of the beam center line along y axis in the deformed state.
