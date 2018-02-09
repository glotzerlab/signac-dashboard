# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from flask import render_template


class Module():

    def __init__(self, name, context, template, enabled=True):
        self.name = name
        self.context = context
        self.template = template
        self.enabled = enabled

    def get_cards(self):
        # Returns an array of dictionaries with properties 'name' and
        # 'content':
        return [{'name': self.name, 'content': render_template(self.template)}]

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled

    def is_enabled(self):
        return self.enabled

    def register_assets(self, dashboard):
        pass

    def register_routes(self, dashboard):
        pass
