# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import glob
import itertools
import os

from flask import render_template

from signac_dashboard.module import Module


class VideoViewer(Module):
    """Displays videos that match a glob.

    The VideoViewer module displays videos using an HTML ``<video>`` tag. The
    module defaults to showing all videos of MP4 or M4V types in the job or
    project root directory. A filename or glob can be defined to select specific
    filenames, which may be of any format supported by your browser with the
    ``<video>`` tag. Each matching file yields a card.

    A "poster" can be defined, which shows a
    thumbnail with that filename before the video is started. Videos do not
    preload by default since file sizes can be large and there may be many
    videos on a page. To enable preloading, use the argument ``preload='auto'``
    or ``preload='metadata'``.

    Multiple VideoViewer modules can be defined
    with different filenames or globs to enable/disable cards individually.
    Examples:

    .. code-block:: python

        from signac_dashboard.modules import VideoViewer
        video_mod = VideoViewer()  # Shows all MP4/M4V videos
        video_mod = VideoViewer(name='Cool Science Video',
                                context="ProjectContext",
                                video_globs=['cool_science.mp4'],
                                poster='cool_science_thumbnail.jpg',
                                preload='none')

    :param context: Supports :code:`'JobContext'` and :code:`'ProjectContext'`.
    :type context: str
    :param video_globs: A list of glob expressions or exact filenames,
        relative to the job or project root directory, to be
        displayed (default: :code:`['*.mp4', '*.m4v']`).
    :type video_globs: list
    :param preload: Option for preloading videos, one of :code:`'auto'`,
        :code:`'metadata'`, or :code:`'none'` (default: :code:`'none'`).
    :type preload: str
    :param poster: A path in the job directory or project directory for a
        poster image to be shown before a video begins playback (default: :code:`None`).
    :type poster: str
    :type sort_key: callable
    :param sort_key: Key to sort the video files, passed internally to :code:`sorted`.

    """

    _supported_contexts = {"JobContext", "ProjectContext"}

    def __init__(
        self,
        name="Video Viewer",
        context="JobContext",
        template="cards/video_viewer.html",
        video_globs=("*.mp4", "*.m4v"),
        preload="none",  # auto|metadata|none
        poster=None,
        sort_key=None,
        **kwargs,
    ):

        super().__init__(
            name=name,
            context=context,
            template=template,
            **kwargs,
        )
        self.video_globs = video_globs
        self.preload = preload
        self.poster = poster
        self.sort_key = sort_key

    def get_cards(self, job_or_project):
        if self.context == "JobContext":
            jobid = job_or_project._id
        elif self.context == "ProjectContext":
            jobid = None

        def make_card(filename):
            if not job_or_project.isfile(filename):
                raise FileNotFoundError(
                    "The filename {} could not be found "
                    "for {}.".format(
                        filename, "the project" if jobid is None else f"job {jobid}"
                    )
                )
            return {
                "name": self.name + ": " + filename,
                "content": render_template(
                    self.template,
                    jobid=jobid,
                    poster=self.poster
                    if self.poster and job_or_project.isfile(self.poster)
                    else None,
                    preload=self.preload,
                    filename=filename,
                ),
            }

        video_globs = [
            glob.iglob(job_or_project.fn(video_glob)) for video_glob in self.video_globs
        ]
        video_files = itertools.chain(*video_globs)
        video_files = sorted(video_files, key=self.sort_key)
        for filepath in video_files:
            yield make_card(os.path.relpath(filepath, job_or_project.fn("")))
