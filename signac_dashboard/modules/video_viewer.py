# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
import os
import glob
import itertools


class VideoViewer(Module):
    """Displays videos in the job workspace that match a glob.

    :param video_globs: A list of glob expressions or exact filenames to be
        displayed, one per card (default: :code:`['*.mp4', '*.m4v']`).
    :type video_globs: list
    :param preload: Option for preloading videos, one of :code:`'auto'`,
        :code:`'metadata'`, or :code:`'none'` (default: :code:`'none'`).
    :type preload: str
    :param poster: A path in the job workspace for a poster image to be shown
        before a video begins playback (default: :code:`None`).
    :type poster: str
    """
    def __init__(self,
                 name='Video Viewer',
                 context='JobContext',
                 template='cards/video_viewer.html',
                 video_globs=['*.mp4', '*.m4v'],
                 preload='none',    # auto|metadata|none
                 poster=None,
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)
        self.preload = preload
        self.poster = poster
        self.video_globs = video_globs

    def get_cards(self, job):
        def make_card(filename):
            jobid = job._id
            if not job.isfile(filename):
                raise FileNotFoundError('The filename {} could not be found '
                                        'for job {}.'.format(filename, jobid))
            return {'name': self.name + ': ' + filename,
                    'content': render_template(
                        self.template,
                        jobid=jobid,
                        poster=self.poster if self.poster and job.isfile(
                            self.poster) else None,
                        preload=self.preload,
                        filename=filename)}

        video_globs = [glob.iglob(job.workspace() + os.sep + video_glob)
                       for video_glob in self.video_globs]
        video_files = itertools.chain(*video_globs)
        for filepath in video_files:
            yield make_card(os.path.basename(filepath))
