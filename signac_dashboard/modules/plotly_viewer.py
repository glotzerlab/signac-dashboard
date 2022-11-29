# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import hashlib
from typing import Callable, Dict, List, Tuple, Union

import flask_login
from flask import abort, jsonify, render_template, request
from flask.views import View
from jinja2.exceptions import TemplateNotFound
from signac import Project
from signac.contrib.job import Job

from signac_dashboard.dashboard import Dashboard
from signac_dashboard.module import Module


class PlotlyView(View):
    decorators = [flask_login.login_required]

    def __init__(self, dashboard, args_function, context):
        self.dashboard = dashboard
        self.args_function = args_function
        self.context = context

    def dispatch_request(self):
        if self.context == "JobContext":
            jobid = request.args.get("jobid")
            job = self.dashboard.project.open_job(id=jobid)
            traces, layout = self.args_function(job)
        elif self.context == "ProjectContext":
            traces, layout = self.args_function(self.dashboard.project)
        else:
            raise NotImplementedError()
        return jsonify({"traces": traces, "layout": layout})


class PlotlyViewer(Module):
    """Displays a plot associated with the job.

    The PlotlyViewer module can display an interactive plot by using the
    Plotly JavaScript library. For information on the different accepted
    parameters for the data and layout, refer to the `Plotly JS documentation
    <https://plotly.com/javascript/>`_.

    Example:

    .. code-block:: python

        from signac_dashboard.modules import PlotlyViewer

        def plotly_args_function(project):
            return [
                (# each element on the data list is a different trace
                 [{
                    "x": [1, 2, 3, 4, 5],  # x coordinates of the trace
                    "y": [1, 2, 4, 8, 16]  # y coordinates of the trace
                 }],
                 {"margin": {"t": 0}}  # layout specification for the whole plot
                )
            ]

        plot_module = PlotlyViewer(plotly_args=plotly_args_function, context="ProjectContext")

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
    _assets_url_registered = False

    def __init__(
        self,
        name="Plotly Viewer",
        plotly_args: Callable[
            [Union[Job, Project]], Tuple[List[Dict], Dict]
        ] = lambda _: ([{}], {}),
        context="JobContext",
        template="cards/plotly_viewer.html",
        **kwargs,
    ):

        super().__init__(
            name=name,
            context=context,
            template=template,
            **kwargs,
        )
        self.plotly_args = plotly_args
        self.card_id = hashlib.sha1(str(id(self)).encode("utf-8")).hexdigest()

    def get_cards(self, job_or_project):
        return [
            {
                "name": self.name,
                "content": render_template(
                    self.template,
                    jobid=job_or_project.id,
                    endpoint=self.arguments_endpoint(),
                ),
            }
        ]

    def register(self, dashboard: Dashboard):
        # Register routes
        if not PlotlyViewer._assets_url_registered:

            @dashboard.app.route("/module/plotly_viewer/<path:filename>")
            @flask_login.login_required
            def plotly_viewer_asset(filename):
                try:
                    return render_template(f"plotly_viewer/{filename}")
                except TemplateNotFound:
                    abort(404, "The file requested does not exist.")

            # Register assets
            assets = [
                "/module/plotly_viewer/js/plotly_viewer.js",
                "https://cdn.plot.ly/plotly-2.16.1.min.js",
            ]
            for asseturl in assets:
                dashboard.register_module_asset({"url": asseturl})

            PlotlyViewer._assets_url_registered = True

        dashboard.app.add_url_rule(
            self.arguments_endpoint(),
            view_func=PlotlyView.as_view(
                f"plotly-{self.card_id}", dashboard, self.plotly_args, self.context
            ),
        )

    def arguments_endpoint(self):
        return f"/module/plotly_viewer/{self.card_id}/arguments"
