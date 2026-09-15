.. _beam_bending_tutorial_frontend:

Frontend
########

.. topic:: Objective

    Build the Dash frontend.

SAF is frontend agnostic. The frontend can be built using any web framework. In this tutorial, we will use Plotly Dash, a web application
framework for Python. Dash is built on top of Flask, Plotly.js, and React.js. It is designed to make it easy to build interactive web
applications in Python.

Implementation
==============

All the code related to the Plotly Dash frontend is located in the ``ui`` directory of your solution in ``src/ansys/solutions/simple_beam_bending``.

Layout
------

By default, the solution generated with ``saf-cli`` contains three pages: ``about_page.py``, ``first_page.py``, and ``second_page.py``. In this tutorial,
we will build a two step app:

1. The first page will be called the **About** page and will contain a description of the problem. No user interaction there. Only static content.
2. The second page will be called the **Compute** page, and will contain the input form for the user to enter the parameters of the beam bending problem and a button to compute the solution.

In this tutorial, we will focus on the **Compute** page as it contains the key concepts to understand how to build the frontend and interact with the backend. The about page is just static
content and does not require any user interaction. So we will copy the content of the **About** page from the reference repository directly, just like we did in the business logic stage.

About page
~~~~~~~~~~

.. practice::

    #. Go to the `about_page.py <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/ui/pages/about_page.py>`__ file in the simple beam bending example repository.

    #. Download the file by clicking the :bdg-primary:`Download raw file` button in the top right corner of the code block.

       .. image:: /_static/images/beam_bending_about_page_download_raw_file_button.png
          :align: center
          :width: 100%
          :alt: Beam bending About page download raw file button

    #. Delete the existing ``about_page.py`` file in the ``ui/pages`` directory of your solution.

    #. Copy the downloaded file into the ``ui/pages`` directory of your solution.

The **About** page is now ready. Let's move on to the **Compute** page.

Compute page
~~~~~~~~~~~~

As mentioned in the backend stage, the ``saf add-step`` command creates simultaneously the backend and the frontend code.
So you should have a file named ``compute_page.py`` already created for you.

Instead of asking you to build a complete Dash UI from scratch---which can be overwhelming if you're just getting started---we're
taking a guided, hands-on approach. We've prepared a nearly complete ``compute_page_incomplete.py`` for you. This page has everything structured and
laid out, but some key pieces are intentionally left out.

.. practice::

    #. Go to the `compute_page_incomplete.py <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/ui/pages/compute_page_incomplete.py>`__ file in the simple beam bending example repository.

    #. Download the file by clicking the :bdg-primary:`Download raw file` button in the top right corner of the code block just like you did for the about page before.

    #. Copy the downloaded file into the ``ui/pages`` directory of your solution.

    #. Delete the original ``compute_page.py`` file in the ``ui/pages`` directory of your solution.

    #. Rename the downloaded file to ``compute_page.py``.

Let's open ``compute_page.py``.

.. practice::

    Open the ``compute_page.py`` file in the ``ui/pages`` directory of your solution. The file is organized in three blocks:
    ``imports``, ``layout``, and ``callbacks``.

    .. code-block:: text

        # Imports
        import base64
        import os
        ...

        # Layout
        def layout(step: ComputeStep) -> html.Div:
            ...

        # Callbacks
        @callback(
            ...
        )
        def compute_beam_deflection(...) -> Tuple[dict, bool]:
            ...

    The ``imports`` block contains the necessary imports for the page---that is, the libraries and modules that are used in the page.
    The ``layout`` block contains the layout of the page---that is, the HTML elements that are displayed on the page.
    The ``callbacks`` block contains the interactivity of the page---that is, the functions that are called when the user interacts with the page.

Remember that we want to build a page following the mock-up below:

.. image:: /_static/images/ui_mockup_step_2.png
    :width: 100%

The layout is divided into two equally sized width sections. The left section contains the input form and the right section contains the
beam sketch and the output graph.

Look at the ``layout`` function. It has a set of variables defined before the return statement. Each variable corresponds to a specific component
or group of component that will be displayed on the page. For instance, ``geometrical_parameters_form`` will expose the geometrical parameters of
the beam. ``material_properties_form`` will expose the material properties of the beam.

It is a good practice to created variables for each component or a small group of components instead of creating the components directly in the
return statement. This makes the code more readable and easier to maintain. Otherwise, you will end up with a huge return statement that is hard
to read and understand.

