from flask import render_template

class Module():

    def __init__(self, name, context, template):
        self.name = name
        self.context = context
        self.template = template

    def render(self):
        render_template(template)
