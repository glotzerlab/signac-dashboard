# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
import os
import glob
import itertools
import io

from flask import Response,render_template
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

class Plotter(Module):
    def __init__(self,
                 name='Plotter',
                 context='JobContext',
                 template='cards/plotter.html',
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)

    def get_cards(self, job):
        return [{'name': self.name ,
                'content': render_template(
                    self.template,
                    jobid=job._id
                    )}]

    def register_routes(self, dashboard):
        @dashboard.app.route('/module/plotter/<jobid>/')
        def plot(jobid):
            fig = self.create_figure(job=dashboard.project.open_job(id=jobid))
            output = io.BytesIO()
            FigureCanvas(fig).print_png(output)
            return Response(output.getvalue(), mimetype='image/png')

    def create_figure(self,job):
        return None

