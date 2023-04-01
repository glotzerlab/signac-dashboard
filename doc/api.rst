.. _dashboard-api:

API Reference
=============

This is the API for the **signac-dashboard** application.

.. _python-api-dashboard:

The Dashboard
-------------

.. currentmodule:: signac_dashboard

.. rubric:: Attributes

.. autosummary::
    Dashboard.add_url
    Dashboard.job_sorter
    Dashboard.job_subtitle
    Dashboard.job_title
    Dashboard.main
    Dashboard.register_module_asset
    Dashboard.run
    Dashboard.update_cache

.. autoclass:: signac_dashboard.Dashboard
    :members:
    :undoc-members:

.. _python-api-dashboard-modules:

Dashboard Modules
-----------------

.. autosummary::
    Module
    modules.DocumentEditor
    modules.DocumentList
    modules.FileList
    modules.FlowStatus
    modules.ImageViewer
    modules.IPythonDisplay
    modules.Notes
    modules.Schema
    modules.StatepointList
    modules.TextDisplay
    modules.VideoViewer

.. autoclass:: signac_dashboard.Module
    :members:
    :undoc-members:

.. automodule:: signac_dashboard.modules
    :members:
    :exclude-members: get_cards, register
