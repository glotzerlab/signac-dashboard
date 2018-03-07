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
                 img_globs=['*.mp4', '*.m4v'],
                 preload='none',    # auto|metadata|none
                 poster=None, **kwargs):
        super().__init__(name=name,
                         context='JobContext',
                         template='cards/video_viewer.html',
                         **kwargs)
        self.preload = preload
        self.poster = poster
        self.img_globs = img_globs

    def get_cards(self, job):
        def make_card(filename):
            return {'name': self.name + ': ' + filename,
                    'content': render_template(
                        self.template,
                        videosrc=url_for('get_file',
                                         jobid=str(job),
                                         filename=filename),
                        postersrc=url_for('get_file',
                                          jobid=str(job),
                                          filename=self.poster),
                        preload=self.preload,
                        filename=filename)}

        image_globs = [glob.iglob(job.workspace() + os.sep + image_glob)
                       for image_glob in self.img_globs]
        image_files = itertools.chain(*image_globs)
        for filepath in image_files:
            yield make_card(os.path.basename(filepath))
