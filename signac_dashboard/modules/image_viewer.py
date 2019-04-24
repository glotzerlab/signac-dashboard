# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
import os
import glob
import itertools


class ImageViewer(Module):
    """Displays images in the job workspace that match a glob.

    This module can display images in any format that works with a standard
    ``<img>`` tag. The module defaults to showing all images of PNG, JPG, or
    GIF types. A filename or glob can be defined to select specific filenames.
    Multiple ImageViewer modules can be defined with different filenames or
    globs to enable/disable cards for each image or image group. Examples:

    .. code-block:: python

        from signac_dashboard.modules import ImageViewer
        img_mod = ImageViewer()  # Shows all PNG/JPG/GIF images
        img_mod = ImageViewer(name='Bond Order Diagram', img_globs=['bod.png'])

    :param img_globs: A list of glob expressions or exact filenames to be
        displayed, one per card (default: :code:`['*.png', '*.jpg', '*.gif']`).
    :type img_globs: list
    """
    def __init__(self,
                 name='Image Viewer',
                 context='JobContext',
                 template='cards/image_viewer.html',
                 img_globs=['*.png', '*.jpg', '*.gif'],
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)
        self.img_globs = img_globs

    def get_cards(self, job):
        def make_card(filename):
            return {'name': self.name + ': ' + filename,
                    'content': render_template(
                        self.template,
                        jobid=job._id,
                        filename=filename)}

        image_globs = [glob.iglob(job.workspace() + os.sep + image_glob)
                       for image_glob in self.img_globs]
        image_files = itertools.chain(*image_globs)
        for filepath in image_files:
            yield make_card(os.path.relpath(filepath, job.ws))
