# Copyright (c) 2020 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
from time import sleep


class Logger(Module):
    """Follows a text file.

    Serves a text file in the job workspace, with the option to periodically
    refresh its contents. This behaves similarly to ``tail -f``.

    :param filename: The name of the text file to follow.
    :type filename: str
    :param num_lines: How many lines of text should be displayed in the window,
                      counting backwards from the end of the file (default:
                      25).
    :type num_lines: int
    :param interval: Number of seconds to sleep in between file refreshes
                     (default: 1).
    :type interval: float
    """
    def __init__(self,
                 filename=None,
                 num_lines=25,
                 interval=1,
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
        self.interval = interval

    def get_cards(self, job):
        return [{'name': self.name + ': ' + format(self.filename),
                 'content': render_template(
                     self.template,
                     jobid=job._id,
                     filename=self.filename,
                     num_lines=self.num_lines
                     )}]

    def register(self, dashboard):
        @dashboard.app.route('/module/logger/<jobid>/<path:filename>/' +
                             '<int:stream>')
        def get_log(jobid, filename, stream):
            job = dashboard.project.open_job(id=jobid)

            def generate():
                if filename is None:
                    raise ValueError("filename argument not provided.\n")
                with open(job.fn(filename)) as f:
                    while True:
                        yield f.read()
                        if not stream:
                            break
                        sleep(self.interval)

            return dashboard.app.response_class(generate(),
                                                mimetype='text/plain')
