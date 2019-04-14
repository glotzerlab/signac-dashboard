#!/usr/bin/env python3
# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard import Dashboard
from signac_dashboard.modules import StatepointList, FlowStatus


class FlowStatusDashboard(Dashboard):
    pass


if __name__ == '__main__':
    modules = [
        StatepointList(),
        FlowStatus(project_module='project', project_class='Project'),
    ]
    FlowStatusDashboard(modules=modules).main()
