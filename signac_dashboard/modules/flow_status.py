# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
from importlib import import_module


class FlowStatus(Module):
    """Show job labels using status from a FlowProject.

    This module determines job status from a signac-flow FlowProject and shows
    the job's current labels.

    :param project_module: The Python module containing the FlowProject
        (default: :code:`'project'`).
    :type project_module: str
    :param project_class: The name of the FlowProject class (default:
        :code:`'FlowProject'`).
    :type project_class: str
    """
    def __init__(self,
                 name='Flow Project Status',
                 context='JobContext',
                 template='cards/flow_status.html',
                 project_module='project',
                 project_class='FlowProject',
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)
        self.project_module = project_module
        self.project_class = project_class

    def get_cards(self, job):
        if self.project_module is None or self.project_class is None:
            return
        module = import_module(self.project_module)
        project = getattr(module, self.project_class)()
        labels = project.labels(job)
        return [{'name': self.name,
                 'content': render_template(self.template, labels=labels)}]
