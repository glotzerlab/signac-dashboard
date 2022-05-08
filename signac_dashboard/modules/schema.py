# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from flask import render_template

from signac_dashboard.module import Module
from signac_dashboard.util import escape_truncated_values


class Schema(Module):
    """Displays the project schema.

    Long values can be optionally truncated.

    :param max_chars: Truncation length for schema values (default:
        :code:`None`).
    :type max_chars: int
    :param exclude_const: Exclude all state point parameters that are shared by all jobs
        in this project (default: :code:`False`).
    :type exclude_const: bool
    :param subset: A sequence of jobs or job ids specifying a subset over which the state
        point schema should be detected (default: :code:`None`).
    """

    _supported_contexts = {"ProjectContext"}

    def __init__(
        self,
        name="Project Schema",
        context="ProjectContext",
        template="cards/escaped_dict_display.html",
        max_chars=None,
        exclude_const=False,
        subset=False,
        **kwargs,
    ):

        super().__init__(
            name=name,
            context=context,
            template=template,
            **kwargs,
        )
        self.max_chars = max_chars
        self.exclude_const = exclude_const
        self.subset = subset

    def get_cards(self, project):
        schema = project.detect_schema(
            exclude_const=self.exclude_const, subset=self.subset
        )
        schema = dict(schema.items())

        # We manually escape the schema contents since the field is marked
        # "safe" in the Jinja template. This is necessary because we added
        # custom HTML for "[Truncated]" fields
        schema = escape_truncated_values(schema, self.max_chars)

        return [
            {
                "name": self.name,
                "content": render_template(self.template, escaped_dict=schema),
            }
        ]
