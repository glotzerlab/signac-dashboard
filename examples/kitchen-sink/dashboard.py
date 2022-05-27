#!/usr/bin/env python3
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import signac
from flow import FlowProject

import signac_dashboard.modules
from signac_dashboard import Dashboard


class Project(FlowProject):
    pass


if __name__ == "__main__":
    project = signac.init_project("dashboard-test-project")

    if len(project) == 0:
        for a in range(10):
            for b in range(10):
                project.open_job({"a": a, "b": b}).init()

    config = {
        "CARDS_PER_ROW": 4,
    }

    modules = []
    # Initialize a new Dashboard using all modules with default settings
    for m in signac_dashboard.modules.__all__:
        module = getattr(signac_dashboard.modules, m)
        for c in module._supported_contexts:
            modules.append(module(context=c))
    Dashboard(config=config, modules=modules, project=Project.get_project()).main()