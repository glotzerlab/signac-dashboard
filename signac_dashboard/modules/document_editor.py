# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template, request, abort
from jinja2 import escape
from jinja2.exceptions import TemplateNotFound
from collections import OrderedDict
from ast import literal_eval


class DocumentEditor(Module):
    """Provides an interface to edit the job document.

    This module shows keys in the job document with a form that allows users
    to edit their contents. When saving, the edited strings are parsed into
    JSON-compatible Python data structures (e.g., :py:class:`list` and
    :py:class:`dict`). Job document keys beginning with an underscore
    :code:`_` are treated as private and are not displayed.
    """
    def __init__(self,
                 name='Document Editor',
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
                doc[key] = escape(repr(doc[key]))
        return [{'name': self.name, 'content': render_template(
            self.template, document=doc, jobid=job._id)}]

    def register(self, dashboard):
        # Register routes
        @dashboard.app.route('/module/document_editor/update',
                             methods=['POST'])
        def document_editor_update():
            jobid = request.form.get('jobid')
            job = dashboard.project.open_job(id=jobid)
            for key, value in request.form.items():
                if key.startswith('doc:'):
                    key = key[4:]
                    try:
                        job.doc[key] = literal_eval(value)
                    except (SyntaxError, TypeError, ValueError) as e:
                        return "Error in key <strong>{}</strong>: {}".format(
                            key, e), 422
            return "Saved."

        @dashboard.app.route('/module/document_editor/<path:filename>')
        def document_editor_asset(filename):
            path = 'document_editor/{}'.format(filename)
            try:
                return render_template(path)
            except TemplateNotFound:
                abort(404, 'The file requested does not exist.')

        # Register assets
        assets = ['js/document_editor.js']
        for assetfile in assets:
            dashboard.register_module_asset({
                'file': 'templates/document_editor/{}'.format(assetfile),
                'url': '/module/document_editor/{}'.format(assetfile)
            })
