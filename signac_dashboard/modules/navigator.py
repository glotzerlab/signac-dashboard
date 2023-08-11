from flask import render_template, url_for
from signac._utility import _to_hashable

from signac_dashboard.module import Module
from signac_dashboard.util import abbr_value


class _DictPlaceholder:
    pass


class Navigator(Module):
    """Displays links to jobs differing in one state point parameter.

    This module uses the project schema to determine which state points vary, then displays links to
    jobs with adjacent values of these parameters in a table. Schema detection can be slow on slow
    file systems, so this module caches the project schema. Therefore, this module may not update if
    the signac project changes while the signac-dashboard is running.

    :param context: Supports :code:`'JobContext'`
    :type context: str
    :param max_chars: Truncation length of state point values (default: 6).
    :type max_chars: int
    """

    _supported_contexts = {"JobContext"}

    def __init__(
        self,
        name="Navigator",
        context="JobContext",
        template="cards/navigator.html",
        max_chars=6,
        **kwargs,
    ):
        super().__init__(name=name, context=context, template=template, **kwargs)
        self.max_chars = max_chars

    def _link_label(self, job, project, key, other_val):
        """Return the url and label for the job with job.sp[key] == other_val."""
        similar_statepoint = job.statepoint()  # modifiable
        similar_statepoint.update({key: other_val})

        # Look only for exact matches that result from only changing one parameter
        # in case of heterogeneous schema
        other_job = project.open_job(similar_statepoint)
        if other_job in project:
            link = url_for("show_job", jobid=other_job.id)
            label = abbr_value(other_val, self.max_chars)
        else:
            link = None
            label = f"no match for {other_val}"
        return link, label

    def get_cards(self, job):
        project = self._dashboard_project

        nearby_jobs = {}
        sp_copy = job.sp()

        # for each parameter in the schema, find the next and previous job and get links to them
        for key, schema_values in self._sorted_schema.items():
            # allow comparison with output of schema, which is hashable
            value = _to_hashable(sp_copy.get(key, _DictPlaceholder))
            if value is _DictPlaceholder:
                # Possible if schema is heterogeneous
                continue
            value_index = schema_values.index(value)

            query_index = value_index - 1
            while query_index >= 0:
                prev_val = schema_values[query_index]
                link, label = self._link_label(job, project, key, prev_val)
                if link is None:
                    query_index -= 1
                else:
                    break
            else:
                link = None
                label = "min"
            previous_label = (link, label)

            query_index = value_index + 1
            while query_index <= len(schema_values) - 1:
                next_val = schema_values[query_index]
                link, label = self._link_label(job, project, key, next_val)
                if link is None:
                    query_index += 1
                else:
                    break
            else:
                link = None
                label = "max"
            next_label = (link, label)

            if previous_label[0] is not None or next_label[0] is not None:
                nearby_jobs[key] = (
                    abbr_value(value, self.max_chars),
                    (previous_label, next_label),
                )

        return [
            {
                "name": self.name,
                "content": render_template(self.template, job_nav=nearby_jobs.items()),
            }
        ]

    def register(self, dashboard):
        """Sorts and caches non-constant schema schema_values."""
        self._dashboard_project = dashboard.project

        # Tell user because this can take a long time
        print("Detecting project schema for Navigator...", end="", flush=True)
        schema = dashboard.project.detect_schema(exclude_const=True)
        print("done.")
        # turn dict of sets of lists ...into list of parameters
        sorted_schema = {}
        for key, project_values in schema.items():
            this_key_vals = set()
            for typename in project_values.keys():
                this_key_vals.update(project_values[typename])
            sorted_schema[key] = sorted(this_key_vals)

        self._sorted_schema = dict(sorted(sorted_schema.items(), key=lambda t: t[0]))
