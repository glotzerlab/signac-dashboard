# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
from time import sleep

class Logger(Module):
    def __init__(self,
                 filename,
                 num_lines=25,
                 name='Logger',
                 context='JobContext',
                 template='cards/logger.html',
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)
        self.filename = filename
        self.num_lines = num_lines

    def get_cards(self, job):
        return [{'name': self.name + ': ' + format(self.filename),
                'content': render_template(
                    self.template,
                    jobid=job._id,
                    filename=self.filename,
                    num_lines=self.num_lines
                    )}]

    def register(self, dashboard):
        @dashboard.app.route('/module/logger/<jobid>/<path:filename>/<int:stream>')
        def get_log(jobid,filename,stream):
            job = dashboard.project.open_job(id=jobid)
            def generate():
                with open(job.fn(filename)) as f:
                    while True:
                        yield f.read()
                        if not stream:
                            break
                        sleep(1)

            return dashboard.app.response_class(generate(), mimetype='text/plain')

