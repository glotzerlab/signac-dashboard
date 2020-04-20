#!/usr/bin/env python3
# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard import Dashboard
from signac_dashboard.modules import StatepointList, Plotter

import numpy as np
import matplotlib.pyplot as plt


def create_figure(job):
    with job:
        fig, ax = plt.subplots()
        x = np.arange(10)
        y = np.random.random(10)
        ax.plot(x, y)
        return fig


if __name__ == '__main__':
    modules = []
    modules.append(StatepointList())
    with Plotter(create_figure) as p:
        modules.append(p)
    Dashboard(modules=modules).main()
