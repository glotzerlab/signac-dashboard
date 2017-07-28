from signac_dashboard.module import Module
from flask import render_template, url_for
import os

class FileList(Module):

    def __init__(self):
        super().__init__(name='File List',
                         context='JobContext',
                         template='panels/file_list.html')

    def get_panels(self, job):
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
