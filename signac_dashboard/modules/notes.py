# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from flask import abort, render_template, request
from jinja2.exceptions import TemplateNotFound

from signac_dashboard.module import Module


class Notes(Module):
    """Displays a text box that is synced to the job document.

    The contents of the text box are saved to :code:`job.document['notes']`.
    The Notes module can be used to annotate a large data space with tags or
    human-readable descriptions for post-processing, parsing, or searching.

    :param key: Document key to display and update (default: :code:`'notes'`).
    :type key: str
    """

    def __init__(
        self,
        name="Notes",
        context="JobContext",
        template="cards/notes.html",
        key="notes",
        **kwargs,
    ):
        super().__init__(name=name, context=context, template=template, **kwargs)
        self.key = key

    def get_cards(self, job):
        note_text = job.document.get(self.key, "")
        return [
            {
                "name": self.name,
                "content": render_template(
                    self.template, note_text=note_text, jobid=job._id
                ),
            }
        ]

    def register(self, dashboard):
        # Register routes
        @dashboard.app.route("/module/notes/update", methods=["POST"])
        def notes_update():
            note_text = request.form.get("note_text")
            jobid = request.form.get("jobid")
            job = dashboard.project.open_job(id=jobid)
            job.document[self.key] = note_text
            return "Saved."

        @dashboard.app.route("/module/notes/<path:filename>")
        def notes_asset(filename):
            path = f"notes/{filename}"
            try:
                return render_template(path)
            except TemplateNotFound:
                abort(404, "The file requested does not exist.")

        # Register assets
        assets = ["js/notes.js"]
        for assetfile in assets:
            dashboard.register_module_asset(
                {
                    "file": f"templates/notes/{assetfile}",
                    "url": f"/module/notes/{assetfile}",
                }
            )
