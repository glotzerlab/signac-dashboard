.. _api:

API Reference
=============

This is the API for the **signac-dashboard** application.

The Dashboard
-------------

.. _python-api-dashboard:

.. currentmodule:: signac_dashboard

.. autoclass:: Dashboard

.. rubric:: Attributes

.. autosummary::
    Dashboard.add_url
    Dashboard.encoded_modules
    Dashboard.job_sorter
    Dashboard.job_subtitle
    Dashboard.job_title
    Dashboard.main
    Dashboard.register_module_asset

.. autoclass:: signac_dashboard.Dashboard
    :members:
    :undoc-members:

Modules
-------

.. _python-api-modules:

.. autosummary::
    Module
    modules.ImageViewer
    modules.VideoViewer
    modules.StatepointList
    modules.DocumentList
    modules.FileList
    modules.Notes

.. autoclass:: signac_dashboard.Module
    :members:
    :undoc-members:

.. automodule:: signac_dashboard.modules
    :members:
    :exclude-members: get_cards
