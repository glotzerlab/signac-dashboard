# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import mimetypes
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

    def _get_icon(self, filename):
        _, ext = os.path.splitext(filename)
        ext = ext.lstrip(".").lower()

        icon_map = {
            "pdf": "fa-file-pdf",
            "zip": "fa-file-archive",
            "tar": "fa-file-archive",
            "gz": "fa-file-archive",
            "7z": "fa-file-archive",
        }
        if ext in icon_map:
            return icon_map[ext]

        mtype, _ = mimetypes.guess_type(filename)
        if mtype:
            if mtype.startswith("image/"):
                return "fa-file-image"
            if mtype.startswith("audio/"):
                return "fa-file-audio"
            if mtype.startswith("video/"):
                return "fa-file-video"
            if "word" in mtype:
                return "fa-file-word"
            if "excel" in mtype or "spreadsheet" in mtype or "csv" in mtype:
                return "fa-file-excel"
            if "powerpoint" in mtype or "presentation" in mtype:
                return "fa-file-powerpoint"
            if "x-" in mtype or "json" in mtype:
                return "fa-file-code"
            if mtype.startswith("text/"):
                return "fa-file-alt"

        return "fa-file"

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
                    "icon": self._get_icon(filename),
                }
                for filename in os.listdir(job.path)
            ),
            key=lambda filedata: filedata["name"],
        )
        return [
            {"name": self.name, "content": render_template(self.template, files=files)}
        ]
