# Copyright (c) 2022 The Regents of the University of Michigan
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


class DashboardBaseTest(unittest.TestCase):
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


class DashboardTestCase(DashboardBaseTest):
    def test_get_project(self):
        response = self.get_response("/project/")
        self.assertTrue("dashboard-test-project" in response)

    def test_get_jobs(self):
        response = self.get_response("/jobs/")
        self.assertTrue("dashboard-test-project" in response)

    def test_job_count(self):
        response = self.get_response("/jobs/")
        self.assertTrue(f"{self.project.num_jobs()} jobs" in response)

    def test_sp_search(self):
        dictquery = {"a": 0}
        true_num_jobs = len(list(self.project.find_jobs(dictquery)))
        query = urlquote(json.dumps(dictquery))
        response = self.get_response(f"/search?q={query}")
        self.assertTrue(f"{true_num_jobs} jobs" in response)

    def test_doc_search(self):
        dictquery = {"sum": 1}
        true_num_jobs = len(list(self.project.find_jobs(doc_filter=dictquery)))
        query = urlquote("doc:" + json.dumps(dictquery))
        response = self.get_response(f"/search?q={query}")
        self.assertTrue(f"{true_num_jobs} jobs" in response)

    def test_allow_where_search(self):
        dictquery = {"sum": 1}
        true_num_jobs = len(list(self.project.find_jobs(doc_filter=dictquery)))
        query = urlquote('doc:sum.$where "lambda x: x == 1"')

        self.dashboard.config["ALLOW_WHERE"] = False
        response = self.get_response(f"/search?q={query}")
        self.assertTrue("ALLOW_WHERE must be enabled for this query." in response)

        self.dashboard.config["ALLOW_WHERE"] = True
        response = self.get_response(f"/search?q={query}")
        self.assertTrue(f"{true_num_jobs} jobs" in response)

    def test_update_cache(self):
        response = self.get_response("/jobs")
        self.assertTrue(f"{self.project.num_jobs()} jobs" in response)

        # Create a new job. Because the project has been cached, the response
        # will be wrong until the cache is cleared.
        self.project.open_job({"a": "test-cache"}).init()
        response = self.get_response("/jobs")
        self.assertTrue(f"{self.project.num_jobs()} jobs" not in response)

        # Clear cache and try again.
        self.dashboard.update_cache()
        response = self.get_response("/jobs")
        self.assertTrue(f"{self.project.num_jobs()} jobs" in response)

    def test_no_view_single_job(self):
        """Make sure View panel is not shown when on a single job page."""
        response = self.get_response("/jobs/7f9fb369851609ce9cb91404549393f3")
        self.assertTrue("Views" not in response)


class NoModulesTestCase(DashboardTestCase):
    """Test the inherited tests and cases without any modules."""

    def test_job_sidebar(self):
        response = self.get_response("/jobs/?view=grid")
        self.assertTrue("No modules." in response)

    def test_project_sidebar(self):
        response = self.get_response("/project/")
        self.assertTrue("No modules." in response)
        self.assertTrue("Views" not in response)


class AllModulesTestCase(DashboardTestCase):
    """Add all modules and contexts and test again."""

    # todo, keep just the module initialization and move the duplicate code away
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
        self.assertTrue(len(module_headers) == 2)

    def test_module_selector(self):
        project_response = self.get_response("/project/")
        job_response = self.get_response("/jobs/?view=grid")
        for m in self.modules:
            with self.subTest(module=f"{m.name} in {m.context}."):
                if m.context == "ProjectContext":
                    self.assertTrue(m.name in project_response)
                elif m.context == "JobContext":
                    self.assertTrue(m.name in job_response)

    def test_enabled_module_indices_project_session(self):
        """Ensure that the message is not displayed when modules are actually enabled."""
        project_response = self.get_response("/project/")
        self.assertTrue("No modules for the ProjectContext are enabled." not in project_response)

    def test_enabled_module_indices_job_session(self):
        """Ensure that the message is not displayed when modules are actually enabled."""
        job_response = self.get_response("/jobs/?view=grid")
        self.assertTrue("No modules for the JobContext are enabled." not in job_response)


if __name__ == "__main__":
    unittest.main()
