#!/usr/bin/env python3
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import numpy as np
import signac

project = signac.init_project("plots")


def plot_coherence(job):
    # Data generation adapted from:
    # https://matplotlib.org/gallery/lines_bars_and_markers/cohere.html

    print(f"Generating signals for coherence time {job.sp.coherence_time}, job {job}")
    # Fixing random state for reproducibility
    np.random.seed(job.sp.seed)

    dt = 0.01
    t = np.arange(0, 30, dt)
    nse1 = np.random.randn(len(t))  # white noise 1
    nse2 = np.random.randn(len(t))  # white noise 2

    # Two signals with a coherent part and a random part
    s1 = np.sin(2 * np.pi * job.sp.coherence_time * t) + nse1
    s2 = np.sin(2 * np.pi * job.sp.coherence_time * t) + nse2

    # Save the signal data
    job.doc["t"] = t.tolist()
    job.doc["s1"] = s1.tolist()
    job.doc["s2"] = s2.tolist()

    # Save correlation coefficient
    job.doc["correlation"] = np.corrcoef(s1, s2)[0, 1]


for i in range(30):
    job = project.open_job({"coherence_time": i, "seed": 42})
    job.init()
    plot_coherence(job)
