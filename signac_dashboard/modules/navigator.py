from flask import render_template, url_for

from signac_dashboard.module import Module
from signac_dashboard.util import escape_truncated_values

class Navigator(Module):
    """Displays links to related jobs."""

    _supported_contexts = {"JobContext"}

    def __init__(
        self,
        name = "Navigator",
        context = "JobContext",
        template = "cards/navigator.html",
        **kwargs
    ):
        super().__init__(
            name = name,
            context=context,
            template=template,
            **kwargs
        )


    def get_cards(self, job):
        project = self._dashboard.project

        def link_label(key, other_val):
            nearest = job.sp() # modifiable
            nearest.update({key: other_val})

            # Look only for exact matches in case of heterogeneous schema
            other_job = project.open_job(nearest)
            if other_job in project:
                link = url_for('show_job', jobid = other_job.id)
                label = other_job.sp[key]
            else:
                link = None
                label = "no match"
            return link, label

        nearby_jobs = dict()
        # for each parameter in the schema, find the next and previous job and get links to them
        for key, values in self._sorted_schema.items():
            print("working on key", key)

            my_val = job.sp.get(key, None)
            if my_val is None:
                print("Job didn't have this key")
                continue

            # find position of my_val in schema values
            my_index = values.index(my_val)
            print(f"my value {my_val} is at index {my_index} of {values}")
            # search for the job that only has that one different
            if my_index >= 1:
                prev_val = values[my_index - 1]
                link, label = link_label(key, prev_val)
            else:
                link = None
                label = "beginning"
            prevlab = (link, label)
            print("prev label", prevlab)

            if my_index <= len(values)-2:
                next_val = values[my_index + 1]
                link, label = link_label(key, next_val)
            else:
                link = None
                label = "end"
            nextlab = (link, label)
            print("next label", nextlab)

            if prevlab[0] is not None or nextlab[0] is not None:
                nearby_jobs[key] = (prevlab, nextlab)

        return [
            {
                "name": self.name,
                "content": render_template(self.template, job_nav = nearby_jobs.items()),
            }
        ]

    def register(self, dashboard):
        """Sorts and caches non-constant schema values."""
        print("Detecting schema for Navigator...")
        self._dashboard = dashboard
        schema = dashboard.project.detect_schema(exclude_const = True)
        print("...done")

        # turn dict of sets of lists ...into list of parameters
        sortedSchema = dict()
        for key, project_values in schema.items():
            thisKeyValues = set()
            for typename in project_values.keys():
                thisKeyValues.update(project_values[typename])
            thisKeyValues = sorted(list(thisKeyValues))
            sortedSchema[key] = thisKeyValues
        self._sorted_schema = sortedSchema
