# signac-dashboard: visual data management and analysis

## About

Data visualization, analysis, and "dashboard" monitoring tool as part of the [signac framework](https://glotzerlab.engin.umich.edu/signac).
The signac-dashboard interface allows users to rapidly view data managed in a [signac project](http://signac.readthedocs.io/en/latest/projects.html).

*The software is currently in an early development stage.*

## Maintainers

  * Bradley Dice (bdice@umich.edu)

## Installation

The **signac-dashboard** app requires at least Python version 3.4!
To install this package, first clone the repository and install its submodules.
```bash
$ git clone https://bitbucket.org/glotzer/signac-dashboard.git
$ cd signac-dashboard
$ git submodule update --init --recursive
```
and then install using pip:
```bash
$ pip install .
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

## Included Modules

Defining a module requires a *name* for display, a *context* to determine when the module should be shown (currently only `'JobContext'` is supported), and a *template* (written in HTML/Jinja-compatible syntax) where the content will be rendered. An optional `enabled` argument can be set to `False` to disable the module until it is selected by the user. A module must be a subclass of `Module` and define the function `get_cards()` which returns an array of dictionaries with properties `'name'` and `'content'`, like so:

```python
class MyModule(Module):

    def get_cards(self):
        return [{'name': 'My Module', 'content': render_template('path/to/template.html')}]
```

### Statepoint

The statepoint module shows the key-value pairs in the statepoint.

```python
sp_mod = StatepointList()
```

### Document

The document module shows the key-value pairs in the job document, with long values optionally truncated (default is no truncation).

```python
doc_mod = DocumentList(max_chars=140)  # Output will be truncated to one tweet length
```

### File List

The File List module shows a listing of the job's workspace directory with links to each file. This can be very slow since it has to read the disk for every job displayed, use with caution in large signac projects.

```python
file_mod = FileList(enabled=False)  # Recommended to disable this module by default
```

### Image Viewer

View images in any format that is supported by an HTML `<img>` tag in your browser. The module defaults to showing all images of PNG, JPG, or GIF types. A filename or glob can be defined to select specific filenames. Multiple Image Viewer modules can be defined to enable/disable each image type.

```python
img_mod = ImageViewer()  # Shows all PNG/JPG/GIF images
img_mod = ImageViewer(name='Bond Order Diagram', img_globs=['bod.png'])
```

### Notes

The Notes module uses the `'notes'` key in the job document to store plain text, perhaps human-readable descriptions of a job that may be useful in later analysis.

```python
notes_mod = Notes()
```