.. code-block:: python

    def layout(step: ComputeStep) -> html.Div:
        """Layout of the compute page."""

        # Left side of the page -------------------------------------------------------------------------------------------

        geometrical_parameters_form = ...

        # TODO: Create the material properties form. Tip: just copy the geometrical parameters form and change the labels and ids.
        material_properties_form = ...

        ...

        # Right side of the page ------------------------------------------------------------------------------------------

        beam_bending_sketch = ...

        image_card = ...

        ...

        return ...


To ease the understanding of the code, some comments have been added. All the variables related to the left-side of the page are located under the
``# Left side of the page`` comment. Similarly, all the variables related to the right-side of the page are located under the ``# Right side of the page``
comment.

The code placed in the return statement is the effective layout. It takes all the variables defined before and arrange them in a specific order to match
the expected layout. Let's look into it below.

It starts with the ``html.Div`` element, which is the main container of the page. Think of it as the main box that contains all the other components. The
``html.Div`` square brackets ``[...]`` contains the list of components that will be displayed on the page. The first two components are the title ``html.H1``
and the subtitle of the page ``html.P``.

A little further down, you can see the ``dmc.Grid`` component. This is a grid layout that divides the page into two columns. The first ``dmc.Col`` contains
the left side of the page, and the second ``dmc.Col`` contains the right side of the page. The ``span=6`` argument means that each column will take half of
the available width.

.. code-block:: python

    return html.Div(
        [
            html.H1("Compute beam deflection", className="display-3", style={"font-size": "35px"}),
            html.P(
                "Compute beam deflection using Euler-Bernoulli Theory.",
                className="lead",
                style={"font-size": "20px"},
            ),
            html.Hr(className="my-2"),
            html.Br(),
            dmc.Grid(
                [
                    dmc.Col(
                        [
                            geometrical_parameters_form,
                            # TODO: Add the material properties form.
                            # TODO: Add the loading parameters form.
                            # TODO: Add the numerical parameters form.
                            # TODO: Add the compute button.
                        ],
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "10px",
                        },
                        span=6,
                    ),
                    dmc.Col(
                        [image_card, graph],
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "20px",
                        },
                        span=6,
                    ),
                ],
                gutter="xs",
            ),
            dcc.Loading(
                type="circle",
                fullscreen=True,
                color="#ffb71b",
                style={
                    "background-color": "rgba(55, 58, 54, 0.1)",
                },
                children=html.Div(id="wait-for-completion"),
            ),
        ]
    )

Let's customize the :file:`compute_page.py`. You'll find comments starting with ``# TODO`` marking the places
where you need to fill in the missing code. Let's start with the left side of the page. The first component
is the geometrical parameters form.

.. code-block:: python

    geometrical_parameters_form = InputForm(
        [
            {
                "label": "a",
                "fields": [
                    {
                        "type": "NumberInput",
                        "value": step.length_a,
                        "min": 0,
                        "id": "length-a",
                        "required": True,
                    }
                ],
                "unit": "mm",
            },
            # TODO: Add the input components for length_b and diameter. Tip: look at the length_a implementation and repeat it.
        ],
        id="geometrical-parameters-form",
        title="Geometrical parameters",
        columns=["label", "fields", "unit"],
    )

The code above indicates that the geometrical parameters form is defined using the ``InputForm`` component which is a custom
component that is part of the ``dash-super-components`` library. ``dash-super-components`` is an Ansys library that provides
a set of components to quickly build Dash applications. These components encapsulate a set of Dash components to provide a more
user-friendly interface and save you time when building your application.

``InputForm`` takes a list of dictionaries as input. Each dictionary represents a row in the form. In the code snippet above, the
geometrical parameter ``a`` is defined. The ``label`` key corresponds to the name of the parameter to be displayed in the form. The
``fields`` key corresponds to the list of Dash components that will be displayed in the row. As ``a`` is a number, the Dash component used is
``NumberInput`` from the Dash Mantine library.

The ``value`` key corresponds to the default value of the component. Remember that we declared the default value of ``a`` in the backend.
Therefore, ``value`` is set to ``step.length_a``, ``step`` being the argument of the ``layout`` function. Here you have an example of a
backend/frontend interaction.

