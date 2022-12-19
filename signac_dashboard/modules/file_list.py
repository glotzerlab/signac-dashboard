# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import os

from flask import render_template

from signac_dashboard.module import Module


class FileList(Module):
    """Lists files in the job directory with download links.

    :param context: Supports :code:`'JobContext'`.
    :type context: str
    :param prefix_jobid: Whether filenames should be prefixed with the job id
        when being downloaded (default: :code:`True`).
    :type prefix_jobid: bool
    """

    _supported_contexts = {"JobContext"}

    def __init__(
        self,
        name="File List",
        context="JobContext",
        template="cards/file_list.html",
        prefix_jobid=True,
        **kwargs,
    ):

        super().__init__(
            name=name,
            context=context,
            template=template,
            **kwargs,
        )
        self.prefix_jobid = prefix_jobid

    def download_name(self, job, filename):
        if self.prefix_jobid:
            return f"{str(job)}_{filename}"
        else:
            return filename

    def get_cards(self, job):
        files = sorted(
            (
                {
                    "name": filename,
                    "jobid": job._id,
                    "download": self.download_name(job, filename),
                }
                for filename in os.listdir(job.path)
            ),
            key=lambda filedata: filedata["name"],
        )
        return [
            {"name": self.name, "content": render_template(self.template, files=files)}
        ]
