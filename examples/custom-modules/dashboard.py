#!/usr/bin/env python3
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard import Dashboard
from signac_dashboard.modules import StatepointList
from modules import AwesomeModule


class AwesomeDashboard(Dashboard):
    pass


if __name__ == '__main__':
    modules = []
    modules.append(StatepointList())

    # Add the custom module
    modules.append(AwesomeModule())

    # Tell the dashboard to search in this path for templates
    config = {'DASHBOARD_PATHS': '.'}

    AwesomeDashboard(config=config, modules=modules).main()