When building Dash applications, each component must have a unique identifier. This is done using the ``id`` key. In the example above,
the ID is set to ``length-a``. The ``required`` key indicates whether the field is required or not. In this case, it is set to ``True``.

.. practice::

    Now it is your turn to add the input components for the other geometrical parameters. Add an entry for ``length_b`` and ``diameter`` in the
    ``geometrical_parameters_form``.

    .. dropdown:: Reveal the solution

        .. code:: python

            geometrical_parameters_form = InputForm(
                [
                    {
                        "label": "a",
                        "fields": [
                            {
                                "type": "NumberInput",
                                "value": step.length_a,
                                "min": 0,
                                "id": "length-a",
                                "required": True,
                            }
                        ],
                        "unit": "mm",
                    },
                    {
                        "label": "b",
                        "fields": [
                            {
                                "type": "NumberInput",
                                "value": step.length_b,
                                "min": 0,
                                "id": "length-b",
                                "required": True,
                            }
                        ],
                        "unit": "mm",
                    },
                    {
                        "label": "d",
                        "fields": [
                            {
                                "type": "NumberInput",
                                "value": step.diameter,
                                "min": 0,
                                "id": "diameter",
                                "required": True,
                            }
                        ],
                        "unit": "mm",
                    },
                ],
                id="geometrical-parameters-form",
                title="Geometrical parameters",
                columns=["label", "fields", "unit"],
            )

        We added two dictionaries to the ``InputForm`` list. The first one is for the length ``b`` and the second one is for the diameter ``d``.
        Both components are of type ``NumberInput``. The ``value`` key is set to the default value of the parameter in the backend. The ``id`` key is set to
        ``length-b`` and ``diameter`` respectively. The ``required`` key is set to ``True`` for both components.

    .. tip::

        If you're having trouble, you can compare your code with the `reference implementation <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/ui/pages/compute_page.py>`__.

    Well done. The geometrical parameters form is now ready.

Let's continue the layout customization. The next component is the material properties form.

.. practice::

    You have seen an example of how to create a form using the ``InputForm`` component. Now it is your turn to create
    the material properties form. Remember that the only material property we need is the elasticity modulus.

    Find the ``material_properties_form`` placeholder code and fill the missing code.

    .. code-block:: python

       # TODO: Create the material properties form. Tip: just copy the geometrical parameters form and change the labels and ids.
       material_properties_form = ...

    Pay attention to each property of the form. You need to adjust the ``title``, the ``id``, and of course the list of entries
    in the form.

    .. dropdown:: Reveal the solution

        .. code:: python

            materials_properties_form = InputForm(
                [
                    {
                        "label": "Elasticity Modulus",
                        "fields": [
                            {
                                "type": "NumberInput",
                                "value": step.elasticity_modulus,
                                "min": 0,
                                "id": "elasticity-modulus",
                                "required": True,
                            }
                        ],
                        "unit": "MPa",
                    },
                ],
                id="material-properties-form",
                title="Material properties",
                columns=["label", "fields", "unit"],
            )

        We created a form with a single entry for the elasticity modulus. The ``label`` is set to ``Elasticity Modulus``. The ``id`` is set to
        ``elasticity-modulus``. The ``value`` is set to the default value of the parameter in the backend. The ``unit`` is set to ``MPa``.

    .. tip::

        If you're having trouble, you can compare your code with the `reference implementation <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/ui/pages/compute_page.py>`__.

    Well done. The material properties form is now ready.

Let's continue the layout customization. The next components are: the loading parameters form and the numerical parameters form.

