# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from flask import render_template

from signac_dashboard.module import Module

try:
    from IPython.core.formatters import HTMLFormatter

    HTML_FORMATTER = True
except ImportError:
    HTML_FORMATTER = False


class IPythonDisplay(Module):
    """Render a function's return value with IPython's HTML formatter.

    This module calls a user-provided function to display HTML content in a
    card. The :code:`IPython` package is required. Example:

    .. code-block:: python

        from signac_dashboard.modules import IPythonDisplay

        def render_job(job):
            return job

        modules = [IPythonDisplay(contents=render_job)]

    :param contents: A callable accepting one argument of type
        :py:class:`signac.contrib.job.Job` and returning an object to be
        rendered with IPython's :code:`HTMLFormatter`.
    :type contents: callable
    """

    def __init__(
        self,
        name="IPython Display",
        contents=lambda job: "No contents provided.",
        **kwargs,
    ):
        super().__init__(
            name=name,
            context="JobContext",
            template="cards/ipython_display.html",
            **kwargs,
        )
        self.contents = contents

    def get_cards(self, job):
        contents = self.contents(job)
        if HTML_FORMATTER:
            html_contents = HTMLFormatter()(contents)
        else:
            html_contents = "Error: Install the 'IPython' library to render contents."
        return [
            {
                "name": self.name,
                "content": render_template(self.template, html_contents=html_contents),
            }
        ]
