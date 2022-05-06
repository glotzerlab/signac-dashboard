# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from collections import OrderedDict

from flask import render_template

from signac_dashboard.module import Module
from signac_dashboard.util import escape_truncated_values


class DocumentList(Module):
    """Displays the job or project document.

    Long values can be optionally truncated.

    :param max_chars: Truncation length for document values (default:
        :code:`None`).
    :type max_chars: int
    """

    def __init__(
        self,
        name=None,
        context="JobContext",
        template="cards/trusted_dict_display.html",
        max_chars=None,
        **kwargs,
    ):
        # Set name based on context
        if name is None:
            if context == "JobContext":
                name = "Job Document"
            elif context == "ProjectContext":
                name = "Project Document"
        self._enabled_contexts = {"JobContext", "ProjectContext"}
        super().__init__(
            name=name,
            context=context,
            template=template,
            **kwargs,
        )
        self.max_chars = max_chars

    def get_cards(self, job_or_project):
        doc = OrderedDict(sorted(job_or_project.document.items(), key=lambda t: t[0]))

        # We manually escape the document's contents since the field is marked
        # "safe" in the Jinja template. This is necessary because we added
        # custom HTML for "[Truncated]" fields
        doc = escape_truncated_values(doc, self.max_chars)

        return [
            {
                "name": self.name,
                "content": render_template(self.template, escaped_dict=doc),
            }
        ]
