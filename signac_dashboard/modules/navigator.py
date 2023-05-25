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

        nearby_jobs = dict()

        def link_label(job, key):
            if job is not None:
                if job.sp.get(key, None) is not None:
                    link = url_for('show_job', jobid = job.id)
                    label = job.sp[key]
            else:
                label = ""
                link = ""
            return link, label

        nearby_jobs = dict()
        # for each parameter in the schema, find the next and previous job and get links to them
        for key, values in self._sorted_schema.items():
            print("working on key", key)

            my_val = job.sp.get(key, None)
            if my_val is None:
                continue

            # find position of my_val in list
            my_index = values.index(my_val)
            print(f"my value {my_val} is at index {my_index} of {values}")
            # search for the job that only has that one different
            link = None
            label = None
            if my_index >= 1:
                prev_val = values[my_index - 1]

                # function here of prev/next_val
                nearest = job.sp()
                nearest.update({key: prev_val})
                prev_job = project.find_jobs(nearest)
                l = len(prev_job)
                print(f"found {l} jobs with previous value {prev_val}")
                if l == 0:
                    pass
                elif l == 1:
                    prev_job = next(iter(prev_job))  
                    link, label = link_label(prev_job, key)
                else:
                    label = f"{l} options"
            else:
                label = "beginning"
            prevlab = (link, label)
            print("prev label", prevlab)

            link = None
            label = None
            if my_index <= len(values)-2:
                next_val = values[my_index + 1]
                nearest = job.sp()
                nearest.update({key: next_val})
                next_job = project.find_jobs(nearest)
                l = len(next_job)
                print(f"found {l} jobs with next value {next_val}")
                if l == 0:
                    pass
                elif l == 1:
                    next_job = next(iter(next_job))
                    link, label = link_label(next_job, key)
                else:
                    label = f"{l} options"
            else:
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
