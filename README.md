# <img src="https://raw.githubusercontent.com/glotzerlab/signac-dashboard/master/doc/images/palette-header.png" width="75" height="58"> signac-dashboard - data visualization for signac

[![Affiliated with NumFOCUS](https://img.shields.io/badge/NumFOCUS-affiliated%20project-orange.svg?style=flat&colorA=E1523D&colorB=007D8A)](https://numfocus.org/sponsored-projects/affiliated-projects)
[![PyPI](https://img.shields.io/pypi/v/signac-dashboard.svg)](https://pypi.org/project/signac-dashboard/)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/signac-dashboard.svg?style=flat)](https://anaconda.org/conda-forge/signac-dashboard)
![CircleCI](https://img.shields.io/circleci/project/github/glotzerlab/signac-dashboard/master.svg)
[![RTD](https://img.shields.io/readthedocs/signac-dashboard.svg?style=flat)](https://docs.signac.io)
[![License](https://img.shields.io/github/license/glotzerlab/signac-dashboard.svg)](https://github.com/glotzerlab/signac-dashboard/blob/master/LICENSE.txt)
[![PyPI-downloads](https://img.shields.io/pypi/dm/signac-dashboard.svg?style=flat)](https://pypistats.org/packages/signac-dashboard)
[![Slack](https://img.shields.io/badge/Slack-chat%20support-brightgreen.svg?style=flat&logo=slack)](https://signac.io/slack-invite/)
[![Twitter](https://img.shields.io/twitter/follow/signacdata?style=social)](https://twitter.com/signacdata)
[![GitHub Stars](https://img.shields.io/github/stars/glotzerlab/signac-dashboard?style=social)](https://github.com/glotzerlab/signac-dashboard/)

The [**signac** framework](https://signac.io) helps users manage and scale file-based workflows, facilitating data reuse, sharing, and reproducibility.

The **signac-dashboard** package allows users to rapidly visualize and analyze data from a **signac** project in a web browser.

## Resources

- [Dashboard topic guide](https://docs.signac.io/en/latest/dashboard.html):
  Introduction to **signac-dashboard**.
- [Dashboard documentation](https://docs.signac.io/projects/dashboard/):
  Package reference and APIs.
- [Dashboard examples](examples/):
  Example dashboards demonstrating a variety of use cases.
- [Framework documentation](https://docs.signac.io/):
  Examples, tutorials, topic guides, and package Python APIs.
- [Slack Chat Support](https://signac.io/slack-invite/):
  Get help and ask questions on the **signac** Slack workspace.
- [**signac** website](https://signac.io/):
  Framework overview and news.

## Installation

The recommended installation method for **signac-dashboard** is through **conda** or **pip**.
The software is tested for Python 3.7+ and is built for all major platforms.

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
