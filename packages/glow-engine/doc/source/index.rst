.. _saf-packages_glow_engine_api_index:


.. title:: SAF GLOW Engine documentation

.. meta::
    :description: SAF GLOW Engine - SAF core application runtime
    :keywords: ansys, glow, engine


#########################
GLOW Engine API reference
#########################

GLOW provides Pythonic APIs that you can use to develop solutions. This documentation provides details on the core classes, functions, and methods in the GLOW API.


.. toctree::
   :hidden:

   ansys/saf/glow/index
   ansys/saf/glow/solution/products/config/index


.. grid:: 2
    :gutter: 4
    :class-container: onboarding-cards

    .. grid-item-card:: :material-outlined:`api;2em` Solution API
        :class-card: highlight-card
        :shadow: lg
        :link-type: doc
        :link: ansys/saf/glow/solution/index

        Provides the core functionality for managing and running solutions with the GLOW.

    .. grid-item-card:: :material-outlined:`api;2em` Runtime API
        :class-card: highlight-card
        :shadow: lg
        :link-type: doc
        :link: ansys/saf/glow/runtime/index

        Enables the integration of a GLOW Solution (a Guided Workflow Application) with the GLOW infrastructure.

    .. grid-item-card:: :material-outlined:`api;2em` Client API
        :class-card: highlight-card
        :shadow: lg
        :link-type: doc
        :link: ansys/saf/glow/client/index

        Enables programs, including a Dash UI server, to access a remote GLOW server that provides the guided workflow service for a given GLOW solution.

    .. grid-item-card:: :material-outlined:`api;2em` Product instance API
        :class-card: highlight-card
        :shadow: lg
        :link-type: doc
        :link: ansys/saf/glow/solution/products/config/index

        Enables you to run, access, and manage Ansys products.

    .. grid-item-card:: :material-outlined:`api;2em` HPS API
        :class-card: highlight-card
        :shadow: lg
        :link-type: doc
        :link: ansys/saf/glow/solution/hps/index

        Enables transaction methods to start HPS jobs and parametric studies and request data from those jobs and studies.

    .. grid-item-card:: :material-outlined:`api;2em` CLI API
        :class-card: highlight-card
        :shadow: lg
        :link-type: doc
        :link: ansys/saf/glow/cli/index

        Enables programs to access CLI commands.

    .. grid-item-card:: :material-outlined:`api;2em` HPS execution API
        :class-card: highlight-card
        :shadow: lg
        :link-type: doc
        :link: ansys/saf/glow/hps_execution/index

        Defines the execution context and product interfaces available to scripts that run inside an HPS job.

    .. grid-item-card:: :material-outlined:`api;2em` HPS execution source
        :class-card: highlight-card
        :shadow: lg
        :link-type: doc
        :link: ansys/saf/glow/hps_execution_str/index

        Provides the HPS execution module source that is shipped to and loaded by HPS job runners.

    .. grid-item-card:: :material-outlined:`api;2em` Solution server API
        :class-card: highlight-card
        :shadow: lg
        :link-type: doc
        :link: ansys/saf/glow/api/index

        Exposes the ASGI application used to start the GLOW solution REST API server.

    .. grid-item-card:: :material-outlined:`api;2em` UI server API
        :class-card: highlight-card
        :shadow: lg
        :link-type: doc
        :link: ansys/saf/glow/ui/index

        Exposes the application used to serve the GLOW solution user interface.


