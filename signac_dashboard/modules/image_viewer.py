# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import glob
import itertools
import os

from flask import render_template

from signac_dashboard.module import Module


class ImageViewer(Module):
    """Displays images that match a glob.

    The ImageViewer module can display images in any format that works with a standard
    ``<img>`` tag. The module defaults to showing all images of PNG, JPG, GIF, and SVG
    types in the job or project directory. A filename or glob can be
    defined to select specific filenames. Each matching file yields a card.

    Multiple ImageViewer modules can be defined with different filenames or
    globs to enable/disable cards for each image or image group.

    :Example:

    .. code-block:: python

        from signac_dashboard.modules import ImageViewer
        img_mod = ImageViewer()  # Show all PNG/JPG/GIF/SVG images
        img_mod = ImageViewer(name='Bond Order Diagram', img_globs=['bod.png'])
        img_mod = ImageViewer(context="ProjectContext",
                              img_globs=['/gallery/*.png'])  # search subdirectory of project path

    :param context: Supports :code:`'JobContext'` and :code:`'ProjectContext'`.
    :type context: str
    :param img_globs: A list of glob expressions or exact filenames,
        relative to the job or project directory, to be displayed
        (default: :code:`['*.png', '*.jpg', '*.gif', '*.svg']`).
    :type img_globs: list
    :type sort_key: callable
    :param sort_key: Key to sort the image files, passed internally to :code:`sorted`.

    """

    _supported_contexts = {"JobContext", "ProjectContext"}

    def __init__(
        self,
        name="Image Viewer",
        context="JobContext",
        template="cards/image_viewer.html",
        img_globs=("*.png", "*.jpg", "*.gif", "*.svg"),
        sort_key=None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            context=context,
            template=template,
            **kwargs,
        )
        self.img_globs = img_globs
        self.sort_key = sort_key

    def get_cards(self, job_or_project):
        if self.context == "JobContext":
            jobid = job_or_project._id
            modal_label = job_or_project._id
        elif self.context == "ProjectContext":
            jobid = None
            modal_label = "project"

        def make_card(filename):
            return {
                "name": self.name + ": " + filename,
                "content": render_template(
                    self.template,
                    modal_label=modal_label,
                    jobid=jobid,
                    filename=filename,
                ),
            }

        image_globs = [
            glob.iglob(job_or_project.fn(image_glob)) for image_glob in self.img_globs
        ]
        image_files = itertools.chain(*image_globs)
        image_files = sorted(image_files, key=self.sort_key)
        for filepath in image_files:
            yield make_card(os.path.relpath(filepath, job_or_project.fn("")))
