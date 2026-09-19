.. _saf-ex-process-logs-events:

Streaming process logs
#############################

.. topic:: Objective

    Use a long-running transaction combined with SAF GLOW events to stream log output produced on the backend to the UI in real time.

:material-outlined:`task;1.25em;sd-text-primary` Prerequisites
=========================================================================

The long-running transaction and events APIs are provided in the |glow-doc-ref|_ package, which is available by default in any SAF-based solution.

:octicon:`code-square;1em;sd-text-primary` Solution
======================================================

This example demonstrates how to run a long-running transaction that periodically writes to a log file and streams each new
log line to the UI as it is produced, instead of waiting for the transaction to finish before displaying the result.

.. tip::

  - Checkout the full backend code of the example in the `example solution <https://github.com/ansys/saf/blob/main/examples/src/saf/solutions/examples/solution/basic_step.py>`__.
  - Checkout the full frontend code of the example in the `example solution <https://github.com/ansys/saf/blob/main/examples/src/saf/solutions/examples/ui/pages/basic/process_logs_page.py>`__.

Feature: Generate and stream process logs
--------------------------------------------

In this example the user starts a long-running transaction that appends a timestamped line to a log file every second for
a given duration. Each time a new line is written, the backend raises an event carrying that line, which the UI appends to
the log panel without needing to poll or refresh. A second event stream notifies the UI when the transaction terminates so
that the UI can re-enable the controls and reflect the final status.

.. _saf-ex-process-logs-events-backend-code-model:

Backend (Solution Definition - Step model)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code shows the ``log_file`` field on the step model that persists the accumulated log content.

.. dropdown:: Backend code - Step model

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/solution/basic_step.py
    :language: python
    :start-at: log_file: EntityHandle = NO_ENTITY
    :end-at: log_file: EntityHandle = NO_ENTITY

The ``log_file`` field is an ``EntityHandle`` that references the log file content stored via BDM. It defaults to ``NO_ENTITY``
until the first log line is written.

.. _saf-ex-process-logs-events-backend-code-transaction:

