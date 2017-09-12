# signac-dashboard: visual data management and analysis

## About

Data visualization, analysis, and "dashboard" monitoring tool based on the signac and signac-flow frameworks.

The signac-dashboard interface allows users to rapidly view content contained in a [signac project](https://glotzerlab.engin.umich.edu/signac).
Additionally, users may monitor the current progress of their work if the signac project is also managed using [signac-flow](https://signac-flow.readthedocs.io/en/latest/).

The software is currently in an early development stage.

## Maintainers

  * Bradley Dice (bdice@umich.edu)

## Usage
This software is an installable package similar to signac-flow, where users' code includes a class that inherits from the base class implemented in signac-dashboard. This enables high extensibility to meet project-specific needs.

### Dissecting the Dashboard Structure
- *Jobs* are how signac manages data. Each job has a statepoint (which contains job metadata) and a document (for persistent storage of key-value pairs). Jobs can be displayed in *list view* or *grid view*. The list view provides quick descriptions and status information from many jobs, while the grid view is intended to show text and media content from one or more jobs.
- *Templates* provide the HTML structure of the dashboard's pages, written in Jinja template syntax for rendering content on the server
- *Modules* are server-side Python code that interface with your signac data to display content. Generally, a module will render content from a specific *job* into a *card template*.
- *Cards* are a type of template that is shown in *grid view* and contains content rendered by a *module*.

### Quickstart
The code below will open a dashboard for an newly-initialized (empty) project, with no jobs and no modules loaded.

```python
#!/usr/bin/env python3
from signac_dashboard import Dashboard
from signac import init_project

if __name__ == '__main__':

    project = init_project('dashboard-test-project')
    config = {}  # dictionary of options
    modules = [] # list of modules
    dashboard = Dashboard(config=config, project=project, modules=modules)
    dashboard.run(host='localhost', port=8888)
```

### Adding Modules

```python
# Import a module
from signac_dashboard.modules.statepoint_list import StatepointList

# Initialize the module
sp_mod = StatepointList()

# Make a list of the initialized modules
modules = [sp_mod]

# Run the dashboard
dashboard = Dashboard(config=config, project=project, modules=modules)
dashboard.run(host='localhost', port=8888)
```

### Adding a custom job title
By creating a class that inherits from `Dashboard` (which we'll call `MyDashboard`), we can begin to customize some of the functions that make up the dashboard, like `job_title(job)`, which gives a human-readable title to each job.

```python
class MyDashboard(Dashboard):
    def job_title(self, job):
        return 'Concentration(A) = {}'.format(job.sp['conc_A'])

dashboard = MyDashboard(project=project)
dashboard.run(host='localhost', port=8888)
```
