# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template, request, abort
from jinja2.exceptions import TemplateNotFound


class Notes(Module):

    def __init__(self,
                 name='Notes',
                 context='JobContext',
                 template='cards/notes.html',
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)

    def get_cards(self, job):
        note_text = job.document.get('notes', '')
        return [{'name': self.name, 'content': render_template(
            self.template, note_text=note_text, jobid=job._id)}]

    def register_routes(self, dashboard):
        @dashboard.app.route('/module/notes/update', methods=['POST'])
        def notes_update():
            note_text = request.form.get('note_text')
            jobid = request.form.get('jobid')
            job = dashboard.project.open_job(id=jobid)
            job.document['notes'] = note_text
            return "Saved."

        @dashboard.app.route('/module/notes/<path:filename>')
        def notes_asset(filename):
            path = 'notes/{}'.format(filename)
            try:
                return render_template(path)
            except TemplateNotFound:
                abort(404, 'The file requested does not exist.')

    def register_assets(self, dashboard):
        assets = ['js/notes.js']
        for assetfile in assets:
            dashboard.register_module_asset({
                'file': 'templates/notes/{}'.format(assetfile),
                'url': '/module/notes/{}'.format(assetfile)
            })
