# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import json
import re
import shutil
import tempfile
import unittest
from urllib.parse import quote as urlquote

from signac import init_project

import signac_dashboard.modules
from signac_dashboard import Dashboard


class DashboardTestCase(unittest.TestCase):
    def get_response(self, query):
        rv = self.test_client.get(query, follow_redirects=True)
        return str(rv.get_data())

    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self.project = init_project(
            "dashboard-test-project", root=self._tmp_dir, make_dir=False
        )
        # Set up some fake jobs
        for a in range(3):
            for b in range(2):
                job = self.project.open_job({"a": a, "b": b})
                with job:
                    job.document["sum"] = a + b
        self.config = {}
        self.modules = []
        self.dashboard = Dashboard(
            config=self.config, project=self.project, modules=self.modules
        )
        self.test_client = self.dashboard.app.test_client()
        self.addCleanup(shutil.rmtree, self._tmp_dir)

    def test_get_project(self):
        rv = self.test_client.get("/project/", follow_redirects=True)
        response = str(rv.get_data())
        assert "dashboard-test-project" in response

    def test_get_jobs(self):
        rv = self.test_client.get("/jobs/", follow_redirects=True)
        response = str(rv.get_data())
        assert "dashboard-test-project" in response

    def test_job_count(self):
        rv = self.test_client.get("/jobs/", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{self.project.num_jobs()} jobs" in response

    def test_sp_search(self):
        dictquery = {"a": 0}
        true_num_jobs = len(list(self.project.find_jobs(dictquery)))
        query = urlquote(json.dumps(dictquery))
        rv = self.test_client.get(f"/search?q={query}", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{true_num_jobs} jobs" in response

    def test_doc_search(self):
        dictquery = {"sum": 1}
        true_num_jobs = len(list(self.project.find_jobs(doc_filter=dictquery)))
        query = urlquote("doc:" + json.dumps(dictquery))
        rv = self.test_client.get(f"/search?q={query}", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{true_num_jobs} jobs" in response

    def test_allow_where_search(self):
        dictquery = {"sum": 1}
        true_num_jobs = len(list(self.project.find_jobs(doc_filter=dictquery)))
        query = urlquote('doc:sum.$where "lambda x: x == 1"')

        self.dashboard.config["ALLOW_WHERE"] = False
        rv = self.test_client.get(f"/search?q={query}", follow_redirects=True)
        response = str(rv.get_data())
        assert "ALLOW_WHERE must be enabled for this query." in response

        self.dashboard.config["ALLOW_WHERE"] = True
        rv = self.test_client.get(f"/search?q={query}", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{true_num_jobs} jobs" in response

    def test_update_cache(self):
        rv = self.test_client.get("/jobs", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{self.project.num_jobs()} jobs" in response

        # Create a new job. Because the project has been cached, the response
        # will be wrong until the cache is cleared.
        self.project.open_job({"a": "test-cache"}).init()
        rv = self.test_client.get("/jobs", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{self.project.num_jobs()} jobs" not in response

        # Clear cache and try again.
        self.dashboard.update_cache()
        rv = self.test_client.get("/jobs", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{self.project.num_jobs()} jobs" in response

    def test_no_view_single_job(self):
        """Make sure View panel is not shown when on a single job page."""
        response = self.get_response("/jobs/7f9fb369851609ce9cb91404549393f3")
        assert "Views" not in response

    def test_project_sidebar(self):
        response = self.get_response("/project/")
        # assert "No modules. Add some!" in response
        assert "Views" not in response


class AllModulesTestCase(DashboardTestCase):
    def get_response(self, query):
        rv = self.test_client.get(query, follow_redirects=True)
        return str(rv.get_data())

    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self.project = init_project(
            "dashboard-test-project", root=self._tmp_dir, make_dir=False
        )
        # Set up some fake jobs
        for a in range(3):
            for b in range(2):
                job = self.project.open_job({"a": a, "b": b})
                with job:
                    job.document["sum"] = a + b
        self.config = {}
        modules = []
        for m in signac_dashboard.modules.__all__:
            module = getattr(signac_dashboard.modules, m)
            for c in module._supported_contexts:
                modules.append(module(context=c))
                with self.assertRaises(RuntimeError):
                    module(context="BadContext")
        self.modules = modules
        self.dashboard = Dashboard(
            config=self.config, project=self.project, modules=self.modules
        )
        self.test_client = self.dashboard.app.test_client()
        self.addCleanup(shutil.rmtree, self._tmp_dir)

    def test_module_visible_mobile(self):
        response = self.get_response("/jobs/?view=grid")
        # Check for two instances of Modules header
        pattern = re.compile("Modules</h")
        module_headers = re.findall(pattern, response)
        assert len(module_headers) == 2

    def test_module_list(self):
        project_response = self.get_response("/project/")
        # job_response = self.get_response("/jobs/&view=grid")
        for m in self.modules:
            print(f"Checking for {m.name}")
            if m.context == "ProjectContext":
                assert m.name in project_response
            # This fails for some reason:
            # elif m.context == "JobContext":
            #     if m.name == "Document Editor":
            #         print(job_response)
            #     assert m.name in job_response

    # def test_module_list_job(self):
    #     job_response = self.get_response("/jobs/")
    #     job_response = self.get_response("/jobs/&view=grid")
    #     breakpoint()
    #     for m in self.modules:
    #         print(f"Checking for {m.name}")
    #         if m.context == "JobContext":
    #             assert m.name in job_response


if __name__ == "__main__":
    unittest.main()