Backend (Solution Definition - Generate logs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code shows the long-running transaction method that writes the log file and streams updates.

.. dropdown:: Backend code - Generate process logs

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/solution/basic_step.py
    :language: python
    :pyobject: BasicStep.generate_process_logs

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/solution/basic_step.py
    :language: python
    :pyobject: BasicStep.clear_logs

The ``generate_process_logs`` method is marked ``@long_running`` so it executes asynchronously, allowing the UI to remain
responsive while it runs. The ``transaction`` decorator sets ``enable_termination_event=True`` so that a termination event is
automatically raised on the stream named after the method, ``generate-process-logs``, when the method completes or fails.

On each iteration the method:

  - appends a new timestamped line to the in-memory log content;
  - persists the updated content by re-uploading it to storage via ``store_stream`` and assigning the resulting ``EntityHandle``
    to ``self.log_file``;
  - raises an event carrying only the new line (not the whole log) on the custom ``generate-process-logs-update`` stream, so
    that listeners can append it directly to what is already displayed.

The ``clear_logs`` transaction simply resets ``log_file`` to ``NO_ENTITY``, discarding the previously stored content.

See

  - :ref:`saf-ex-process-logs-events-frontend-code-listeners` for how the UI subscribes to both streams;
  - :ref:`saf-ex-process-logs-events-frontend-code-update` for the callback that appends streamed lines to the log panel; and
  - :ref:`saf-ex-process-logs-events-frontend-code-termination` for the callback that reacts to the termination event.

.. _saf-ex-process-logs-events-frontend-code-layout:

Frontend (Layout)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code shows the layout that renders the "Start" button and the scrollable log panel.

.. dropdown:: Frontend code - Layout

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/ui/pages/basic/process_logs_page.py
    :language: python
    :start-at: NO_LOGS_MESSAGE = "No logs are available yet."
    :end-at: NO_LOGS_MESSAGE = "No logs are available yet."

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/ui/pages/basic/process_logs_page.py
    :language: python
    :pyobject: layout

The log text is rendered inside a stable ``html.Pre`` element identified by ``id="log_content"``. Keeping the log text as a
single string on a fixed component (rather than rebuilding the whole ``log_container`` tree on every update) makes it possible
for later callbacks to update the displayed logs with a simple string concatenation. The initial content is populated from
the persisted log file, if any, via :ref:`saf-ex-process-logs-events-frontend-code-initial-text`.

.. _saf-ex-process-logs-events-frontend-code-listeners:

Frontend (Event listeners)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code mounts the event listeners that subscribe to the two backend streams.

.. dropdown:: Frontend code - Mount event listeners

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/ui/pages/basic/process_logs_page.py
    :language: python
    :pyobject: mount_event_listeners

Two listeners are created: ``generate-process-logs-update-listener`` receives every new log line raised on the
``generate-process-logs-update`` stream while the transaction is running, and ``generate-process-logs-termination-listener``
receives the termination event automatically raised on the ``generate-process-logs`` stream (named after the transaction
method) when the transaction completes or fails.

.. _saf-ex-process-logs-events-frontend-code-start:

Frontend (Callback starting the transaction)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code shows the callback that starts the ``generate_process_logs`` transaction.

.. dropdown:: Frontend code - Start transaction

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/ui/pages/basic/process_logs_page.py
    :language: python
    :pyobject: start_generate_process_logs_transaction

Clicking the "Start" button calls ``step.generate_process_logs(wait_time=10.0)``, which starts the long-running transaction
asynchronously, and immediately shows a persistent, loading notification so the user knows the process is underway.

.. _saf-ex-process-logs-events-frontend-code-update:

Frontend (Callback appending streamed logs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code shows the callback that appends each streamed log line to the log panel.

.. dropdown:: Frontend code - Append streamed logs

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/ui/pages/basic/process_logs_page.py
    :language: python
    :pyobject: update_logs_on_backend_events

Each event message payload is JSON-encoded, so it must be decoded with ``json.loads`` before being used; otherwise the raw
JSON text (including surrounding quotes and escaped ``\n`` sequences) would be displayed instead of an actual line break.
If the log panel currently only shows the placeholder text, the new line replaces it rather than being appended, so the
placeholder disappears as soon as the first log line arrives. Because the ``log_content`` element uses ``whiteSpace:
pre-wrap``, the ``\n`` terminating each log line causes it to be displayed on its own row.

.. _saf-ex-process-logs-events-frontend-code-termination:

Frontend (Callbacks handling termination)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code shows the callbacks that react to the transaction's termination event.

.. dropdown:: Frontend code - Handle termination

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/ui/pages/basic/process_logs_page.py
    :language: python
    :pyobject: sync_controls

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/ui/pages/basic/process_logs_page.py
    :language: python
    :pyobject: sync_notifications

``sync_controls`` disables the "Start" button and shows a loading spinner as soon as it is clicked, then re-enables it once the
termination event is received. ``sync_notifications`` parses the termination event payload into a ``MethodState`` and uses the
shared ``handle_method_event`` helper to replace the in-progress notification with a success or failure message.

.. _saf-ex-process-logs-events-frontend-code-clear:

Frontend (Callback clearing the logs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code shows the callback triggered by the "Clear Logs" icon button.

.. dropdown:: Frontend code - Clear logs

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/ui/pages/basic/process_logs_page.py
    :language: python
    :pyobject: clear_process_logs

This callback calls the ``clear_logs`` transaction to discard the persisted log file, and resets the ``log_content`` text back
to the placeholder message.

.. _saf-ex-process-logs-events-frontend-code-initial-text:

Frontend (Initial log text)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code reads the persisted log file to populate the log panel when the page is first rendered.

.. dropdown:: Frontend code - Initial log text

  .. literalinclude:: ../../../../examples/src/saf/solutions/examples/ui/pages/basic/process_logs_page.py
    :language: python
    :pyobject: get_process_logs_text

This ensures that navigating back to the page after logs have already been generated shows the previously accumulated content,
rather than starting from the placeholder message.
