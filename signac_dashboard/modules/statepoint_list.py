# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
from collections import OrderedDict


class StatepointList(Module):
    """Displays the job state point."""
    def __init__(self,
                 name='Statepoint Parameters',
                 context='JobContext',
                 template='cards/statepoint_list.html',
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)

    def get_cards(self, job):
        sp = OrderedDict(sorted(job.statepoint().items(), key=lambda t: t[0]))
        return [{'name': self.name,
                 'content': render_template(self.template, statepoint=sp)}]
