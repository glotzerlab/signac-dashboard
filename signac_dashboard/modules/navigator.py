from collections import OrderedDict

from flask import render_template, url_for

from signac_dashboard.module import Module


class _DictPlaceholder:
    pass


class Navigator(Module):
    """Displays links to jobs differing in one state point parameter.

    This module may not update if the signac project changes because the module
    caches the project schema when the signac-dashboard launches.

    :param context: Supports :code:`'JobContext'`
    :type context: str
    """

    _supported_contexts = {"JobContext"}

    def __init__(
        self,
        name="Navigator",
        context="JobContext",
        template="cards/navigator.html",
        **kwargs,
    ):
        super().__init__(name=name, context=context, template=template, **kwargs)

    def _link_label(self, job, project, key, other_val):
        """Return the url and label for the job with job.sp[key] == other_val."""
        similar_statepoint = job.statepoint()  # modifiable
        similar_statepoint.update({key: other_val})

        # Look only for exact matches of only changing one parameter
        # in case of heterogeneous schema
        other_job = project.open_job(similar_statepoint)
        if other_job in project:
            link = url_for("show_job", jobid=other_job.id)
            label = other_val
        else:
            link = None
            label = f"no match for {other_val}"
        return link, label

    def get_cards(self, job):
        project = self._dashboard.project

        nearby_jobs = {}
        # for each parameter in the schema, find the next and previous job and get links to them
        for key, schema_values in self._sorted_schema.items():
            value = job.sp.get(key, _DictPlaceholder)
            if value is _DictPlaceholder:
                # Possible if schema is heterogeneous
                continue

            value_index = schema_values.index(value)

            query_index = value_index - 1
            while query_index >= 0:
                prev_val = schema_values[query_index]
                link, label = self._link_label(job, project, key, prev_val)
                if link is None:
                    query_index = query_index - 1
                else:
                    break
            else:
                link = None
                label = "beginning"
            previous_label = (link, label)

            query_index = value_index + 1
            while query_index <= len(schema_values) - 1:
                next_val = schema_values[query_index]
                link, label = self._link_label(job, project, key, next_val)
                if link is None:
                    query_index = query_index + 1
                else:
                    break
            else:
                link = None
                label = "end"
            next_label = (link, label)

            if previous_label[0] is not None or next_label[0] is not None:
                nearby_jobs[key] = (value, (previous_label, next_label))

        return [
            {
                "name": self.name,
                "content": render_template(self.template, job_nav=nearby_jobs.items()),
            }
        ]

    def register(self, dashboard):
        """Sorts and caches non-constant schema schema_values."""
        self._dashboard = dashboard

        # Tell user because this can take a long time
        print("Detecting project schema for Navigator...", end="")
        schema = dashboard.project.detect_schema(exclude_const=True)
        print("done.")
        # turn dict of sets of lists ...into list of parameters
        sorted_schema = {}
        for key, project_values in schema.items():
            this_key_vals = set()
            for typename in project_values.keys():
                this_key_vals.update(project_values[typename])
            sorted_schema[key] = sorted(this_key_vals)

        self._sorted_schema = OrderedDict(
            sorted(sorted_schema.items(), key=lambda t: t[0])
        )
