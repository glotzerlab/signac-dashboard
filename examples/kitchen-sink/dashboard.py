#!/usr/bin/env python3
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard import Dashboard
import signac_dashboard.modules
import signac

if __name__ == '__main__':
    project = signac.init_project('dashboard-test-project')

    if len(project) == 0:
        for a in range(10):
            for b in range(10):
                project.open_job({'a': a, 'b': b}).init()

    modules = []
    if 'dashboard' not in project.document:
        # Initialize a new Dashboard using all modules with default settings
        for m in signac_dashboard.modules.__all__:
            modules.append(getattr(signac_dashboard.modules, m).__call__())
    Dashboard(modules=modules).main()
