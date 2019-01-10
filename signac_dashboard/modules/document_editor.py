# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template, request, abort
from jinja2 import escape
from collections import OrderedDict
from ast import literal_eval


class DocumentEditor(Module):

    def __init__(self,
                 name='DocumentEditor',
                 context='JobContext',
                 template='cards/document_editor.html',
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)

    def get_cards(self, job):
        doc = OrderedDict(sorted(job.document.items(), key=lambda t: t[0]))

        for key in doc:
            if key.startswith('_'):
                # Don't allow users to edit "private" keys that begin with _
                del doc[key]
            else:
                doc[key] = escape(doc[key])
        return [{'name': self.name, 'content': render_template(
            self.template, document=doc, jobid=job._id)}]

    def register_routes(self, dashboard):
        @dashboard.app.route('/module/document_editor/update', methods=['POST'])
        def document_editor_update():
            jobid = request.form.get('jobid')
            job = dashboard.project.open_job(id=jobid)
            for key, value in request.form.items():
                if key.startswith('doc:'):
                    key = key[4:]
                    try:
                        job.doc[key] = literal_eval(value)
                    except SyntaxError as e:
                        return "Key {} failed: {}".format(key, repr(e))
            return "Saved."

        @dashboard.app.route('/module/document_editor/<path:filename>')
        def document_editor_asset(filename):
            path = 'document_editor/{}'.format(filename)
            try:
                return render_template(path)
            except TemplateNotFound:
                abort(404, 'The file requested does not exist.')

    def register_assets(self, dashboard):
        assets = ['js/document_editor.js']
        for assetfile in assets:
            dashboard.register_module_asset({
                'file': 'templates/document_editor/{}'.format(assetfile),
                'url': '/module/document_editor/{}'.format(assetfile)
            })
