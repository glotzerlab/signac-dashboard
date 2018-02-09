# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template, url_for, request


class Notes(Module):

    def __init__(self, **kwargs):
        super().__init__(name='Notes',
                         context='JobContext',
                         template='cards/notes.html',
                         **kwargs)

    def get_cards(self, job):
        note_text = job.document.get('notes', '')
        notes_action = url_for('update_notes')
        return [{'name': self.name, 'content': render_template(
            self.template, notes_action=notes_action, note_text=note_text,
            jobid=str(job))}]

    def register_routes(self, dashboard):
        @dashboard.app.route('/notes/update', methods=['POST'])
        def update_notes():
            note_text = request.form.get('note_text')
            jobid = request.form.get('jobid')
            job = dashboard.project.open_job(id=jobid)
            job.document['notes'] = note_text
            # redirect(request.form.get('redirect', url_for('home')))
            return "Saved."
