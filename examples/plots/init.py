#!/usr/bin/env python3
# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import signac
import numpy as np
import matplotlib.pyplot as plt

try:
    project = signac.get_project()
except LookupError:
    project = signac.init_project('plots')


def plot_coherence(job):
    # Plot script adapted from:
    # https://matplotlib.org/gallery/lines_bars_and_markers/cohere.html

    print('Making plots for coherence time {}, job {}'.format(
        job.sp.coherence_time, job))
    # Fixing random state for reproducibility
    np.random.seed(job.sp.seed)

    dt = 0.01
    t = np.arange(0, 30, dt)
    nse1 = np.random.randn(len(t))                 # white noise 1
    nse2 = np.random.randn(len(t))                 # white noise 2

    # Two signals with a coherent part at 10Hz and a random part
    s1 = np.sin(2 * np.pi * job.sp.coherence_time * t) + nse1
    s2 = np.sin(2 * np.pi * job.sp.coherence_time * t) + nse2

    fig, axs = plt.subplots(2, 1)
    plt.title('Coherence time = {}'.format(job.sp.coherence_time))

    axs[0].plot(t, s1, t, s2)
    axs[0].set_xlim(0, 2)
    axs[0].set_xlabel('time')
    axs[0].set_ylabel('s1 and s2')
    axs[0].grid(True)

    cxy, f = axs[1].cohere(s1, s2, 256, 1. / dt)
    axs[1].set_ylim(0, 1)
    axs[1].set_ylabel('coherence')

    fig.tight_layout()
    plt.savefig(job.fn('coherence.png'))
    plt.close()


for i in range(30):
    job = project.open_job({'coherence_time': i, 'seed': 42})
    job.init()
    plot_coherence(job)
