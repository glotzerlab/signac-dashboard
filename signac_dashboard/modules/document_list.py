# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from collections import OrderedDict

from flask import render_template
from markupsafe import escape

from signac_dashboard.module import Module
from signac_dashboard.util import ellipsis_string


class DocumentList(Module):
    """Displays the job or project document, depending
    on the module context.

    Long values can be optionally truncated.

    :param max_chars: Truncation length for document values (default:
        :code:`None`).
    :type max_chars: int
    """

    def __init__(
        self,
        context="JobContext",
        name=None,
        template="cards/document_list.html",
        max_chars=None,
        **kwargs,
    ):
        # set name based on intialized context
        if name is None:
            if context == "JobContext":
                name = "Job Document"
            elif context == "ProjectContext":
                name = "Project Document"
        super().__init__(name=name, context=context, template=template, enabled_contexts = {"JobContext", "ProjectContext"}, **kwargs)
        self.max_chars = max_chars

    def get_cards(self, job_or_project):
        doc = OrderedDict(sorted(job_or_project.document.items(), key=lambda t: t[0]))

        # We manually escape the document's contents since the field is marked
        # "safe" in the Jinja template. This is necessary because we added
        # custom HTML for "[Truncated]" fields
        if self.max_chars is not None and int(self.max_chars) > 0:
            for key in doc:
                if len(str(doc[key])) > self.max_chars:
                    doc[key] = (
                        str(escape(ellipsis_string(doc[key], length=self.max_chars)))
                        + " <em>[Truncated]</em>"
                    )
        else:
            for key in doc:
                doc[key] = escape(doc[key])

        return [
            {"name": self.name, "content": render_template(self.template, document=doc)}
        ]
