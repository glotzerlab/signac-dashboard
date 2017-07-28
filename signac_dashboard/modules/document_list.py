from signac_dashboard.module import Module
from flask import render_template
from collections import OrderedDict

class DocumentList(Module):

    def __init__(self):
        super().__init__(name='Job Document',
                         context='JobContext',
                         template='panels/document_list.html')

    def get_panels(self, job):
        doc = OrderedDict(sorted(job.document.items(), key=lambda t: t[0]))
        return [{'name': self.name,
                 'content': render_template(self.template, document=doc)}]
