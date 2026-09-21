.. _saf-ex-long-transaction:

Long-running transaction streaming uploads
############################################

.. topic:: Objective

  Report the progress of a slow computation while it runs: execute it in a long-running
  transaction method, upload intermediate results from inside the method, and refresh a
  progress bar and a status label in the solution UI.

  Source code for this example is in the `example solution <https://github.com/ansys/saf/tree/main/examples>`_.


.. _saf-ex-long-transaction-feature-highlight:

:material-outlined:`emoji_objects;1.25em;sd-text-primary` Feature highlight
============================================================================

A **long-running transaction method** is a transaction method decorated with ``@long_running``. It
runs asynchronously, so the frontend stays responsive and other methods can execute while it is
still in progress. Instead of uploading its results once at the end, such a method can upload
intermediate values as it goes, which is what makes live progress reporting possible.

In this example, you learn how to:

- :material-outlined:`hourglass_top;1.25em;saf-objective-icon` Turn a slow computation into a
  **long-running transaction method** with the ``@long_running`` decorator.
- :material-outlined:`data_object;1.25em;saf-objective-icon` Track the progress in **typed step
  fields**, such as a counter, a status string, and a running flag.
- :material-outlined:`publish;1.25em;saf-objective-icon` Push intermediate results to the solution
  from inside the method with ``self.transaction.upload``.
- :material-outlined:`timer;1.25em;saf-objective-icon` Poll the step from the frontend with a
  ``dcc.Interval`` component that fires every second while the method is running.
- :material-outlined:`bolt;1.25em;saf-objective-icon` Wire **callbacks** that start the method and
  refresh the **progress bar**, the status label, and the button state.

When you complete this example, you can expect the following output in the solution UI:

.. _saf-ex-long-transaction-output-1:

.. figure:: /_static/images/usage_saf_ex_long_transaction_output_1.png
  :width: 100%

  Progress bar before the transaction execution starts

.. figure:: /_static/images/usage_saf_ex_long_transaction_output_2.png
  :width: 100%

  Progress bar while transaction execution is in progress

.. figure:: /_static/images/usage_saf_ex_long_transaction_output_3.png
  :width: 100%

  Progress bar when transaction execution is complete


.. _saf-ex-long-transaction-prerequisites:

:material-outlined:`task;1.25em;sd-text-primary` Prerequisites
=========================================================================

The long-running transaction API is provided in the |glow-doc-ref|_ package, which is available by default in any SAF-based solution.
The progress bar used in this example comes from the `Dash Bootstrap Components <https://dash-bootstrap-components.opensource.faculty.ai/docs/components/progress/>`_ library.


.. _saf-ex-long-transaction-solution:

:octicon:`code-square;1em;sd-text-primary` Coding
======================================================

To stream the progress of a long-running transaction method to the solution UI, work through the following sequence of sections.


.. _saf-ex-long-transaction-backend:

:material-outlined:`dns;1.25em;sd-text-primary` Backend
---------------------------------------------------------

Create the solution definition.

.. key-concept:: Long-running transaction method

    A transaction method decorated with ``@long_running`` executes asynchronously. The frontend keeps
    responding to user actions, and the current status of the method can be queried at any time with
    ``step.get_long_running_method_state(<method_name>)``.

.. key-concept:: Streaming upload

    A blocking transaction method uploads its fields only when it returns. Inside a long-running
    transaction method, ``self.transaction.upload([...])`` pushes the current value of the listed
    fields to the solution immediately, so the frontend can read them before the method completes.

.. dropdown:: Define the step model
  :open:

  The step model for a simple step named ``FirstStep`` is defined in the ``first_step.py`` file.

  * The step manages the state of the long transaction, using the ``current_increment`` attribute to count from 0 to 50.

  * The other attributes manage the actual number of increments to run:

    * A status string reflects when the latest increment was updated.
    * A Boolean attribute indicates whether the long transaction is running.

  * The only defined transaction uses a *for-loop* to increment the counter and the status string
    every second.

  .. code-block:: python
     :lineno-start: 6
     :caption: ``first_step.py``

         from ansys.saf.glow.solution import StepModel, StepSpec, transaction, long_running
         import time
         import datetime


         class FirstStep(StepModel):
             """Definition of a simple step."""

             status: str = "[]"
             processing: bool = False
             number_of_increments: int = 50
             current_increment: int = -1

             @long_running
             @transaction(
                 self=StepSpec(
                     download=["processing", "number_of_increments"],
                     upload=["status", "current_increment"],
                 )
             )
             def stream_updates(self) -> None:
                 for i in range(self.number_of_increments):
                     self.status = f"Update {i} at  {_now()}"
                     self.current_increment = i
                     self.transaction.upload(["status", "current_increment"])
                     time.sleep(1)
                     self.status = f"Last updated at {_now()}"


         def _now():
             return datetime.datetime.now().strftime("%H:%M:%S")


