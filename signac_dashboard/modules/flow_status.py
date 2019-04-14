# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template

try:
    from flow import FlowProject  # noqa: F401
except ImportError:
    raise RuntimeWarning('Need signac-flow installed.\n')


class FlowStatus(Module):
    """Show job labels using status from a FlowProject.

    This module determines job status from a signac-flow FlowProject and shows
    the job's current labels.

    :param project_file: The module containing the FlowProject (e.g.,
        :code:`'project.py'`).
    :type project_file: str
    :param project_class: The name of the FlowProject class (e.g.,
        :code:`'MyProject'`).
    :type project_class: str
    """
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
