.. _examples-index:

########
Examples
########

Each example demonstrates how to implement a specific feature in a solution application. Unless otherwise indicated, examples are both integrated into the :ref:`Solution Examples <examples_solution>` solution and addressed in :ref:`this documentation <examples_instructions>`.

.. _examples_solution:

Set up the example solution
============================

The example solution provided in the ``saf/examples`` directory demonstrates selected SAF examples. Follow these instructions to install and run the solution.

#. Ensure you've fulfilled all requirements noted in the :ref:`prerequisites` section.

#. In a local clone of the ``saf`` repository, move to the ``examples`` folder:

   .. code-block:: bash

     cd saf/examples

#. Install the solution:

   .. code-block:: bash

       saf install -f

#. Run the solution:

   .. code-block:: bash

     saf run


.. _examples_instructions:

Get example instructions
==========================

To get detailed instructions for examples, either click a category in the left navigation sidebar or click the corresponding card below:

.. card:: :large-bold:`UI Components and visualization`

  .. grid:: 3
    :gutter: 4
    :class-container: onboarding-cards

    .. grid-item-card:: :material-outlined:`show_chart;1.75em` :ref:`saf-ex-plotly-graph`
      :class-card: highlight-card
      :link-type: doc
      :link: ui_components_visualization_examples/saf_ex_plotly_graph
      :shadow: lg

      Use Plotly graphs to display step field data in a solution user interface.

    .. grid-item-card:: :material-outlined:`table_chart;1.75em` :ref:`saf-ex-dash-table`
      :class-card: highlight-card
      :link-type: doc
      :link: ui_components_visualization_examples/saf_ex_dash_table
      :shadow: lg

      Generate an interactive Dash data table to display a simple dataset in a solution user interface.

.. card:: :large-bold:`Data and file management`

  .. grid:: 3
    :gutter: 4
    :class-container: onboarding-cards

    .. grid-item-card:: :material-outlined:`upload_file;1.75em` :ref:`saf-ex-file-upload`
      :class-card: highlight-card
      :link-type: doc
      :link: data_file_management_examples/saf_ex_file_upload
      :shadow: lg

      Use SAF GLOW to upload files to a solution and use them to perform a simple computation.

    .. grid-item-card:: :material-outlined:`data_object;1.75em` :ref:`saf-ex-bdm`
      :class-card: highlight-card
      :link-type: doc
      :link: data_file_management_examples/saf_ex_bdm
      :shadow: lg

      Use Blob Data Management (BDM) Python API to manage files and directories in a solution.

    .. grid-item-card:: :material-outlined:`image;1.75em` :ref:`saf-ex-display-images`
      :class-card: highlight-card
      :link-type: doc
      :link: data_file_management_examples/saf_ex_display_images
      :shadow: lg

      Use SAF GLOW to parse and store files and display them as images in a solution user interface.

    .. grid-item-card:: :material-outlined:`list_alt;1.75em` :ref:`saf-ex-process-logs`
      :class-card: highlight-card
      :link-type: doc
      :link: data_file_management_examples/saf_ex_process_logs
      :shadow: lg

      Use Dash to display the content of a log file in a solution user interface.

.. card:: :large-bold:`Transaction methods`

  .. grid:: 2
    :gutter: 4
    :class-container: onboarding-cards

    .. grid-item-card:: :material-outlined:`sync;1.75em` :ref:`Long-running transaction streaming uploads <saf-ex-long-transaction>`
      :class-card: highlight-card
      :link-type: doc
      :link: transaction_methods_examples/saf_ex_long_transaction
      :shadow: lg

      Use SAF GLOW to display a progress bar tracking the execution of a long-running transaction through streaming uploads.

    .. grid-item-card:: :material-outlined:`cloud_sync;1.75em` :ref:`saf-ex-hps-job-submission`
      :class-card: highlight-card
      :link-type: doc
      :link: transaction_methods_examples/saf_ex_hps_job_submission
      :shadow: lg

      Use SAF GLOW Engine to start an HPS job and monitor the job's progress, using event streaming with termination events to change UI state.

    .. grid-item-card:: :material-outlined:`list_alt;1.75em` :ref:`saf-ex-process-logs-events`
      :class-card: highlight-card
      :link-type: doc
      :link: transaction_methods_examples/saf_ex_process_logs_events
      :shadow: lg

      Use a long-running transaction combined with SAF GLOW events to stream log output produced on the backend to the UI in real time.

