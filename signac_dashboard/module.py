# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from flask import render_template


class Module:
    """Base class for modules, the building blocks of the dashboard.

    A module turns select information from the job directory or project
    directory into cards displayed on the dashboard. The cards pull content from
    the job directory or project directory depending on whether the module
    ``context`` is ``'JobContext'`` or ``'ProjectContext'``.

    :param name: Name of the module for card titles.
    :type name: str
    :param context: Context in which this module's cards will be displayed, either
        :code:`'JobContext'` *or* :code:`'ProjectContext'`.
    :type context: str
    :param template: Path to a template file for this module's cards (e.g.
        :code:`cards/my_module.html`, without the template directory prefix
        :code:`templates/`).
    :type template: str
    :param enabled: Whether the module's cards will be displayed. (default: :code:`True`)
    :type enabled: bool

    **Custom modules:** User-defined module classes should be a subclass of
    :py:class:`~.Module` and define the function :py:meth:`~.Module.get_cards`.
    Template files are written in HTML/Jinja-compatible syntax.
    See `this example <https://github.com/glotzerlab/signac-dashboard/tree/master/examples/custom-modules>`_.

    **Module assets:** If a module requires scripts or stylesheets to be
    included for its content to be rendered, they must be handled by the
    callback :py:meth:`.register`. For example, a module inheriting from
    the base :py:class:`signac_dashboard.Module` class may implement this by
    overriding the default method as follows:

    .. code-block:: python

        def register(self, dashboard):
            assets = ['js/my-script.js', 'css/my-style.css']
            for asset in assets:
                dashboard.register_module_asset({
                    'file': 'templates/my-module/{}'.format(asset),
                    'url': '/module/my-module/{}'.format(asset)
                })

    Then, when the module is active, its assets will be included and a
    route will be created that returns the asset file.

    **Module routes:** The callback :py:meth:`.register` allows modules
    to implement custom routes, such as methods that should be triggered by
    :code:`POST` requests or custom APIs. For example, a module inheriting from
    the base :py:class:`signac_dashboard.Module` class may implement this by
    overriding the default method as follows:

    .. code-block:: python

        def register(self, dashboard):
            @dashboard.app.route('/module/my-module/update', methods=['POST'])
            def my_module_update():
                # Perform update
                return "Saved."

    """  # noqa: E501

    _supported_contexts = {}

    def __init__(self, name, context, template, enabled=True):
        self._module = self.__module__
        self._moduletype = self.__class__.__name__
        self.name = name
        if len(self._supported_contexts) == 0:
            raise ValueError(f"{self._moduletype} is not supported by any contexts.")
        if context not in self._supported_contexts:
            raise RuntimeError(
                f"{self._moduletype} does not support the {context}, only "
                f"{self._supported_contexts}."
            )
        self.context = context
        self.template = template
        self.enabled = enabled

    def get_cards(self):
        """Returns this module's cards for rendering.

        The cards are returned as a list of dictionaries with keys
        :code:`'name'` and :code:`'content'`.

        :returns: List of module cards.
        :rtype: list
        """
        return [{"name": self.name, "content": render_template(self.template)}]

    def enable(self):
        """Enable this module."""
        self.enabled = True

    def disable(self):
        """Disable this module."""
        self.enabled = False

    def toggle(self):
        """Toggle this module."""
        self.enabled = not self.enabled

    def register(self, dashboard):
        """Callback to register this module with the dashboard.

        This callback should register assets and routes, as well as any other
        initialization that accesses or modifies the dashboard.

        :param dashboard: The dashboard invoking this callback method.
        :type dashboard: :py:class:`signac_dashboard.Dashboard`
        """
        pass
