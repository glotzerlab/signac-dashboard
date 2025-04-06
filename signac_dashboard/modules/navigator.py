from flask import render_template, url_for
from signac._utility import _to_hashable
from signac.job import calc_id

import functools

from signac_dashboard.module import Module
from signac_dashboard.util import abbr_value
from line_profiler import profile

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
        self.ignore=ignore


    def prepare_shadow_project(self, project):
        """Detect neighbors and build cache for shadow project which comes from ignored keys.

        Ignoring a key creates a subset of jobs, now identified with different job ids.
        Call it shadow job id because we're making a projection of the project.

        We can map from the shadow job id to the actual job id in the use cases identified.
        Raise ValueError if this mapping is ill defined.

        We can detect the neighbor list on the shadow project then map it back
        to the real project.
        
        TODO: Belongs in signac core eventually.

        Returns shadow_map, shadow_cache

        shadow_map is a map from shadow job id to project job id.
        
        shadow_cache is an in-memory state point cache for the shadow project
        mapping job id --> shadow state point


        Use cases:

        1) Seed that is different for every job.

        2) State point key that changes in sync with another key.

        Case 1:

        {"a": 1, "b": 2, "seed": 0} -> jobid1
        {"a": 1, "b": 3, "seed": 1} -> jobid2
        {"a": 1, "b": 2} -> shadowid1
        {"a": 1, "b": 3} -> shadowid2

        shadowid1 <---> jobid1
        shadowid2 <---> jobid2

        Breaking case 1 with repeated shadow jobs
        {"a": 1, "b": 2, "seed": 0} -> jobid1
        {"a": 1, "b": 3, "seed": 1} -> jobid2
        {"a": 1, "b": 3, "seed": 2} -> jobid3

        {"a": 1, "b": 2} -> shadowid1
        {"a": 1, "b": 3} -> shadowid2
        {"a": 1, "b": 3} -> shadowid2 *conflict* No longer bijection. Maybe we can just keep track of these? Should be few cases.
        Now we have shadowid2 .---> jobid2
                              \\--> jobid3

        Case 2:

        {"a1": 10, "a2": 20} -> jobid1
        {"a1": 2, "a2": 4} -> jobid2

        {"a1": 10} -> shadowid1
        {"a1": 2} -> shadowid2

        Can still make the mapping between ids.

        Breaking case 2:
        {"a1": 10, "a2": 20} -> jobid1
        {"a1": 2, "a2": 4} -> jobid2
        {"a1": 2, "a2": 5} -> jobid3

        {"a1": 10} -> shadowid1
        {"a1": 2} -> shadowid2
        {"a1": 2} -> shadowid2 --
        Now we have shadowid2 .---> jobid2
                              \\--> jobid3
        """
        
        shadow_cache = {} # like a state point cache
        job_to_shadow = {} # goes from job id to shadow. Call it the projection?
        for job in project:
            shadow_sp = dict(job.cached_statepoint)
            shadow_sp.pop(self.ignore, None)
            shadow_id = calc_id(shadow_sp)
            shadow_cache[shadow_id] = shadow_sp
            job_to_shadow[job.id] = shadow_id

        if len(set(job_to_shadow.values())) != len(job_to_shadow):
            # map that has duplicates
            duplicate_map = {}
            for k,v in job_to_shadow.items():
                try:
                    duplicate_map[v].append(k)
                except KeyError:
                    duplicate_map[v] = [k]
            # one of the breaking cases
            # figure out who breaks
            counts = Counter(job_to_shadow.values())
            bads = []
            for k,v in counts.items():
                if v>1:
                    bads.append(k)
            err_str = "\n".join(f"Job ids: {', '.join(duplicate_map[b])}." for b in bads)
            raise ValueError(f"Ignoring key '{self.ignore}' makes it impossible to distinguish some jobs:\n{err_str}")
        shadow_map = {v: k for k, v in job_to_shadow.items()}
        return shadow_map, shadow_cache


    def make_neighbor_list(self, my_map, my_cache, _sorted_schema):
        nearby_jobs = {}
        for _id, _sp in my_cache.items():
            nearby_entry = {}
            for key, schema_values in _sorted_schema.items(): # from project
                # allow comparison with output of schema, which is hashable
                value = _to_hashable(_sp.get(key, _DictPlaceholder))
                if value is _DictPlaceholder:
                    # Possible if schema is heterogeneous
                    continue

                value_index = schema_values.index(value)
                # need to pass _sp by copy
                search_fun = functools.partial(self._search_cache_for_val, dict(_sp), my_cache, key)
                previous_job = self._search_out(-1, schema_values, value_index, 0, search_fun)
                next_job = self._search_out(1, schema_values, value_index, len(schema_values) - 1, search_fun)

                this_d = {}
                if next_job[0] is not None:
                    this_d.update({next_job[1]: my_map[next_job[0]]})
                if previous_job[0] is not None:
                    this_d.update({previous_job[1]: my_map[previous_job[0]]})
                nearby_entry.update({key: this_d})
            nearby_jobs[my_map[_id]] = nearby_entry
        return nearby_jobs
    
    def _search_out(self, direction_multiplier, values, current_index, boundary, search_fun):
        """Search values towards boundary from current_index using search_fun.
        
        :param direction_multiplier: 1 means search in the positive direction from the index
        :param values: iterator of values to index into
        :param current_index: index in values to start searching from.
         The value at this index is not accessed directly.
        :param search_fun: function taking 1 argument returning jobid if there is a match
        :param boundary: the index at which to stop
        :param search_fun: function that decides if value exists in project

        """

        query_index = current_index + direction_multiplier
        # search either query_index >= low_boundary or query_index <= high_boundary
        while direction_multiplier * query_index <= boundary * direction_multiplier: 
            val = values[query_index]
            jobid = search_fun(val)
            if jobid is None:
                query_index += direction_multiplier
            else:
                break
        else:
            jobid = None
            val = None
        return jobid, val

    def _search_cache_for_val(self, sp_dict, cache, key, other_val):
        sp_dict.update({key: other_val})
        other_job_id = calc_id(sp_dict)
        if other_job_id in cache:
            return other_job_id
        else:
            return None

    def get_cards(self, job):
        project = self._dashboard_project

        # use the cache
        neighbors = self._neighbor_list[job.id]
        nearby_jobs = {}
        for key, neighbor_vals in neighbors.items():
            my_value = job.cached_statepoint[key]
            next_link = None
            previous_link = None
            next_label = "max"
            previous_label = "min"
            for neighbor_value, neighbor_job_id in neighbor_vals.items():
                if neighbor_value > my_value:
                    next_link = url_for("show_job", jobid=neighbor_job_id)
                    next_label = abbr_value(neighbor_value, self.max_chars)
                else:
                    previous_link = url_for("show_job", jobid=neighbor_job_id)
                    previous_label = abbr_value(neighbor_value, self.max_chars)
            nearby_jobs[key] = (abbr_value(my_value, self.max_chars), ((previous_link, previous_label), (next_link, next_label)))
        return [
            {
                "name": self.name,
                "content": render_template(self.template, job_nav=nearby_jobs.items()),
            }
        ]

    def register(self, dashboard):
        """Sorts and caches non-constant schema schema_values."""
        self._dashboard_project = dashboard.project

        # makes schema run faster
        self._dashboard_project.update_cache()

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
            try:
                sorted_schema[key] = sorted(this_key_vals)
            except TypeError:
                # cannot sort between different types, so leave in order
                sorted_schema[key] = list(this_key_vals)
        sorted_schema.pop(self.ignore, None)
        self._sorted_schema = dict(sorted(sorted_schema.items(), key=lambda t: t[0]))

        print("Building neighbor list...", end="", flush=True)
        if self.ignore is not None:
            # make a shadow project
            self._map, self._cache = self.prepare_shadow_project(self._dashboard_project)

            # TODO write shadow_cache to disk?
        else:
            # use built-in project cache, but still make neighbor list
            self._cache = self._dashboard_project._read_cache()
            # the identity map
            self._map = {k: k for k in self._cache}
        self._neighbor_list = self.make_neighbor_list(self._map, self._cache, self._sorted_schema)
        print("done.")
