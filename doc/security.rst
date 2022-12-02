.. _dashboard-security:

Security Guidelines
-------------------

By default, the **signac-dashboard** application only listens to HTTP requests from :code:`localhost`, on port 8888.
Running the **signac-dashboard** Flask server with a configuration that makes it publicly accessible presents a critical security risk.
For example, user-implemented modules may not be safe-guarded against arbitrary code execution.
To enable remote access, use :ref:`secure port forwarding via SSH<signac-docs:dashboard-remote-ssh>`.
The use of the :code:`$where` operation in searches is disabled by default and must be :ref:`explicitly enabled<python-api-dashboard>`, in which case the dashboard is vulnerable against `code-injection attacks <https://en.wikipedia.org/wiki/Code_injection>`_.

By default, **signac-dashboard** generates an access token that is required to login to the web page.
This protects your data from access by other users on multi-user systems.
To disable authentication, set ``ACCESS_TOKEN`` to ``None`` in the ``config`` dictionary.
To protect your data, disable authentication only when running on a dedicated host that provides additional layers of security.
