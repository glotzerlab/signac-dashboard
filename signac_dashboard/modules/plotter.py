# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template

import io

from multiprocessing import Process, Queue, cpu_count, Manager

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt


class Plotter(Module):
    """Renders a matplotlib figure

    The content of the figure is rendered on the fly inside a use-provided function. To work around
    the lack of thread safety in matplotlib, these functions are evavluated in subprocesses rather
    than webserver threads.

    :param plotfn: A function that returns a matplotlib `Figure` object
    :type plotfn: callable
    :param n_processes: Number of sever proceses used for creating figures (default: number of CPU cores)
    :type n_processes: int
    """
    def __init__(self,
                 plotfn,
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
        self.lock = manager.Lock()
        if n_processes is None:
            n_processes = cpu_count()
        self.n_processes = n_processes
        self.plotfn = plotfn

    def get_cards(self, job):
        return [{'name': self.name,
                'content': render_template(
                    self.template,
                    jobid=job._id
                    )}]

    def worker(self, in_queue, result, lock, project, plotfn):
        for jobid in iter(in_queue.get, 'STOP'):
            res = None
            try:
                job = project.open_job(id=jobid)
                fig = plotfn(job)
                output = io.BytesIO()
                FigureCanvas(fig).print_png(output)
                plt.close(fig)
                res = output.getvalue()
            except Exception as e:
                print(repr(e))

            # store result in shared variable
            with lock:
                result[jobid] = res

    def register(self, dashboard):
        @dashboard.app.route('/module/plotter/<jobid>')
        def plot(jobid):
            self.in_queue.put(jobid)

            while True:
                with self.lock:
                    if jobid in self.result:
                        res = self.result[jobid]
                        del self.result[jobid]
                        break

            return dashboard.app.response_class(res, mimetype='image/png')

        # Start worker processes
        for i in range(self.n_processes):
            Process(target=self.worker,
                    args=(self.in_queue, self.result, self.lock,
                          dashboard.project, self.plotfn)).start()