.. practice::

    Same as before, let's finalize the input forms with the last two remaining. Start with the loading parameters form.

    .. code-block:: python

        # TODO: Create the loading parameters form. Tip: just copy the geometrical parameters form and change the labels and ids.
        loading_parameters_form = ...

    .. dropdown:: Reveal the solution

        .. code:: python

            loading_parameters_form = InputForm(
                [
                    {
                        "label": "Concentrated Force",
                        "fields": [
                            {
                                "type": "NumberInput",
                                "value": step.load,
                                "min": 0,
                                "id": "load",
                                "required": True,
                            }
                        ],
                        "unit": "N",
                    },
                ],
                id="loading-parameters-form",
                title="Loading parameters",
                columns=["label", "fields", "unit"],
            )

        We created a form with a single entry for the concentrated force. The ``label`` is set to ``Concentrated Force``. The ``id`` is set to
        ``load``. The ``value`` is set to the default value of the parameter in the backend. The ``unit`` is set to ``N``.

    Continue with the numerical parameters form.

    .. code-block:: python

        # TODO: Create the numeriacl parameters form. Tip: just copy the geometrical parameters form and change the labels and ids.
        numerical_parameters_form = ...

    .. dropdown:: Reveal the solution

        .. code:: python

            numerical_parameters_form = InputForm(
                [
                    {
                        "label": "Number of points",
                        "fields": [
                            {
                                "type": "NumberInput",
                                "value": step.nbr_of_pts,
                                "min": 0,
                                "id": "nbr-of-pts",
                                "required": True,
                            }
                        ],
                        "unit": None,
                    },
                ],
                id="numerical-parameters-form",
                title="Numerical parameters",
                columns=["label", "fields", "unit"],
            )

        We created a form with a single entry for the number of points. The ``label`` is set to ``Number of points``. The ``id`` is set to
        ``nbr-of-pts``. The ``value`` is set to the default value of the parameter in the backend. The ``unit`` is set to ``None`` as there
        is no unit for this parameter.

    .. tip::

        If you're having trouble, you can compare your code with the `reference implementation <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/ui/pages/compute_page.py>`__.


    Well done. The loading parameters form and the numerical parameters form are now ready.

We are almost done with the left side of the page. The last component is the compute button. Let's go.

.. practice::

    The compute button is a simple button that will trigger the computation of the beam deflection. Let's create it
    using the ``dmc.Button`` component from the Dash Mantine library.

    Visit the `Dash Mantine documentation <https://dmc-docs-0-12.onrender.com/components/button>`__ to see the available options for the button.
    You will find a couple of examples there.

    Replace the placeholder code with a working code.

    .. code-block:: python

        # TODO: Create the compute button. Tip: visit https://dmc-docs-0-12.onrender.com/components/button for inspiration.
        compute_button = dmc.Button(...)

    .. dropdown:: Reveal the solution

        .. code:: python

            compute_button = dmc.Button(
                "Compute",
                id="compute-deflection",
                color="blue",
                size="xl",
                style={
                    "width": "60%",
                    "margin": "auto",
                },
            )

        The first argument is the label of the button. The ``id`` is set to ``compute-deflection``. The component has other properties for
        customization.

    .. tip::

        If you're having trouble, you can compare your code with the `reference implementation <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/ui/pages/compute_page.py>`__.

    Well done. The left side of the page is now ready.

The layout of the right side of the page is already done for you. The layout of the **Compute** page is therefore ready.
Now we need to add the interactivity to the page, that is, trigger the ``compute_beam_deflection`` transaction
method when the user clicks on the compute button.

Interactivity
-------------

Interactivity in Dash is done using callbacks. A callback is a function that is called when a specific event occurs.
In our case, we want to call the ``compute_beam_deflection`` function when the user clicks on the compute button.

Look at the code of the callback function at the bottom of the file.

.. code-block:: python

    @callback(
        Output(...),
        Input(...),
        State(...),
    )
    def compute_beam_deflection(*args, **kwargs) -> Tuple[dict, bool]: ...

The callback decorator defines the inputs and outputs of the callback function. The inputs are the events that will
trigger the callback. The outputs are the properties of the components that will be updated when the callback will
complete.

Inputs are defined using the ``Input`` class. The ``Input`` class takes two arguments: the ID of the component and
the property of the component that will be used as input.

Outputs are defined using the ``Output`` class. Similarly to the ``Input`` class, the ``Output`` class takes two arguments:
the ID of the component and the property of the component that will be updated when the callback completes.

There is another class called ``State``. The ``State`` class is used to read the current state of a property of a component.
The key difference between ``Input`` and ``State`` is that the ``Input`` class will trigger the callback when the property changes,
whereas the ``State`` class will not trigger the callback. It only reads the current state of the property.

You can use as many inputs, states and outputs as you want. However there are two rules to follow:

1. The number of inputs and states declared in the callback decorator must match the number of inputs and states in the function signature.
   So whenever you add an input or a state in the decorator, you need to add the corresponding argument in the function signature.

2. The number of outputs declared in the callback decorator must match the number of items returned in the return statement of the function.

First let's fix the inputs and states of the callback.

