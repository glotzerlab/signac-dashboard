# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from flask import render_template

from signac_dashboard.module import Module


class AwesomeModule(Module):
    """Displays the job's awesome factor."""

    def __init__(
        self,
        name="Awesome Factor",
        context="JobContext",
        template="cards/awesome_module.html",
        **kwargs,
    ):
        self._enabled_contexts = {"JobContext"}
        super().__init__(
            name=name,
            context=context,
            template=template,
            **kwargs,
        )

    def get_cards(self, job):
        return [
            {
                "name": self.name,
                "content": render_template(
                    self.template, awesome_factor=job.sp.get("awesome_factor", "not")
                ),
            }
        ]
