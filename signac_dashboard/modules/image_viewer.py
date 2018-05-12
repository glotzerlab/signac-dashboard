# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
import os
import glob
import itertools


class ImageViewer(Module):

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
            yield make_card(os.path.basename(filepath))