.. practice::

    If you look at the callback decorator, there is an ``Input`` entry available. We want to configure it to trigger
    the callback when the user clicks on the compute button. As mentioned before, ``Input`` takes two arguments:
    the ID of the component and the property of the component that will be used as input. So we are expecting to see
    something like this:

    .. code-block:: python

        Input("<component-id>", "<property>")

    In our case the component ID is the ID of the compute button. The property we want to use as input is the ``n_clicks`` property.
    Adapt the code in the callback decorator to match this.

    .. dropdown:: Reveal the solution

        .. code:: python

            Input("compute-deflection", "n_clicks"),

    Now let's add all the states. Why do we need the states entries in the first place? We need them because those values
    are susceptible to change when the user interacts with the page.

    You can see that the first state is already there. It corresponds to the ``a`` parameter of the geometrical parameters form.

    .. code-block:: python

        State(
            {"form_id": "geometrical-parameters-form", "type": f"input-form-numberinput-field", "index": "length-a"}, "value"
        ),

    Don't be scared by the apparent complexity of the code above. Just like ``Input``, ``State`` takes two arguments: the ID of
    the component and the property of the component that will be used as input. In this case the ID is not a simple string, but a
    dictionary. This is because the ``InputForm`` component is leveraging the ``pattern-matching`` feature of Dash.

    You don't need to understand how it works for now. Just know that the ID of the component is a dictionary and that the
    ``value`` property is the one we want to use as input. So the explanation of the code above is that we are using the
    ``value`` property of the ``length-a`` field of the ``geometrical-parameters-form`` form. That's it.

    Now it is your turn to add the other states. Based on the existing example, replace all the empty states ``State(...)`` with
    a proper state.

    .. dropdown:: Reveal the solution

        .. code:: python

            @callback(
                # TODO: Add the output entry for the deflection graph.
                Output(...),
                Output("wait-for-completion", "children"),
                Input("compute-deflection", "n_clicks"),
                State(
                    {"form_id": "geometrical-parameters-form", "type": f"input-form-numberinput-field", "index": "length-a"},
                    "value",
                ),
                State(
                    {"form_id": "geometrical-parameters-form", "type": f"input-form-numberinput-field", "index": "length-b"},
                    "value",
                ),
                State(
                    {"form_id": "geometrical-parameters-form", "type": f"input-form-numberinput-field", "index": "diameter"},
                    "value",
                ),
                State(
                    {"form_id": "material-properties-form", "type": f"input-form-numberinput-field", "index": "elasticity-modulus"},
                    "value",
                ),
                State({"form_id": "loading-parameters-form", "type": f"input-form-numberinput-field", "index": "load"}, "value"),
                State(
                    {"form_id": "numerical-parameters-form", "type": f"input-form-numberinput-field", "index": "nbr-of-pts"},
                    "value",
                ),
                State("url", "pathname"),
                State("deflection-graph", "figure"),
                prevent_initial_call=True,
            )
            def callback_stub(*args): ...

    We are almost done. The last thing to do is to update the argument of the function to match the inputs and states we just added. Look
    at the function signature.

    .. code-block:: python

        def compute_beam_deflection(
            n_clicks: int,
            length_a: float,
            # TODO: Add the argument for the length-b parameter. Tip: look at the length-a implementation and repeat it.
            # TODO: Add the argument for the diameter parameter. Tip: look at the length-a implementation and repeat it.
            # TODO: Add the argument for the elasticity modulus parameter. Tip: look at the length-a implementation and repeat it.
            # TODO: Add the argument for the loading parameter. Tip: look at the length-a implementation and repeat it.
            # TODO: Add the argument for the numerical parameter. Tip: look at the length-a implementation and repeat it.
            pathname: str,
            figure: dict,
        ) -> Tuple[dict, bool]: ...

    You can see that the function takes the ``n_clicks`` argument. This is the input we just added. ``length_a`` corresponds to the
    first state. Now for each of the other states, you need to add the corresponding argument in the function signature. Try to use
    meaningful names for the arguments.

    .. dropdown:: Reveal the solution

        .. code:: python

            def compute_beam_deflection(
                n_clicks: int,
                length_a: float,
                length_b: float,
                diameter: float,
                elasticity_modulus: float,
                load: float,
                nbr_of_pts: int,
                pathname: str,
                figure: dict,
            ) -> Tuple[dict, bool]: ...

        If you're having trouble, you can compare your code with the `reference implementation <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/ui/pages/compute_page.py>`__.


