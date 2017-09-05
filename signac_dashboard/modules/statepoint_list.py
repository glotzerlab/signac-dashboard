from signac_dashboard.module import Module
from flask import render_template
from collections import OrderedDict

class StatepointList(Module):

    def __init__(self, **kwargs):
        super().__init__(name='Statepoint Parameters',
                         context='JobContext',
                         template='cards/statepoint_list.html',
                         **kwargs)

    def get_cards(self, job):
        sp = OrderedDict(sorted(job.statepoint().items(), key=lambda t: t[0]))
        return [{'name': self.name,
                'content': render_template(self.template, statepoint=sp)}]
