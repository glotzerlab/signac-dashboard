# <img src="https://raw.githubusercontent.com/glotzerlab/signac-dashboard/master/doc/images/palette-header.png" width="75" height="58"> signac-dashboard: data visualization for signac

[![PyPI](https://img.shields.io/pypi/v/signac-dashboard.svg)](https://pypi.org/project/signac-dashboard/)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/signac-dashboard.svg?style=flat)](https://anaconda.org/conda-forge/signac-dashboard)
![CircleCI](https://img.shields.io/circleci/project/github/glotzerlab/signac-dashboard/master.svg)
[![RTD](https://img.shields.io/readthedocs/signac-dashboard.svg?style=flat)](https://docs.signac.io)
[![License](https://img.shields.io/github/license/glotzerlab/signac-dashboard.svg)](https://github.com/glotzerlab/signac-dashboard/blob/master/LICENSE.txt)
[![PyPI-downloads](https://img.shields.io/pypi/dm/signac-dashboard.svg?style=flat)](https://pypistats.org/packages/signac-dashboard)
[![Gitter](https://img.shields.io/gitter/room/signac/Lobby.svg?style=flat)](https://gitter.im/signac/Lobby)
[![Twitter](https://img.shields.io/twitter/follow/signacdata?style=social)](https://twitter.com/signacdata)
[![GitHub Stars](https://img.shields.io/github/stars/glotzerlab/signac-dashboard?style=social)](https://github.com/glotzerlab/signac-dashboard/)

Built on top of the **signac** framework, **signac-dashboard** allows users to rapidly visualize and analyze data managed in a [**signac** project](https://docs.signac.io/en/latest/projects.html).

## Resources

- [Dashboard topic guide](https://docs.signac.io/en/latest/dashboard.html):
  Introduction to **signac-dashboard**.
- [Dashboard documentation](https://docs.signac.io/projects/dashboard/):
  Package reference and APIs.
- [Dashboard examples](examples/):
  Example dashboards demonstrating a variety of use cases.
- [Framework documentation](https://docs.signac.io/):
  Examples, tutorials, topic guides, and package Python APIs.
- [Chat Support](https://gitter.im/signac/Lobby):
  Get help and ask questions on the **signac** gitter channel.
- [**signac** website](https://signac.io/):
  Framework overview and news.

## Installation

The recommended installation method for **signac-dashboard** is through **conda** or **pip**.
The software is tested for Python 3.6+ and is built for all major platforms.

To install **signac-dashboard** *via* the [conda-forge](https://conda-forge.github.io/) channel, execute:

```bash
conda install -c conda-forge signac-dashboard
```

To install **signac-dashboard** *via* **pip**, execute:

```bash
pip install signac-dashboard
```

**Detailed information about alternative installation methods can be found in the [documentation](https://docs.signac.io/projects/dashboard/en/latest/installation.html).**


## Quickstart

In an existing **signac** project directory, create a file `dashboard.py`:

```python
from signac_dashboard import Dashboard
from signac_dashboard.modules import StatepointList, DocumentList, ImageViewer

if __name__ == '__main__':
    modules = [StatepointList(), DocumentList(), ImageViewer()]
    Dashboard(modules=modules).main()
```

Then launch the dashboard:

```bash
$ python dashboard.py run
```
