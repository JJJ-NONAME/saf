.. vale off

{{ name | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :show-inheritance:
{% set ids_classname = objname + 'Ids' %}
{% if ids_classname in members %}

.. rubric:: IDs

.. autoclass:: {{ module }}.{{ objname }}.{{ ids_classname }}
   :show-inheritance:
   :members:
{% endif %}
