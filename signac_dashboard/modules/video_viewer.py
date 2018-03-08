# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template, url_for
import os
import glob
import itertools


class VideoViewer(Module):

    def __init__(self, name='Video Viewer',
                 video_globs=['*.mp4', '*.m4v'],
                 preload='none',    # auto|metadata|none
                 poster=None, **kwargs):
        super().__init__(name=name,
                         context='JobContext',
                         template='cards/video_viewer.html',
                         **kwargs)
        self.preload = preload
        self.poster = poster
        self.video_globs = video_globs

    def get_cards(self, job):
        def make_card(filename):
            jobid = str(job)
            if job.isfile(filename):
                videosrc = url_for('get_file',
                                   jobid=jobid,
                                   filename=filename)
            else:
                raise FileNotFoundError('The filename {} could not be found '
                                        'for job {}.'.format(filename, jobid))
            if self.poster is not None and job.isfile(self.poster):
                postersrc = url_for('get_file',
                                    jobid=jobid,
                                    filename=self.poster)
            else:
                postersrc = None
            return {'name': self.name + ': ' + filename,
                    'content': render_template(
                        self.template,
                        videosrc=videosrc,
                        postersrc=postersrc,
                        preload=self.preload,
                        filename=filename)}

        video_globs = [glob.iglob(job.workspace() + os.sep + video_glob)
                       for video_glob in self.video_globs]
        video_files = itertools.chain(*video_globs)
        for filepath in video_files:
            yield make_card(os.path.basename(filepath))
