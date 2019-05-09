.. _dashboard-security:

Security Guidelines
-------------------

By default, the **signac-dashboard** application only listens to HTTP requests from :code:`localhost`, on port 8888.
Running the **signac-dashboard** Flask server with a configuration that makes it publicly accessible presents a critical security risk.
For example, user-implemented modules may not be safe-guarded against arbitrary code execution.
To enable remote access, use `secure port forwarding via SSH <dashboard-remote-ssh>`_.
The use of the :code:`$where` operation in searches is disabled by default and must be `explicitly enabled <python-api-dashboard>`_, in which case the dashboard is vulnerable against `code-injection attacks <https://en.wikipedia.org/wiki/Code_injection>`_.
