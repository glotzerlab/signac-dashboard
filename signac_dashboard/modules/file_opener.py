# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from flask import abort, render_template, request
from jinja2.exceptions import TemplateNotFound
import os

from signac_dashboard.module import Module


class FileOpener(Module):
    """Display a button that runs a user-defined command to open a file when \
            clicked.

    This can be useful for browsing through jobs in the dashboard, but need to
    do something specific on a per-job basis. One could write a function that
    opens a specific file in the job workspace, e.g., to open a simulation
    trajectory in a visualization application for a more detailed visualization
    of the data in that specific job.

    For security reasons (e.g., to guard against code-injection attacks), this
    module should not be used with a server configuration that makes the
    dashboard publicly accessible.
    """

    def __init__(
        self,
        name="File opener",
        context="JobContext",
        template="cards/file_opener.html",
        open_command="open",
        filename="",
        **kwargs,
    ):
        super().__init__(name=name, context=context, template=template, **kwargs)
        self.open_cmd = open_command
        self.filename = filename

    def get_cards(self, job):
        return [
            {
                "name": self.name,
                "content": render_template(
                    self.template, jobid=job._id
                ),
            }
        ]

    def register(self, dashboard):
        # Register routes
        @dashboard.app.route("/module/file_opener/update", methods=["POST"])
        def file_opener_update():
            jobid = request.form.get("jobid")
            job = dashboard.project.open_job(id=jobid)
            if not job.isfile(self.filename):
                return "File not found."
            full_filename = job.fn(self.filename)
            cmd = f'{self.open_cmd} {full_filename}'
            os.system(cmd)
            return "Nice click!"

        @dashboard.app.route("/module/file_opener/<path:filename>")
        def file_opener_asset(filename):
            path = f"file_opener/{filename}"
            try:
                return render_template(path)
            except TemplateNotFound:
                abort(404, "The file requested does not exist.")

        # Register assets
        assets = ["js/file_opener.js"]
        for assetfile in assets:
            dashboard.register_module_asset(
                {
                    "file": f"templates/file_opener/{assetfile}",
                    "url": f"/module/file_opener/{assetfile}",
                }
            )
