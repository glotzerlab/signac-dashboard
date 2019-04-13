# signac-dashboard: visual data management and analysis

## About

Data visualization, analysis, and "dashboard" monitoring tool as part of the [signac framework](http://www.signac.io).
The `signac-dashboard` interface allows users to rapidly view data managed in a [signac project](http://signac.readthedocs.io/en/latest/projects.html).

*The software is currently in an early development stage.*

## Maintainers

  * Bradley Dice (bdice@umich.edu)

## Installation

The **signac-dashboard** app requires at least Python version 3.4!
To install this package, first clone the repository and install its submodules.
```bash
$ git clone https://github.com/glotzerlab/signac-dashboard.git
$ cd signac-dashboard
$ git submodule update --init --recursive
```
and then install using pip:
```bash
$ pip install .
```

## Documentation

Documentation is hosted on [signac-dashboard.readthedocs.io](https://signac-dashboard.readthedocs.io/en/latest/).

## Usage

You can start a dashboard to visualize *signac* project data in the browser, by importing the `Dashboard` class and calling its `main` function.

### Start a Dashboard

The code below will open a dashboard for an newly-initialized (empty) project, with no jobs and one module loaded. Write the file `dashboard.py` with these contents:

```python
#!/usr/bin/env python3
from signac_dashboard import Dashboard
from signac_dashboard.modules import ImageViewer

if __name__ == '__main__':
    dashboard = Dashboard(modules=[ImageViewer()])
    dashboard.main()
```

Then launch the dashboard with `python dashboard.py run`.

### Specifying a custom job title

By creating a class that inherits from `Dashboard` (which we'll call `MyDashboard`), we can begin to customize some of the functions that make up the dashboard, like `job_title(job)`, which gives a human-readable title to each job.

```python
class MyDashboard(Dashboard):

    def job_title(self, job):
        return 'Concentration(A) = {}'.format(job.sp['conc_A'])

if __name__ == '__main__':
    MyDashboard().main()
```

## Running dashboards on a remote host

To use dashboards hosted by a remote computer, open an SSH tunnel to the remote computer and forward the port where the dashboard is hosted. For example, connect to the remote computer with

```bash
ssh username@remote.server.org -L 8890:localhost:8888
```

to forward port 8888 on the host to port 8890 on your local computer.

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

### Statepoint Parameters

The `StatepointList` module shows the key-value pairs in the statepoint.

```python
from signac_dashboard.modules.statepoint_list import StatepointList
sp_mod = StatepointList()
```

### Job Document

The `DocumentList` module shows the key-value pairs in the job document, with long values optionally truncated (default is no truncation).

```python
from signac_dashboard.modules.document_list import DocumentList
doc_mod = DocumentList(max_chars=140)  # Output will be truncated to one tweet length
```

### File List

The `FileList` module shows a listing of the job's workspace directory with links to each file. This can be very slow since it has to read the disk for every job displayed, use with caution in large signac projects.

```python
from signac_dashboard.modules.file_list import FileList
file_mod = FileList(enabled=False)  # Recommended to disable this module by default
```

### Image Viewer

The `ImageViewer` module displays images in any format that works with a standard HTML `<img>` tag. The module defaults to showing all images of PNG, JPG, or GIF types. A filename or glob can be defined to select specific filenames. Multiple Image Viewer modules can be defined with different filenames or globs to enable/disable cards individually.

```python
from signac_dashboard.modules.image_viewer import ImageViewer
img_mod = ImageViewer()  # Shows all PNG/JPG/GIF images
img_mod = ImageViewer(name='Bond Order Diagram', img_globs=['bod.png'])
```

### Video Viewer

The `VideoViewer` module displays videos using a standard HTML `<video>` tag. The module defaults to showing all videos of MP4 or M4V types. A filename or glob can be defined to select specific filenames, which may be of any format supported by your browser with the `<video>` tag. A "poster" can be defined, which shows a thumbnail with that filename before the video is started. Videos do not preload by default, since file sizes can be large and there may be many videos on a page. To enable preloading, use the argument `preload='auto'` or `preload='metadata'`. Multiple Video Viewer modules can be defined with different filenames or globs to enable/disable cards individually.

```python
from signac_dashboard.modules.video_viewer import VideoViewer
video_mod = VideoViewer()  # Shows all MP4/M4V videos
video_mod = VideoViewer(name='Cool Science Video',
                        video_globs=['cool_science.mp4'],
                        poster='cool_science_thumbnail.jpg',
                        preload='none')
```

### Notes

The `Notes` module uses the `'notes'` key in the job document to store plain text, perhaps human-readable descriptions of a job that may be useful in later analysis.

```python
from signac_dashboard.modules.notes import Notes
notes_mod = Notes()
```

## Searching jobs

The search bar accepts JSON-formatted queries in the same way as the `signac find` command-line tool. For example, using the query `{"key": "value"}` will return all jobs where the job statepoint `key` is set to `value`. To search jobs by their document key-value pairs, use `doc:` before the JSON-formatted query, like `doc:{"key": "value"}`.

## Tips for Developers

During continuous integration, the code is checked with `flake8`. Run the following commands to [set up a pre-commit hook](http://flake8.pycqa.org/en/latest/user/using-hooks.html) that will ensure your code is compliant before pushing.

```bash
flake8 --install-hook git
git config --bool flake8.strict true
```