.. card:: :large-bold:`SAF product instance managers (PIM)`

  .. grid:: 3
    :gutter: 4
    :class-container: onboarding-cards

    .. grid-item-card:: :material-outlined:`device_hub;1.75em`  :ref:`saf-ex-aedt-product-instance`
      :class-card: highlight-card
      :link-type: doc
      :link: product_instance_managers_examples/saf_ex_aedt_product_instance
      :shadow: lg

      Use SAF GLOW Engine to create an instance of an AEDT product (Maxwell 2D) and integrate its workflow in your solution.

    .. grid-item-card:: :material-outlined:`device_hub;1.75em` :ref:`saf-ex-fluent-product-instance`
      :class-card: highlight-card
      :link-type: doc
      :link: product_instance_managers_examples/saf_ex_fluent_product_instance
      :shadow: lg

      Use SAF GLOW Engine to create an instance of a Fluent product and integrate its workflow in your solution.

    .. grid-item-card:: :material-outlined:`device_hub;1.75em` :ref:`saf-ex-optislang-product-instance`
      :class-card: highlight-card
      :link-type: doc
      :link: product_instance_managers_examples/saf_ex_optislang_product_instance
      :shadow: lg

      Use SAF GLOW Engine to create an instance of an optiSLang product and integrate its workflow in your solution.

    .. grid-item-card:: :material-outlined:`device_hub;1.75em` :ref:`saf-ex-geometry-product-instance`
      :class-card: highlight-card
      :link-type: doc
      :link: product_instance_managers_examples/saf_ex_geometry_product_instance
      :shadow: lg

      Use SAF GLOW Engine to create an instance of a Geometry product and integrate its workflow in your solution.

    .. grid-item-card:: :material-outlined:`device_hub;1.75em` :ref:`saf-ex-mechanical-product-instance`
      :class-card: highlight-card
      :link-type: doc
      :link: product_instance_managers_examples/saf_ex_mechanical_product_instance
      :shadow: lg

      Use SAF GLOW Engine to create an instance of a Mechanical product and integrate its workflow in your solution.

    .. grid-item-card:: :material-outlined:`device_hub;1.75em` :ref:`saf-ex-mapdl-product-instance`
      :class-card: highlight-card
      :link-type: doc
      :link: product_instance_managers_examples/saf_ex_mapdl_product_instance
      :shadow: lg

      Use SAF GLOW Engine to create an instance of a MAPDL product and integrate its workflow in your solution.

.. card:: :large-bold:`Dash Super Components`

  Get started with a collection of simple, single-file Dash applications that highlight the features of the Dash Super Components library.

  .. grid:: 2
    :gutter: 4
    :class-container: onboarding-cards


    .. grid-item-card:: :material-outlined:`dashboard;1.75em` :ref:`sphx_glr_examples_dash_super_components_examples_general`
      :class-card: highlight-card
      :link-type: doc
      :link: dash_super_components_examples/general/index
      :shadow: lg

      Explore examples that demonstrate the usage of Dash Super Components in a general Dash app.

    .. grid-item-card:: :material-outlined:`widgets;1.75em` :ref:`sphx_glr_examples_dash_super_components_examples_saf_based`
      :class-card: highlight-card
      :link-type: doc
      :link: dash_super_components_examples/saf_based/index
      :shadow: lg

      Explore examples that demonstrate the usage of Dash Super Components that integrate directly with SAF GLOW API.


  .. note:: The Dash Super Components examples are not integrated into the example solution.


.. toctree::
  :hidden:
  :maxdepth: 3

  ui_components_visualization_examples/index
  data_file_management_examples/index
  transaction_methods_examples/index
  product_instance_managers_examples/index
  dash_super_components_examples/index
