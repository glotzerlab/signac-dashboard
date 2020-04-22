# Copyright (c) 2020 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard.module import Module
from flask import render_template
from multiprocessing import Process, Manager, cpu_count, Queue

import io
import os


class Plotter(Module):
    """Renders a matplotlib figure.

    The content of the figure is rendered on the fly inside a user-provided
    function. Because matplotlib is not thread-safe, these functions are
    evaluated in subprocesses rather than webserver threads.

    `Plotter` manages processes and therefore needs to be used as a context
    manager.

    Examples:

    .. code-block:: python

        def create_figure(job):
            fig, ax = plt.subplots()
            ax.plot([1,2],[3,4])
            return fig

        with Plotter(create_figure) as p:
            Dashboard(modules=[p]).main()


    :param plotfn: A function that returns a matplotlib `Figure` object
    :type plotfn: callable
    :param n_processes: Number of server proceses used for creating figures
                        (default: number of CPU cores).
    :type n_processes: int
    """
    def __init__(self,
                 plotfn=None,
                 n_processes=None,
                 name='Plotter',
                 context='JobContext',
                 template='cards/plotter.html',
                 **kwargs):
        super().__init__(name=name,
                         context=context,
                         template=template,
                         **kwargs)

        self.processes = []
        if n_processes is None:
            n_processes = cpu_count()
        self.n_processes = n_processes
        self.plotfn = plotfn
        self.parent_pid = None
        self.in_queue = None

    def __enter__(self):
        # Start worker processes

        manager = Manager()
        self.result = manager.dict()
        self.lock = manager.Lock()
        self.in_queue = Queue()

        for i in range(self.n_processes):
            p = Process(target=self.worker,
                        args=(self.in_queue, self.result, self.lock,
                              self.plotfn))
            p.start()
            self.processes.append(p)

        self.parent_pid = os.getpid()
        return self

    def get_cards(self, job):
        return [{'name': self.name,
                 'content': render_template(
                     self.template,
                     jobid=job._id
                     )}]

    def worker(self, in_queue, result, lock, plotfn):
        from matplotlib.backends.backend_agg import FigureCanvasAgg \
            as FigureCanvas
        import matplotlib.pyplot as plt

        for (project, jobid) in iter(in_queue.get, 'STOP'):
            res = None
            try:
                job = project.open_job(id=jobid)
                if plotfn is None:
                    raise ValueError("plotfn argument not provided.\n")
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
            if self.in_queue is None:
                raise RuntimeError('Plotter module not initialized. ' +
                                   'Use Plotter as a context manager.')
            self.in_queue.put((dashboard.project, jobid))

            while True:
                with self.lock:
                    if jobid in self.result:
                        res = self.result[jobid]
                        del self.result[jobid]
                        break

            return dashboard.app.response_class(res, mimetype='image/png')

    def terminate_processes(self):
        if os.getpid() == self.parent_pid:
            # send stop signal to workers
            for p in self.processes:
                self.in_queue.put('STOP')

            # wait for processes to finish
            for p in self.processes:
                p.join()

            self.processes = []

    def __exit__(self, *args):
        self.terminate_processes()
