# Copyright (c) 2017 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template, url_for, Markup
import os
import markdown

class TextDisplay(Module):

    def __init__(self, name='Text Display',
            text_function=lambda *args, **kwargs: 'No message provided.',
            markdown=False, **kwargs):
        super().__init__(name=name,
                         context='JobContext',
                         template='cards/text_display.html',
                         **kwargs)
        self.text_function = text_function
        self.markdown = markdown

    def get_cards(self, job):
        msg = self.text_function(job)
        if self.markdown:
            msg = Markup(markdown.markdown(msg, extensions=['markdown.extensions.attr_list']))
        return [{'name': self.name,
                 'content': render_template(self.template, msg=msg)}]
