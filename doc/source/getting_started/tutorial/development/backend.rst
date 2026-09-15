.. _beam_bending_tutorial_backend:

Backend
#######

.. topic:: Objective

    Build the solution application backend.

The solution application backend is the most important part of the solution where the core SAF's functionalities are implemented. It is
responsible for:

- Invoking the business logic
- Ensuring the business logic is cloud-compatible, that is, it can be executed in any type of environment (desktop, on-premises, or cloud)
- Interacting with the Ansys products or the job submission system (such as HPS)
- Establishing dependencies between fields
- Persisting the data in the database
- Generating a REST API for the solution backend from the Python code

Implementation
==============

All the code related to the solution application backend is located in the ``solution`` directory of your solution in ``src/ansys/solutions/simple_beam_bending``.

Solution definition
-------------------

The solution definition refers to the ``definition.py`` module located in the ``solution`` directory. It lists the steps of
the workflow. The minimal solution generated using ``saf-cli`` comes with a two-step solution definition: ``first_step`` and ``second_step``.

The code snippet below shows the solution definition:

.. code:: python

    from ansys.saf.glow.solution import Solution, StepsModel

    from ansys.solutions.simple_beam_bending.solution.first_step import FirstStep
    from ansys.solutions.simple_beam_bending.solution.second_step import SecondStep


    class Steps(StepsModel):
        """Workflow definition."""

        first_step: FirstStep
        second_step: SecondStep


    class SimpleBeamBendingSolution(Solution):
        """Solution definition."""

        display_name: str = "Simple Beam Bending"
        version: int = 1
        steps: Steps

The ``Steps`` class defines the workflow of the solution. ``FirstStep`` and ``SecondStep`` are ``StepModel`` classes
imported from the ``first_step.py`` and ``second_step.py`` modules, respectively. We will cover these classes in the
next sections.

Now, in our case, we only need a single step, called ``ComputeStep``. We could remove the ``second_step`` from the
solution definition and simply rename the ``first_step`` to ``compute_step``. However, these manual changes are potentially
error-prone. Instead, we will use the ``saf-cli`` to create a new step. Then we will remove the  ``FirstStep`` and ``SecondStep``.

.. practice::

    ``saf-cli`` provides a command to create a new step with its corresponding page. So it creates both the backend and frontend
    code.

    Run the following command in the terminal:

    .. code:: bash

        saf add-step simple-beam-bending --step-name compute_step --ui-framework dash

    Open the ``definition.py`` module in VS Code. You will see that the ``ComputeStep`` class is added to the solution
    definition as follows:

    .. code:: python

        from ansys.saf.glow.solution import Solution, StepsModel

        from ansys.solutions.simple_beam_bending.solution.first_step import FirstStep
        from ansys.solutions.simple_beam_bending.solution.second_step import SecondStep
        from ansys.solutions.simple_beam_bending.solution.compute_step import ComputeStep


        class Steps(StepsModel):
            """Workflow definition."""

            first_step: FirstStep
            second_step: SecondStep
            compute_step: ComputeStep


        class SimpleBeamBendingSolution(Solution):
            """Solution definition."""

            display_name: str = "Simple Beam Bending"
            version: int = 1
            steps: Steps

    .. tip::

        If you're having trouble, you can compare your code with the `reference implementation <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/solution/definition.py>`__.

    You are done with the solution definition. Now let's look at the setp models.

Solution steps
--------------

The solution definition defines the workflow of the solution, and the solution steps contains the backend logic of each step.
In this section, we will look at the ``ComputeStep`` class, in which we will implement the backend logic for the beam bending
problem.

Let's look into the ``compute_step.py`` module. Open the ``compute_step.py`` module in VS Code. You will see that the
``ComputeStep`` class is already implemented:

.. code:: python

    from ansys.saf.glow.solution import StepModel, StepSpec, transaction


    class ComputeStep(StepModel):
        """Step definition of the compute_step step."""

        first_arg: float = 0
        second_arg: float = 0
        result: float = 0

        @transaction(self=StepSpec(upload=["result"], download=["first_arg", "second_arg"]))
        def calculate(self) -> None:
            """Compute the sum of two numbers."""
            self.result = self.first_arg + self.second_arg

A step model is a class that inherits from the ``StepModel`` class imported from ``ansys.saf.glow``.
As a standard Python class, it can have attributes and methods. The attributes of the step model are called fields.
The fields can be of any type, including primitive types (int, float, str, etc.) and complex types (list, dict, etc.).
They are used to store the data of the step model.

In this tutorial, the fields correspond to the input and output parameters of the beam bending problem. In other words,
all the arguments and outputs of the ``compute_beam_deflection`` method defined in the business logic step before,
must be defined as fields in the step model.

