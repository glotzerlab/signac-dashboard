# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template, Markup
try:
    import markdown
    MARKDOWN = True
except ImportError:
    MARKDOWN = False


class TextDisplay(Module):
    """Render custom text or Markdown in a card.

    This module calls a user-provided function to display text or Markdown
    content in a card. Rendering Markdown requires the :code:`markdown`
    library to be installed. Example:

    .. code-block:: python

        def my_text(job):
            return 'This job id is {}.'.format(str(job))

        modules = [TextDisplay(message=my_text)]

    :param message: A callable accepting one argument of type
        :py:class:`signac.contrib.job.Job` and returning text or Markdown
        content.
    :type message: callable
    :param markdown: Enables Markdown rendering if True (default: False).
    :type markdown: bool
    """

    def __init__(self, name='Text Display',
                 message=lambda job: 'No message provided.',
                 markdown=False, **kwargs):
        super().__init__(name=name,
                         context='JobContext',
                         template='cards/text_display.html',
                         **kwargs)
        self.message = message
        self.markdown = markdown

    def get_cards(self, job):
        msg = self.message(job)
        if self.markdown:
            if MARKDOWN:
                msg = Markup(markdown.markdown(
                    msg, extensions=['markdown.extensions.attr_list']))
            else:
                msg = ('Error: Must install markdown library to render '
                       'Markdown.')
        return [{'name': self.name,
                 'content': render_template(self.template, msg=msg)}]
