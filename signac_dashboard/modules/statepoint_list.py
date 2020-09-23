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
                 exclude_const=False,
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)
        self.exclude_const = exclude_const

    def get_cards(self, job):
        sp = [(k, v) for k, v in sorted(job.statepoint().items(),
              key=lambda t: t[0]) if k in self.sp_keys_to_show]
        sp = OrderedDict(sp)
        return [{'name': self.name,
                 'content': render_template(self.template, statepoint=sp)}]

    def register(self, dashboard):
        # always show all sp params for a single-job project
        if len(dashboard.project) == 1:
            excl_const = False
        else:
            excl_const = self.exclude_const
        schema = dashboard.project.detect_schema(exclude_const=excl_const)
        self.sp_keys_to_show = schema.keys()