.. practice::

    Check the ``compute_beam_deflection`` method in the ``business_logic.py`` module and create the corresponding fields in the
    ``ComputeStep`` class.

    .. dropdown:: Reveal the solution

        The attributes of the ``ComputeStep`` class should now look like this:

        .. code:: python

            class ComputeStep(StepModel):
                """Step definition of the compute_step step."""

                # Input parameters

                length_a: float = 1000  # mm
                length_b: float = 1000  # mm
                diameter: float = 50  # mm
                elasticity_modulus: float = 210e3  # MPa
                load: float = 10e3  # N
                nbr_of_pts: int = 100

                # Output parameters

                deflection: List = []  # [[mm], [mm]]

    .. tip::

        If you're having trouble, you can compare your code with the `reference implementation <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/solution/compute_step.py>`__.

    You might have noticed that for each field, we have defined the type. Indeed, SAF enforces the typing feature to
    control the data types of the fields. This is a good practice to ensure that the data is consistent. Creating a field
    without a type will result in a runtime error.

Now that we have defined the fields, let's invoke the business logic in the step model. Currently, the ``calculate`` method is
implemented. It is a basic example that computes the sum of two numbers. We will replace it with the call to the
``compute_beam_deflection`` method defined in the business logic module.

Note that the ``calculate`` method is decorated with the ``transaction`` decorator. The ``transaction`` decorator serves the
following purposes in solution code:

- Ensures that solution code is cloud-compatible
- Publishes the methods in the REST API (to be discussed later in the SAF essentials training)
- Establishes dependencies between fields.

A transaction method---that is a method decorated with the ``transaction`` decorator---is executed in an isolated environment to ensure cloud-compatibility.

.. practice::

    First, rename the ``calculate`` method to ``compute_beam_deflection``. It is a good practice to give a meaningful name to the
    methods, classes, and variables.

    .. code:: python

        @transaction(self=StepSpec(upload=["result"], download=["first_arg", "second_arg"]))
        def compute_beam_deflection(self) -> None:
            """Compute the sum of two numbers."""
            self.result = self.first_arg + self.second_arg

    Then, we need to import the ``compute_beam_deflection`` method from the business logic module. Add the following import
    statement at the top of the module (above the class definition):

    .. code:: python

        from ansys.solutions.simple_beam_bending.solution.logic.beam_deflection import compute_beam_deflection

    Now, we need to adjust the ``download`` and ``upload`` parameters of the ``transaction`` decorator. These parameters are used to
    specify the inputs to pull into this isolated execution environment and the outputs to push back to the Solution API Server.

    In our case, we need to pull all the input parameters and push the beam deflection parameter. Adjust the decorator accordingly.

    .. dropdown:: Reveal the solution

        The ``transaction`` decorator should now look like this:

        .. code:: python

            @transaction(
                self=StepSpec(
                    download=["length_a", "length_b", "diameter", "elasticity_modulus", "load", "nbr_of_pts"],
                    upload=["deflection"],
                )
            )
            def compute_beam_deflection(self) -> None: ...

    Finally, we need to call the ``compute_beam_deflection`` method in the corresponding transaction method. Adjust the body of the
    transaction method.

    .. dropdown:: Reveal the solution

        The ``compute_beam_deflection`` method should now look like this:

        .. code:: python

            @transaction(
                self=StepSpec(
                    download=["length_a", "length_b", "diameter", "elasticity_modulus", "load", "nbr_of_pts"],
                    upload=["deflection"],
                )
            )
            def compute_beam_deflection(self) -> None:
                """Method to compute the deflection of a simply supported beam."""
                self.deflection = compute_beam_deflection(
                    self.length_a, self.length_b, self.diameter, self.elasticity_modulus, self.load, n=self.nbr_of_pts
                )

    .. tip::

        If you're having trouble, you can compare your code with the `reference implementation <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/solution/compute_step.py>`_.

    Your backend implementation is now complete. You have defined the solution definition, the step model, and you have
    successfully invoked the business logic in a transaction method.


Testing (optional)
===================

SAF-based solutions follow a microservices architecture and so the backend and the frontend are
two separate services that communicate with each other using REST APIs. The backend is responsible for invoking the business logic, while the
frontend is responsible for the user interface.

Therefore, it is possible to test the backend without the frontend. To do this, we will run the solution without the frontend and use
the solution REST API to test the ``compute_beam_deflection`` transaction method.

.. warning::

    The next steps could be a bit disturbing if you're not familiar with a REST API Swagger UI. But don't worry—this section is optional. You
    can move on to the next part if things don't work as expected.

First we need to run the solution backend.

