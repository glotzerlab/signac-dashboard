# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import flask_login
from flask import Blueprint, abort, redirect, render_template, request, url_for
from jinja2.exceptions import TemplateNotFound
from markupsafe import escape

from signac_dashboard.module import Module


class Notes(Module):
    """Displays a text box that is synced to the job document.

    The contents of the text box are saved to :code:`job.document['notes']`.
    The Notes module can be used to annotate a large data space with tags or
    human-readable descriptions for post-processing, parsing, or searching.

    :param context: Supports :code:`'JobContext'`.
    :type context: str
    :param key: Document key to display and update (default: :code:`'notes'`).
    :type key: str
    """

    _supported_contexts = {"JobContext"}

    def __init__(
        self,
        name="Notes",
        context="JobContext",
        template="cards/notes.html",
        key="notes",
        **kwargs,
    ):
        super().__init__(
            name=name,
            context=context,
            template=template,
            **kwargs,
        )
        self.key = key

        self.note_blueprint = Blueprint(
            name=key,
            import_name=key,
            url_prefix=f"/module/notes/{escape(key)}",
            template_folder=template,
        )
        print(self.note_blueprint)

    def get_cards(self, job):
        note_text = job.document.get(self.key, "")
        return [
            {
                "name": self.name,
                "content": render_template(
                    self.template, note_text=note_text, jobid=job.id, note_key=self.key
                ),
            }
        ]

    def register(self, dashboard):
        # Register routes
        @self.note_blueprint.route("/update", methods=["POST"])
        @flask_login.login_required
        def notes_update():
            note_text = request.form.get("note_text")
            print("key is", self.key)
            # breakpoint()
            jobid = request.form.get("jobid")
            job = dashboard.project.open_job(id=jobid)
            job.document[self.key] = note_text
            # return redirect(url_for("show_job", jobid=jobid))
            return "Saved."

        @self.note_blueprint.route("/<path:filename>")
        @flask_login.login_required
        def notes_asset(filename):
            path = f"notes/{filename}"
            try:
                return render_template(path)
            except TemplateNotFound:
                abort(404, "The file requested does not exist.")

        # Register assets
        assets = ["js/notes.js"]
        for asset_file in assets:
            dashboard.register_module_asset(
                {
                    "file": f"templates/notes/{asset_file}",
                    "url": f"/module/notes/{self.key}/{asset_file}",
                }
            )

        # register Blueprint
        dashboard.app.register_blueprint(self.note_blueprint)
        print(self.note_blueprint.root_path)
        # print(dashboard.app.url_map)
        for name, blueprint in dashboard.app.blueprints.items():
            print(f"Blueprint: {name}, URL prefix: {blueprint.url_prefix}")
