#!/usr/bin/env python3
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard import Dashboard
from signac_dashboard.modules import (
    ImageViewer,
    PlotlyViewer,
    StatepointList,
    TextDisplay,
)


class PlotDashboard(Dashboard):
    def job_sorter(self, job):
        return job.sp.get("coherence_time", -1)

    def job_title(self, job):
        return f"Coherence time: {job.sp.coherence_time}"


def correlation_text(job):
    return "Correlation coefficient: {:.5f}".format(job.doc["correlation"])


# Visualization adapted from:
# https://matplotlib.org/gallery/lines_bars_and_markers/cohere.html

# It's necessary to cast to list because the list elements of the job
# document are BufferedJSONAttrList, which is not serializable


def signals_plotly_args(job):
    signals_traces = [
        {
            "x": list(job.doc["t"]),
            "y": list(job.doc["s1"]),
            "name": "s1",
        },
        {
            "x": list(job.doc["t"]),
            "y": list(job.doc["s2"]),
            "name": "s2",
        },
    ]
    signals_layout = {
        "xaxis": {
            "title": "time",
            "range": [0, 2],
        },
        "height": 200,
        "margin": dict(t=30, b=40, l=40, r=0),
    }
    return (signals_traces, signals_layout)


def coherence_plotly_args(job):
    coherence_traces = [
        {
            "x": list(job.doc["f"]),
            "y": list(job.doc["cxy"]),
        }
    ]
    coherence_layout = {
        "title": f"Coherence time = {job.sp.coherence_time}",
        "xaxis": {"title": "frequency"},
        "yaxis": {"title": "coherence", "range": [0, 1]},
        "height": 200,
        "margin": dict(t=30, b=40, l=40, r=0),
    }
    return (coherence_traces, coherence_layout)


if __name__ == "__main__":
    modules = []
    modules.append(StatepointList())
    modules.append(ImageViewer())
    modules.append(PlotlyViewer("Signals", plotly_args=signals_plotly_args))
    modules.append(PlotlyViewer("Coherence", plotly_args=coherence_plotly_args))
    modules.append(TextDisplay(name="Correlation", message=correlation_text))
    PlotDashboard(modules=modules).main()