.. practice::

    Open a terminal and run the following command:

    .. code:: bash

        saf run simple-beam-bending --no-ui

    Watch the console output. At some point, you should see the following message:

    .. image:: /_static/images/rest_api_url.png
        :width: 60%
        :alt: REST API URL

    The solution API URL is highlighted in yellow in the figure above (``http://127.0.0.1:<port-number>/docs``). In the example,
    the port number is ``55481``. In your case, it might be different. Press :kbd:`Ctrl` and click the URL to open it in your
    browser or simply copy/past the URL in your favorite browser. You should see the following:

    .. image:: /_static/images/solution_api_swagger_ui.png
        :width: 100%
        :align: center

    This is the Swagger UI of the solution API. It is a web-based interface that allows you to interact with the REST API of the solution.

Now that the backend is running, we can interact with the REST API. The Swagger UI provides a list of endpoints of the solution API.
To test the backend, we first need to create a new project. Let's go.

.. practice::

    Click the :bdg-success:`POST` :bdg-success-line:`/projects Create Project` endpoint (second one in the list) in the projects section of the Swagger UI.
    You should see the following:

    .. image:: /_static/images/click_create_project_endpoint.png
        :width: 100%
        :align: center

    This endpoint is used to create a new project. Click the :guilabel:`Try it out` button.
    You should see the following:

    .. image:: /_static/images/click_create_project_endpoint_try_it_out.png
        :width: 100%
        :align: center

    The request body is a JSON object that contains the project display name. By default, the project name is set to ``"test project"``.
    You can keep it or change it. To change it, click the text box and replace ``"test project"`` with your own project name. Here
    is how it looks like for a project named ``"my custom project"``:

    .. code:: json

        {
            "display_name": "my custom project"
        }


    Then click the :guilabel:`Execute` button. You should see the following:

    .. image:: /_static/images/run_create_project_endpoint.png
        :width: 100%
        :align: center

    The response body is a JSON object that contains the project ID. The project ID is a unique identifier.
    It corresponds to the alphanumeric string located after the ``projects/`` prefix in the values of the ``name`` key as per the
    image below.

    .. image:: /_static/images/create_project_response_body.png
        :width: 50%
        :alt: Create project response body

    Copy the project ID of your project. We will use it in the next step.

With a project created, we can now interact with the compute step. First, we will check the current values of the deflection field.

.. practice::

    Scroll down to the ``steps`` section and click the :bdg-primary:`GET` :bdg-primary-line:`/projects/{project_id}/steps/compute-step Get step`
    endpoint (third :bdg-primary:`GET` endpoint starting from the top). You should see the following:

    .. image:: /_static/images/click_get_step_endpoint.png
        :width: 100%
        :align: center

    Now click the :guilabel:`Try it out` button and paste the project ID in the ``project_id`` text box.
    Then click the :bdg-primary:`Execute` button.
    You should see the following:

    .. image:: /_static/images/get_compute_step_first_time_response_body.png
        :width: 100%
        :align: center
        :alt: Get compute step first time response body

    The response body is a JSON object that contains the current values of the fields of the compute step.
    You can see that the ``deflection`` field is an empty list which is expected since we haven't run the transaction yet.

Now we are all set to run the transaction.

.. practice::

    Click the :bdg-success:`POST` :bdg-success-line:`/projects/{project_id}/steps/compute-step:compute-beam-deflection Invoke Method` endpoint.
    As before, click the :guilabel:`Try it out` button, past the project ID in the ``project_id`` text box and click the
    :guilabel:`Execute` button. You should see the following:

    .. image:: /_static/images/solution_api_compute_beam_deflection_post_endpoint.png
        :width: 100%
        :align: center
        :alt: Solution API compute beam deflection POST endpoint

    After clicking on the :guilabel:`Execute` button, you should see an empty response body. This is expected since the
    ``compute-beam-deflection`` method does not return anything. However, the transaction has been executed successfully.

    Now let's check the values of the fields again. Scroll up to the ``steps`` section and repeat the same steps as before to call the
    :bdg-primary:`GET` :bdg-primary-line:`/projects/{project_id}/steps/compute-step Get step` endpoint. You should see the following:

    .. image:: /_static/images/get_compute_step_after_running_the_transaction.png
        :width: 100%
        :align: center

    You can see that the ``deflection`` field is now populated with the values of the beam deflection. The transaction has been executed successfully.
    The SAF backend is now fully functional and ready to be used.

Key takeaways
=============

.. important::

    - The solution application backend implementation occurs in the ``solution`` directory of your solution.
    - SAF enforces the typing feature to control the data types of the fields. Each field must have a type.
    - The backend can be tested without the frontend using the REST API.
    - The ``transaction`` decorator is used to ensure that the solution code is cloud-compatible and to establish dependencies between fields.
    - The backend is responsible for invoking the business logic and persisting the data in the SAF database.
    - Just like the business logic, it is important to test the backend independently from the frontend.
