from signac_dashboard.module import Module
from flask import render_template
from collections import OrderedDict

class StatepointList(Module):

    def __init__(self):
        super().__init__(name='Statepoint Parameters',
                         context='JobContext',
                         template='panels/statepoint_list.html')

    def get_panels(self, job):
        sp = OrderedDict(sorted(job.statepoint().items(), key=lambda t: t[0]))
        return [{'name': self.name,
                'content': render_template(self.template, statepoint=sp)}]
