# signac-dashboard: visual data management and analysis

## About

Data visualization, analysis, and "dashboard" monitoring tool as part of the [signac framework](https://glotzerlab.engin.umich.edu/signac).
The signac-dashboard interface allows users to rapidly view data managed in a [signac project](http://signac.readthedocs.io/en/latest/projects.html).

*The software is currently in an early development stage.*

## Maintainers

  * Bradley Dice (bdice@umich.edu)

## Installation

Clone the repository with `git clone https://bitbucket.org/glotzer/signac-dashboard.git` and then install with

```bash
$ python setup.py install --user
```

## Usage

You can start a dashboard to visualize *signac* project data in the browser, by importing the `Dashboard` class and calling its run function.

### Start a Dashboard

The code below will open a dashboard for an newly-initialized (empty) project, with no jobs and one module loaded.

```python
#!/usr/bin/env python3
from signac_dashboard import Dashboard
from signac_dashboard.modules import ImageViewer


if __name__ == '__main__':
    dashboard = Dashboard(modules=[ImageViewer()])
    dashboard.run(host='localhost', port=8888)
```

### Specifying a custom job title

By creating a class that inherits from `Dashboard` (which we'll call `MyDashboard`), we can begin to customize some of the functions that make up the dashboard, like `job_title(job)`, which gives a human-readable title to each job.

```python
class MyDashboard(Dashboard):

    def job_title(self, job):
        return 'Concentration(A) = {}'.format(job.sp['conc_A'])

MyDashboard().run()
```

## Dissecting the Dashboard Structure

- *Jobs* are how signac manages data. Each job has a statepoint (which contains job metadata) and a document (for persistent storage of key-value pairs). Jobs can be displayed in *list view* or *grid view*. The list view provides quick descriptions and status information from many jobs, while the grid view is intended to show text and media content from one or more jobs.
- *Templates* provide the HTML structure of the dashboard's pages, written in Jinja template syntax for rendering content on the server
- *Modules* are server-side Python code that interface with your signac data to display content. Generally, a module will render content from a specific *job* into a *card template*.
- *Cards* are a type of template that is shown in *grid view* and contains content rendered by a *module*.