Well done. The inputs and states of the callback are now ready.

First let's fix the outputs of the callback.

.. practice::

    Hopefully, the number of outputs is not that big. There are two outputs in the callback decorator. The first one
    corresponds to the deflection graph. Indeed, whenever a new computation is triggered, we want to update the graph
    with the new results, so that the user can see the new deflection of the beam. The second one corresponds to the
    ``dcc.Loading`` component that we did not discuss yet. This component is used to display a loading spinner while
    the computation is in progress.

    Just like ``Input`` and ``State``, ``Output`` takes two arguments: the ID of the component and the property of the
    component that will be updated when the callback completes. In this case, the property we want to update is the
    ``figure`` property of the graph. Now edit the code in the callback decorator to add the output entry for the
    deflection graph.

    .. dropdown:: Reveal the solution

        .. code:: python

            Output("deflection-graph", "figure"),

    Don't forget to edit the ``return`` statement of the function to match the output we just added. The return statement
    should look like this:

    .. code-block:: python

        return (figure, True)

    .. tip::

        If you're having trouble, you can compare your code with the `reference implementation <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/ui/pages/compute_page.py>`__.

The callback decorator is now well defined. What's left to do is to implement the function body.
The function body is where the magic happens. This is where we will call the backend transaction method to compute the
deflection of the beam.

Look at the first two lines of the function body.

.. code-block:: python

    project = DashClient[Simple_Beam_BendingSolution].get_project(pathname)
    step = project.steps.compute_step

``DashClient`` is a class that allows you to access the backend of the application.
``Simple_Beam_BendingSolution`` is the name of the solution definition we are working on. ``get_project`` is a method
that allows you to get the current project and to interact with the steps.

The ``step`` variable is the object that contains all the fields and methods we implemented in the backend stage.
Look a this line:

.. code-block:: python

    step.length_a = length_a

We are assigning the value of the ``length_a`` argument to the ``length_a`` field of the ``step`` object. This is how we
update the value of the field in the backend. We need to do this for all the parameters we want to update.

.. practice::

    Replace the placeholder code with the code that updates the values of the parameters in the backend.

    .. dropdown:: Reveal the solution

        .. code:: python

            project = DashClient[Simple_Beam_BendingSolution].get_project(pathname)
            step = project.steps.compute_step
            step.length_a = length_a
            step.length_b = length_b
            step.diameter = diameter
            step.elasticity_modulus = elasticity_modulus
            step.load = load
            step.nbr_of_pts = nbr_of_pts

    .. tip::

        If you're having trouble, you can compare your code with the `reference implementation <https://github.com/ansys/simple-beam-bending/blob/main/src/ansys/solutions/simple_beam_bending/ui/pages/compute_page.py>`__.

    Well done. The parameters are now updated in the backend.

The next critical line of code is that one:

.. code-block:: python

    step.compute_beam_deflection()

Remember that we implemented the ``compute_beam_deflection`` method in the backend. This is a transaction method that will
invoke the business logic. It is a synchronous method that will block the execution of the code until the computation is
finished. If the transaction is successful, the ``deflection`` field of the ``step`` object will be updated with the
new coordinates of the deflected beam. Further down in the code, you can see that we are using the ``deflection`` field to
update the graph.

Clean-up
--------

There is one remaining step to do before we can test the application. We need to clean up the code a little bit.
We need to get rid of all the files that are not needed anymore. This includes:

- For the frontend: the ``first_page.py`` and ``second_page.py`` located in the ``ui/pages`` directory.
- For the backend: the ``first_step.py`` and ``second_step.py`` files located in the ``solution`` directory.

.. practice::

    Deleted the files mentioned above. You can do this using the file explorer of your IDE or using the command line.
    Your backend folder should look like this:

    .. code:: bash

        ├── solution
        │   ├── compute_step.py
        │   ├── definition.py

    Your frontend folder should look like this:

    .. code:: bash

        ├── ui
        │   ├── pages
        │   │   ├── about_page.py
        │   │   ├── compute_page.py
        │   │   ├── page.py

Almost there. We need to delete all the places where the deleted files are imported.

