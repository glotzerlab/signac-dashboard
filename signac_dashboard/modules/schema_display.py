# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from collections import OrderedDict

from flask import render_template
from markupsafe import escape

from signac_dashboard.module import Module
from signac_dashboard.util import ellipsis_string


class SchemaView(Module):
    """Displays the project schema.

    Long values can be optionally truncated.

    :param max_chars: Truncation length for document values (default:
        :code:`None`).
    :type max_chars: int
    """

    def __init__(
        self,
        name="Project Schema",
        context="ProjectContext",
        template="cards/document_list.html",
        max_chars=None,
        exclude_const=False,
        **kwargs,
    ):
        self._enabled_contexts = {"ProjectContext"}
        super().__init__(
            name=name,
            context=context,
            template=template,
            **kwargs,
        )
        self.max_chars = max_chars
        self.exclude_const = exclude_const

    def get_cards(self, project):
        schema = project.detect_schema(exclude_const=self.exclude_const)
        schema = OrderedDict(schema.items())

        # We manually escape the schema contents since the field is marked
        # "safe" in the Jinja template. This is necessary because we added
        # custom HTML for "[Truncated]" fields
        if self.max_chars is not None and int(self.max_chars) > 0:
            for key in schema:
                if len(str(schema[key])) > self.max_chars:
                    schema[key] = (
                        str(escape(ellipsis_string(schema[key], length=self.max_chars)))
                        + " <em>[Truncated]</em>"
                    )
        else:
            for key in schema:
                schema[key] = escape(schema[key])

        return [
            {
                "name": self.name,
                "content": render_template(self.template, document=schema),
            }
        ]
