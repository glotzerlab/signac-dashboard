# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
from importlib import import_module


class FlowStatus(Module):
    """Show job labels using status from a :py:class`flow.FlowProject`.

    This module imports a user-specified :py:class:`flow.FlowProject` and uses
    :py:meth:`flow.FlowProject.labels` to display labels for the provided job.

    :param project_module: The Python module containing the
        :py:class:`flow.FlowProject` (default: :code:`'project'`).
    :type project_module: str
    :param project_class: The name of the :py:class:`FlowProject` class
        (default: :code:`'Project'`).
    :type project_class: str
    """
    def __init__(self,
                 name='Flow Project Status',
                 context='JobContext',
                 template='cards/flow_status.html',
                 project_module='project',
                 project_class='Project',
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)
        self.project_module = project_module
        self.project_class = project_class
        self._flowproject = None

    def _get_flowproject(self):
        if self._flowproject is None:
            module = import_module(self.project_module)
            self._flowproject = getattr(module, self.project_class)()

    def get_cards(self, job):
        self._get_flowproject()
        labels = self._flowproject.labels(job)
        return [{'name': self.name,
                 'content': render_template(self.template, labels=labels)}]
