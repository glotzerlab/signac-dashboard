# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
from collections import OrderedDict

try:
    from flow import FlowProject
except ImportError:
    raise RuntimeWarning('Need signac-flow installed.\n')

class FlowStatus(Module):

    def __init__(self,
                 name='Flow Project Status',
                 context='JobContext',
                 template='cards/flow_status.html',
                 project_file=None,
                 project_class=None,
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)
        self.project_file = project_file
        self.project_class = project_class

    def get_cards(self, job):
        import importlib
        if self.project_file is None:
            return None
        module = importlib.import_module(self.project_file)
        my_class = getattr(module,  self.project_class)
        obj = my_class()
        labels = obj.labels(job)
        return [{'name': self.name,
                 'content': render_template(self.template, labels=labels)}]
