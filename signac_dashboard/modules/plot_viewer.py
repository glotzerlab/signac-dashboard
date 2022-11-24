# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from typing import Callable, Dict, Iterable, List, Tuple, Union

from flask import abort, render_template
from jinja2.exceptions import TemplateNotFound
from signac import Project
from signac.contrib.job import Job

from signac_dashboard.dashboard import Dashboard
from signac_dashboard.module import Module


def plot_viewer_asset(filename):
    path = f"plot_viewer/{filename}"
    try:
        return render_template(path)
    except TemplateNotFound:
        abort(404, "The file requested does not exist.")


class PlotViewer(Module):
    """Displays a plot associated with the job"""

    _supported_contexts = {"JobContext", "ProjectContext"}

    def __init__(
        self,
        name="Plot Viewer",
        necessary_key: Callable[[Job], bool] = lambda _: True,
        plotly_args: Callable[
            [Union[Job, Project]], Iterable[Tuple[str, List[Dict], Dict]]
        ] = lambda _: list(),
        context="JobContext",
        template="cards/plot_viewer.html",
        **kwargs,
    ):

        super().__init__(
            name=name,
            context=context,
            template=template,
            **kwargs,
        )
        self.necessary_key = necessary_key
        self.plotly_args = plotly_args

    def get_cards(self, job_or_project):
        if not self.necessary_key(job_or_project):
            return []

        return [
            {
                "name": title if title else self.name,
                "content": render_template(
                    self.template,
                    jobid=job_or_project.id,
                    plotlydata=data,
                    plotlylayout=layout,
                ),
            }
            for title, data, layout in self.plotly_args(job_or_project)
        ]

    def register(self, dashboard: Dashboard):
        # Register routes
        dashboard.app.route("/module/plot_viewer/<path:filename>")(plot_viewer_asset)

        # Register assets
        assets = ["js/plot_viewer.js"]
        for assetfile in assets:
            dashboard.register_module_asset(
                {
                    "file": f"templates/plot_viewer/{assetfile}",
                    "url": f"/module/plot_viewer/{assetfile}",
                }
            )