.. _saf-ex-long-transaction-frontend:

:material-outlined:`web;1.25em;sd-text-primary` Frontend
----------------------------------------------------------

Expose the solution definition in the UI.

.. dropdown:: Define the step layout
  :open:

  The user interface has three main widgets: a button, a progress bar, and a status label.
  A fourth element triggers a callback every second while active.

  .. code-block:: python
      :lineno-start: 6
      :caption: layout from ``first_page.py``

      from ansys.saf.glow.client import DashClient, callback
      from dash_extensions.enrich import Input, Output, State, dcc, html
      from ansys.saf.glow.solution import MethodStatus
      import dash_bootstrap_components as dbc
      from dash.exceptions import PreventUpdate

      from ansys.solutions.abc.solution.definition import AbcSolution
      from ansys.solutions.abc.solution.first_step import FirstStep


      def layout(step: FirstStep):
          return html.Div(
              [
                  html.H1("Long Transaction Streaming Update Example"),
                  html.P(),
                  html.Button("Run test", id="run-button", n_clicks=0),
                  html.Div(
                      [
                          dbc.Progress(
                              id="completion-progress", className="mb-3", value=0, label="", max=step.number_of_increments
                          )
                      ]
                  ),
                  html.Div(id="status-line", children=["nothing"]),
                  dcc.Interval(id="interval-refresh", interval=1 * 1000, n_intervals=0, disabled=True),  # in milliseconds
              ]
          )

.. key-concept:: Callback

    A **callback** is a Dash-decorated function that fires in response to a UI event. In a SAF
    solution, callbacks reach the backend through ``project.steps.<step_name>``, read or write
    fields, and invoke transaction methods — no manual HTTP calls needed.

.. dropdown:: Define the transaction start button
  :open:

  * The callback starting the long transaction resets the data in the step.
  * To extend this example, you could add an input indicating the number of increments
    to be run.
  * This data can be set as it is downloaded in the corresponding transaction.

  .. code-block:: python
      :lineno-start: 33
      :caption: transaction start button callback from ``first_page.py``

      @callback(
          Output("status-line", "children"),
          Output("run-button", "disabled"),
          Output("interval-refresh", "disabled"),
          Output("completion-progress", "value"),
          Output("completion-progress", "label"),
          Input("run-button", "n_clicks"),
          State("url", "pathname"),
          prevent_initial_call=True,
      )
      def start_long_running_transaction(n_clicks, pathname):
          if n_clicks <= 0:
              raise PreventUpdate
          project = DashClient[AbcSolution].get_project(pathname)
          step = project.steps.first_step
          step.processing = True
          step.current_increment = -1
          step.stream_updates()
          return "running", True, False, 0, ""

.. dropdown:: Define the timer callback
  :open:

  * When the :guilabel:`Run` test button is clicked, the timer callback is activated
    and called every second.
  * The callback uses the data from the step to update the status string and the progress bar.
  * When the processing is finished, it reactivates the :guilabel:`Run` test button and
    deactivates the timer.

  .. code-block:: python
      :lineno-start: 53
      :caption: timer callback from ``first_page.py``

      @callback(
          Output("status-line", "children"),
          Output("run-button", "disabled"),
          Output("interval-refresh", "disabled"),
          Output("completion-progress", "value"),
          Output("completion-progress", "label"),
          Input("interval-refresh", "n_intervals"),
          State("url", "pathname"),
          prevent_initial_call=True,
      )
      def update_status(_, pathname):
          project = DashClient[AbcSolution].get_project(pathname)
          step = project.steps.first_step
          if not step.processing:
              raise PreventUpdate
          else:
              number_of_completed_increments = step.current_increment + 1
              progress = int((number_of_completed_increments * 100) / step.number_of_increments)
              if step.get_long_running_method_state("stream_updates").status == MethodStatus.Running:
                  status = "running"
              else:
                  status = "done"
                  step.processing = False
              return (
                  f"{step.status} {status}",
                  step.processing,
                  not step.processing,
                  number_of_completed_increments,
                  f"{progress}%",
              )

  Now that your implementation is complete, continue to the :ref:`saf-ex-long-transaction-testing` section.


.. _saf-ex-long-transaction-testing:

:octicon:`verified;1em;sd-text-primary`  Testing
==================================================

Finally, test your implementation to confirm it works as expected.

Run the solution and compare your results with the results shown in the
:ref:`Feature highlight <saf-ex-long-transaction-feature-highlight>` section.
