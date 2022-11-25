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
    """Displays a plot associated with the job

    The PlotViewer module can display an interactive plot by using the
    Plotly JavaScript library.

    :param name: Default name for the card. Ignored if the :code:`plotly_args`
        callable provides one for each card.
    :type name: str
    :param plotly_args: A callable that accepts a job (in the :code:`'JobContext'`)
        or a project (in the :code:`'ProjectContext'`) and returns an iterable. Each
        element will constitute a new card and will be composed of a tuple of three
        elements: the card title, the plotly data and the plotly layout specification.
    :type plotly_args: callable
    :param context: Supports :code:`'JobContext'` and :code:`'ProjectContext'`.
    :type context: str
    """

    _supported_contexts = {"JobContext", "ProjectContext"}

    def __init__(
        self,
        name="Plot Viewer",
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
        self.plotly_args = plotly_args

    def get_cards(self, job_or_project):
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
        assets = ["js/plot_viewer.js", "js/plotly-2.16.1.min.js"]
        for assetfile in assets:
            dashboard.register_module_asset(
                {
                    "file": f"templates/plot_viewer/{assetfile}",
                    "url": f"/module/plot_viewer/{assetfile}",
                }
            )
