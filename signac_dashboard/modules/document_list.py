# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from signac_dashboard.util import ellipsis_string
from flask import render_template
from jinja2 import escape
from collections import OrderedDict


class DocumentList(Module):
    """Displays the job document.

    Long values can be optionally truncated.

    :param max_chars: Truncation length for document values (default:
        :code:`None`).
    :type max_chars: int
    """
    def __init__(self,
                 name='Job Document',
                 context='JobContext',
                 template='cards/document_list.html',
                 max_chars=None,
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)
        self.max_chars = max_chars

    def get_cards(self, job):
        doc = OrderedDict(sorted(job.document.items(), key=lambda t: t[0]))

        # We manually escape the document's contents since the field is marked
        # "safe" in the Jinja template. This is necessary because we added
        # custom HTML for "[Truncated]" fields
        if self.max_chars is not None and int(self.max_chars) > 0:
            for key in doc:
                if len(str(doc[key])) > self.max_chars:
                    doc[key] = str(escape(
                        ellipsis_string(doc[key], length=self.max_chars)
                    )) + ' <em>[Truncated]</em>'
        else:
            for key in doc:
                doc[key] = escape(doc[key])

        return [{'name': self.name,
                 'content': render_template(self.template, document=doc)}]
