# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import collections.abc

from flask import render_template

from signac_dashboard.module import Module

try:
    from IPython.core.formatters import HTMLFormatter, PlainTextFormatter

    HTML_FORMATTER = True
except ImportError:
    HTML_FORMATTER = False


def _dict_to_collapsible_table(dict_):
    button_fmt = '<button type="button" class="collapsible">{}</button>'
    content_fmt = '<div class="content">{}</div>'
    content = []
    content.append('<div class="collapsible-table">')
    for key, value in dict_.items():
        content.append(button_fmt.format(key))
        if isinstance(value, collections.abc.Mapping):
            inner_content = _dict_to_collapsible_table(value)
        else:
            inner_content = "<p>" + repr(value) + "</p>"
        content.append(content_fmt.format(inner_content))
    content.append("</div>")
    return "".join(content)


class _JobHTMLView:
    """Provides a rich HTML expandable node view of a job's statepoint."""

    def __init__(self, job):
        self.job = job

    def _repr_html_(self):
        return _dict_to_collapsible_table(self.job.sp)


class IPythonDisplay(Module):
    """Render a function's return value with IPython's HTML formatter.

    This module calls a user-provided function to display HTML content in a
    card. The :code:`IPython` package is required. Example:

    .. code-block:: python

        from signac_dashboard.modules import IPythonDisplay

        def render_job(job):
            return job

        modules = [IPythonDisplay(contents=render_job)]

    Many common Python libraries (such as pandas) come with classes that already
    implement ``_repr_html_`` and can be used directly. However, this next
    example shows a custom output (in this case a bolded temperature).

    .. code-block:: python

        from signac_dashboard.modules import IPythonDisplay

        class BoldTemperature:
            def __init__(self, job):
                self.job = job

            def _repr_html_(self):
                return f"<strong>T={self.job.sp.temperature}</strong>"

        def render_job(job):
            return BoldTemperature(job)

        modules = [IPythonDisplay(contents=render_job)]

    :param contents: A callable accepting one argument of type
        :py:class:`signac.contrib.job.Job` and returning an object to be
        rendered with IPython's :code:`HTMLFormatter`.
    :type contents: callable
    """

    _supported_contexts = {"JobContext"}

    def __init__(
        self,
        name="IPython Display",
        contents=None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            context="JobContext",
            template="cards/ipython_display.html",
            **kwargs,
        )
        if contents is None:
            if HTML_FORMATTER:
                self.contents = _JobHTMLView
            else:
                self.contents = lambda j: j
        else:
            self.contents = contents

    def get_cards(self, job):
        contents = self.contents(job)
        if HTML_FORMATTER:
            html_contents = HTMLFormatter()(contents)
            # Handle lack of _repr_html_ like IPython
            if html_contents is None:
                html_contents = "<p>" + PlainTextFormatter()(contents) + "</p>"
        else:
            html_contents = "Error: Install the 'IPython' library to render contents."
        return [
            {
                "name": self.name,
                "content": render_template(self.template, html_contents=html_contents),
            }
        ]

    def register(self, dashboard):
        # Register assets
        assets = ["js/ipython_job_viewer.js", "css/ipython_job_viewer.css"]
        for assetfile in assets:
            dashboard.register_module_asset(
                {
                    "file": f"templates/ipython_display/{assetfile}",
                    "url": f"module/ipython_display/{assetfile}",
                }
            )
