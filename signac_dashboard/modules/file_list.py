# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template, url_for
import os


class FileList(Module):

    def __init__(self, **kwargs):
        super().__init__(name='File List',
                         context='JobContext',
                         template='cards/file_list.html',
                         **kwargs)

    def get_cards(self, job):
        job_files = os.listdir(job.workspace())
        files = list()
        for filename in job_files:
            files.append({
                'name': filename,
                'url': url_for('get_file', jobid=str(job), filename=filename)
            })
        files = sorted(files, key=lambda file: file['name'])
        return [{'name': self.name,
                 'content': render_template(self.template, files=files)}]