.. practice::

    Open the ``definition.py`` file and delete the import statement for the ``first_step.py`` and ``second_step.py`` files.
    Also remove the ``FirstStep`` and ``SecondStep`` classes from the solution definition. The final solution definition
    should look like this:

    .. code:: python

        from ansys.saf.glow.solution import Solution, StepsModel
        from ansys.solutions.simple_beam_bending.solution.compute_step import ComputeStep


        class Steps(StepsModel):
            """Workflow definition."""

            compute_step: ComputeStep


        class SimpleBeamBendingSolution(Solution):
            """Solution definition."""

            display_name: str = "Simple Beam Bending"
            version: int = 1
            steps: Steps

    Open the ``page.py`` file and delete the import statement for the ``first_page.py`` and ``second_page.py`` files.
    Also scroll down to the bottom of the file and find the ``display_pages`` function. Delete the lines of code that
    are referencing the deleted pages. The final ``display_pages`` function should look like this:

    .. code:: python

        @callback(
            Output("page-content", "children"),
            Input("url", "pathname"),
            Input(Tree.ids.selected_item("navigation_tree"), "data"),
            prevent_initial_call=True,
        )
        def display_page(pathname: str, value: dict) -> html.Div:
            """Display page content."""
            project = DashClient[Simple_Beam_BendingSolution].get_project(pathname)
            triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
            if triggered_id == "url":
                return about_page.layout()
            else:
                triggered_id = json.loads(triggered_id)
                if isinstance(triggered_id, dict):
                    if triggered_id["aio_id"] == "navigation_tree":
                        if value["index"] == "about_page":
                            return about_page.layout()
                        elif value["index"] == "compute_page":
                            return compute_page.layout(project.steps.compute_step)
                        else:
                            raise ValueError(f"Unknown page selection: {value['index']}")
            raise PreventUpdate

The frontend is now ready to be tested. We built the page layout and implemented the callback function that will trigger the
backend transaction method.

Before we wrap up, there are a couple of key points to note:

- During the frontend development, all the interactions with the backend are done in a full Pythonic way.
  Under the hood, SAF is making API calls between the frontend service (Dash) and the backend service (SAF)
  without you having to worry about it. This is one of the key features of SAF.

- You might have noticed the similarities between the ``callback`` decorator and the ``transaction`` decorator
  we used in the backend. Both have a concept of entry parameters and exit parameters. The dash equivalent of
  the ``download`` parameter of SAF is the ``Input`` parameter. The dash equivalent of the ``upload`` parameter
  of SAF is the ``Output`` parameter.

- Just like the backend we used the typing feature for the frontend code. While it is mandatory for the backend, it is not
  mandatory for the frontend. However, it is highly recommended to use it as it is a good practice and will help you to
  catch errors early in the development process.

Testing
=======

We are now ready for a full end-to-end test of the application.

.. practice::

    Run the application using the command:

    .. code:: bash

        saf run simple-beam-bending

    The solution UI should open in the desktop window. The first page should be the about page.
    You should see the following content:

    .. image:: /_static/images/beam_bending_about_page.png
        :align: center
        :width: 100%

    Click the **Compute** page in the navigation tree. The **Compute** page should look like this:

    .. image:: /_static/images/beam_bending_compute_page.png
        :align: center
        :width: 100%

    Click the compute button. The application should display a loading spinner while the computation is in progress.
    Once the computation is finished, the graph should be updated with the new deflection of the beam.

    .. image:: /_static/images/beam_bending_compute_page_witg_graph_updated.png
        :align: center
        :width: 100%

    You can also try to change the values of the input fields and click the compute button again. The graph should be updated.

    If any of the steps fail, please check the console for any error messages. In any case, you can always refer to the
    finalized code in the beam-bending repository to fix the issues.

Key takeaways
=============

.. important::

    - The frontend is built using Plotly Dash, a web application framework for Python.
    - The frontend is responsible for rendering the user interface and handling user interactions.
    - The static content of a page is placed in the ``layout`` function of the page.
    - The interactivity of the page is handled using callbacks. A ``callback`` is a function that is called when a specific event occurs.
    - The interaction between the frontend and the backend occurs in a full Pythonic way. It is done using the ``DashClient`` class in the
      ``callback`` function or a using the ``StepModel`` object in the layout function.
    - Typing is not mandatory for the frontend, but it is highly recommended to use it as it is a good practice.

