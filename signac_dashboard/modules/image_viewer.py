from signac_dashboard.module import Module
from flask import render_template, url_for
import os
import glob
import itertools

class ImageViewer(Module):

    def __init__(self, name='Image Viewer', img_globs=['*.png', '*.jpg', '*.gif']):
        super().__init__(name=name,
                         context='JobContext',
                         template='panels/image_viewer.html')
        self.img_globs = img_globs

    def get_panels(self, job):
        def make_panel(filename):
            return {'name': self.name + ': ' + filename,
                    'content': render_template(self.template,
                                               imgsrc = url_for('get_file', jobid=str(job), filename=filename),
                                               filename=filename)}

        image_globs = [glob.iglob(job.workspace() + os.sep + image_glob) for image_glob in self.img_globs]
        image_files = itertools.chain(*image_globs)
        for filepath in image_files:
            yield make_panel(os.path.basename(filepath))
