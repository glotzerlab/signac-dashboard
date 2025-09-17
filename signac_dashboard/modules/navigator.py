from flask import render_template, url_for
from signac._utility import _to_hashable
from signac.job import calc_id

from collections import Counter
import functools

from signac_dashboard.module import Module
from signac_dashboard.util import abbr_value

class _DictPlaceholder:
    pass


class Navigator(Module):
    """Displays links to jobs differing in one state point parameter.

    This module uses the project schema to determine which state points vary, then displays links to
    jobs with adjacent values of these parameters in a table.

    This module caches the schema and the job neighbor list. Therefore, this module may not update if
    the signac project changes while the signac-dashboard is running.

    :param context: Supports :code:`'JobContext'`
    :type context: str
    :param max_chars: Truncation length of state point values (default: 6).
    :type max_chars: int
    :param ignore: key to ignore when detecting neighbors
    """

    _supported_contexts = {"JobContext"}

    def __init__(
        self,
        name="Navigator",
        context="JobContext",
        template="cards/navigator.html",
        max_chars=6,
        ignore=None,
        **kwargs,
    ):
        super().__init__(name=name, context=context, template=template, **kwargs)
        self.max_chars = max_chars
        # TODO check how this handles iterables
        if isinstance(ignore, list):
            self.ignore = ignore
        else:
            self.ignore = [ignore]

    def get_cards(self, job):
        neighbors = self._neighbor_list[job.id]
        nearby_jobs = {}

        for key, neighbor_vals in neighbors.items():
            if "." in key:
                ks = iter(key.split("."))
                my_value = job.cached_statepoint[next(ks)]
                for k in ks:
                    my_value = my_value[k]
            else:
                my_value = job.cached_statepoint[key]
            previous_link = None
            next_link = None
            previous_label = "min"
            next_label = "max"

            if len(neighbor_vals) == 2:
                # prev and next in dict order
                (prev_val, prev_jobid), (next_val, next_jobid) = neighbor_vals.items()
                previous_label = abbr_value(prev_val, self.max_chars)
                previous_link = url_for("show_job", jobid = prev_jobid)
                next_label = abbr_value(next_val, self.max_chars)
                next_link = url_for("show_job", jobid = next_jobid)
            elif len(neighbor_vals) == 1:
                val, jobid = next(iter(neighbor_vals.items()))
                try:
                    is_previous = val < my_value
                except TypeError:
                    is_previous = type(val).__name__ < type(my_value).__name__
                if is_previous:
                    previous_label = abbr_value(val, self.max_chars)
                    previous_link = url_for("show_job", jobid = jobid)
                else:
                    next_label = abbr_value(val, self.max_chars)
                    next_link = url_for("show_job", jobid = jobid)
            nearby_jobs[key] = (abbr_value(my_value, self.max_chars), ((previous_link, previous_label), (next_link, next_label)))
        return [
            {
                "name": self.name,
                "content": render_template(self.template, job_nav=nearby_jobs.items()),
            }
        ]

    def register(self, dashboard):
        self._dashboard_project = dashboard.project

        # makes schema run faster
        self._dashboard_project.update_cache()
        self._neighbor_list = self._dashboard_project.get_neighbors(ignore = self.ignore)

