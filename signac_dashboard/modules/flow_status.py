# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template


class FlowStatus(Module):
    """Show job labels from a :py:class:`flow.FlowProject`.

    This module displays a card with labels from
    :py:meth:`flow.FlowProject.labels`. The user must provide an instance of
    :py:class:`flow.FlowProject` to the dashboard constructor. Example:

    .. code-block:: python

        from project import Project  # FlowProject subclass with labels
        from signac_dashboard import Dashboard

        if __name__ == '__main__':
            Dashboard(project=Project()).main()
    """
    def __init__(self,
                 name='Flow Status',
                 context='JobContext',
                 template='cards/flow_status.html',
                 project_module='project',
                 project_class='Project',
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)

    def register(self, dashboard):
        self.project = dashboard.project

    def get_cards(self, job):
        labels = self.project.labels(job)
        return [{'name': self.name,
                 'content': render_template(self.template, labels=labels)}]
