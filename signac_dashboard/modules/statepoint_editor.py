# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from ast import literal_eval
from collections import OrderedDict

import flask_login
from flask import abort, render_template, request
from jinja2.exceptions import TemplateNotFound
from markupsafe import escape

from signac_dashboard.module import Module


class StatepointEditor(Module):
    """Provides an interface to edit the job state point.

    This module shows keys in the job state point with a form that allows users
    to edit their contents. When saving, the edited strings are parsed into
    JSON-compatible Python data structures (e.g., :py:class:`list` and
    :py:class:`dict`).

    :param context: Supports :code:`'JobInit'`.
    :type context: str
    """

    _supported_contexts = {"JobInit"}

    def __init__(
        self,
        name="State Point Editor",
        template="cards/statepoint_editor.html",
        **kwargs,
    ):
        super().__init__(
            name=name,
            context="JobInit",
            template=template,
            **kwargs,
        )

    def get_cards(self, job):
        sp = OrderedDict(sorted(job.statepoint.items(), key=lambda t: t[0]))

        for key in sp:
            sp[key] = escape(repr(sp[key]))
        return [
            {
                "name": self.name,
                "content": render_template(self.template, statepoint=sp, jobid=job._id),
            }
        ]

    def register(self, dashboard):
        # Register routes
        @dashboard.app.route("/module/statepoint_editor/update", methods=["POST"])
        @flask_login.login_required
        def statepoint_editor_update():
            #jobid = request.form.get("jobid")
            #job = dashboard.project.open_job(id=jobid)

            # todo need a way to update and store the state point even
            # when it's not attached to a job
            # sp = 
            for key, value in request.form.items():
                if key.startswith("sp:"):
                    key = key[3:]
                    try:
                        sp[key] = literal_eval(value)
                    except (SyntaxError, TypeError, ValueError) as e:
                        return (
                            f"Error in key <strong>{key}</strong>: {e}",
                            422,
                        )
            return "Saved."

        @dashboard.app.route("/module/statepoint_editor/<path:filename>")
        @flask_login.login_required
        def statepoint_editor_asset(filename):
            path = f"statepoint_editor/{filename}"
            try:
                return render_template(path)
            except TemplateNotFound:
                abort(404, "The file requested does not exist.")

        # Register assets
        assets = ["js/statepoint_editor.js"]
        for assetfile in assets:
            dashboard.register_module_asset(
                {
                    "file": f"templates/statepoint_editor/{assetfile}",
                    "url": f"/module/statepoint_editor/{assetfile}",
                }
            )
