#!/usr/bin/env python3
from signac_dashboard import Dashboard
from signac import init_project

if __name__ == '__main__':

    project = init_project('dashboard-test-project')
    config = {}
    modules = []
    dashboard = Dashboard(config=config, project=project, modules=modules)
    dashboard.run(host='localhost', port=8888)
