# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
import io

from flask import Response,render_template
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt

from multiprocessing import Process, Queue, cpu_count, Lock, Manager

class Plotter(Module):
    def __init__(self,
                 n_processes=None,
                 name='Plotter',
                 context='JobContext',
                 template='cards/plotter.html',
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)
        self.in_queue = Queue()
        manager = Manager()
        self.result = manager.dict()
        self.lock = Lock()
        if n_processes is None:
            n_processes = cpu_count()
        self.n_processes = n_processes

    def get_cards(self, job):
        return [{'name': self.name ,
                'content': render_template(
                    self.template,
                    jobid=job._id
                    )}]

    def worker(self, in_queue, result, lock, project):
        for jobid in iter(in_queue.get, 'STOP'):
            job = project.open_job(id=jobid)
            fig = self.create_figure(job)
            output = io.BytesIO()
            FigureCanvas(fig).print_png(output)
            plt.close(fig)

            # store result in shared variable
            with lock:
                result[jobid] = output.getvalue()

    def register(self, dashboard):
        @dashboard.app.route('/module/plotter/<jobid>')
        def plot(jobid):
            self.in_queue.put(jobid)

            while True:
                with self.lock:
                    if jobid in self.result:
                        res = self.result[jobid]
                        self.result[jobid] = None
                        break

            return dashboard.app.response_class(res,
                mimetype='image/png')

        # Start worker processes
        for i in range(self.n_processes):
            Process(target=self.worker,
                args=(self.in_queue, self.result, self.lock,
                      dashboard.project)).start()

    def create_figure(self,job):
        return None

